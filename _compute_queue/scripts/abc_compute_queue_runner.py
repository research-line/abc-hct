#!/usr/bin/env python3
"""Small remote compute queue runner for abc/HCT jobs.

The runner is intentionally conservative:
- it is meant to run on Mac Studio / server / desktop, not on the laptop;
- it starts at most one queued job at a time;
- each job is declared as JSON under compute_queue/jobs;
- long Sage commands are launched detached and tracked via state JSON.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shlex
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


DATE = "2026-05-23"
QUEUE_DIR = "compute_queue"

# Slot-Koordination mit dem Memory-Watchdog (v5+):
# Der Watchdog schreibt compute_slot_status.json (pull_ok, overflow_locked).
# Der Runner registriert gestartete Jobs als PID-Dateien in RUNNER_JOBS_DIR,
# damit der Watchdog sie in count_active_compute mitzaehlt (sonst saehe er
# Runner-gestartete Jobs nicht und das Slot-Modell briche).
MEMWATCH_DIR = Path.home() / ".memwatchdog"
SLOT_STATUS_PATH = MEMWATCH_DIR / "compute_slot_status.json"
RUNNER_JOBS_DIR = MEMWATCH_DIR / "runner_jobs"


def now() -> float:
    return time.time()


def read_slot_status() -> dict[str, Any]:
    """Liest den Watchdog-Slot-Status. Leeres dict, wenn nicht vorhanden/frisch."""
    try:
        d = read_json(SLOT_STATUS_PATH)
    except Exception:
        return {}
    # Veralteter Status (>90s = 1.5x Watchdog-Poll) -> als nicht vorhanden
    # behandeln (Watchdog tot/haengt -> kein Pull, Race-Schutz).
    if now() - float(d.get("ts", 0)) > 90:
        return {}
    return d


def register_runner_job(job_id: str, pid: int) -> None:
    try:
        RUNNER_JOBS_DIR.mkdir(parents=True, exist_ok=True)
        (RUNNER_JOBS_DIR / f"{job_id}.pid").write_text(str(pid), encoding="utf-8")
    except Exception:
        pass


def cleanup_runner_jobs() -> None:
    """Entfernt PID-Dateien beendeter Runner-Jobs (analog Watchdog-cleanup)."""
    try:
        if not RUNNER_JOBS_DIR.exists():
            return
        for f in RUNNER_JOBS_DIR.glob("*.pid"):
            try:
                pid = int(f.read_text().strip())
            except Exception:
                f.unlink(missing_ok=True)
                continue
            if not pid_alive(pid):
                f.unlink(missing_ok=True)
    except Exception:
        pass


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def host_aliases() -> set[str]:
    node = platform.node()
    aliases = {node, node.lower()}
    env_alias = os.environ.get("ABC_COMPUTE_HOST_ALIAS")
    if env_alias:
        aliases.add(env_alias)
        aliases.add(env_alias.lower())
    lower = node.lower()
    if lower in {"mac-studio", "macstudvonlukas"} or "mac" in lower:
        aliases.add("mac-studio")
    if "ellmos" in lower:
        aliases.add("ellmos-services")
    if lower.startswith("asus") or lower == "asus-gei":
        aliases.add("ASUS-GEI")
        aliases.add("laptop")
    return aliases


def ps_rows() -> list[str]:
    if platform.system() == "Darwin":
        cmd = ["ps", "-axo", "pid,pcpu,rss,etime,command"]
    else:
        cmd = ["ps", "-eo", "pid,pcpu,rss,etime,cmd"]
    try:
        out = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
    except Exception:
        return []
    return [line.rstrip() for line in out.splitlines()[1:]]


def process_matches(patterns: list[str]) -> list[str]:
    rows = ps_rows()
    hits: list[str] = []
    for row in rows:
        if "compute_queue_runner.py" in row:
            continue
        for pat in patterns:
            if re.search(pat, row):
                hits.append(row)
                break
    return hits


def proc_state(pid: int) -> str | None:
    """ps-Statusbuchstabe (R/S/Z/...) oder None, wenn Prozess nicht existiert."""
    try:
        out = subprocess.check_output(
            ["ps", "-o", "state=", "-p", str(pid)], text=True, stderr=subprocess.DEVNULL
        )
    except Exception:
        return None
    s = out.strip()
    return s[:1] if s else None


def pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    # Zombies existieren in der Prozesstabelle, laufen aber nicht mehr.
    # Ohne diesen Check hielt der Runner <defunct>-Jobs fuer "running"
    # und blockierte die Queue (Vorfall 2026-06-12).
    return proc_state(pid) != "Z"


def _exit_code_from_status(status: int) -> int:
    try:
        return os.waitstatus_to_exitcode(status)
    except AttributeError:  # Python < 3.9
        if os.WIFEXITED(status):
            return os.WEXITSTATUS(status)
        return -os.WTERMSIG(status)


def mark_job_file(root: Path, job_id: str, status: str, reason: str) -> None:
    jp = root / QUEUE_DIR / "jobs" / f"{job_id}.json"
    if not jp.exists():
        return
    try:
        jd = read_json(jp)
        if str(jd.get("status", "")).lower() in {"completed", "done", "failed", "blocked", "disabled"}:
            return
        jd["status"] = status
        jd["completed_unix"] = now()
        jd["completed_reason"] = reason
        write_json(jp, jd)
    except Exception:
        pass


def finalize_job_by_pid(root: Path, pid: int, code: int) -> None:
    """Schliesst den running-Job mit dieser PID anhand des Exit-Codes ab.

    Exit 0  -> State "success" + Job-Datei "completed" (Auto-Done).
    Exit >0 -> State/Job-Datei "failed" (deterministischer Scriptfehler,
               kein Retry-Brennen).
    Signal (<0) -> State "killed", Job-Datei unangetastet (transient:
               manueller kill/OOM -> Neustart durch Runner erlaubt).
    """
    state_dir = root / QUEUE_DIR / "state"
    if not state_dir.exists():
        return
    for sp in state_dir.glob("*.state.json"):
        try:
            st = read_json(sp)
        except Exception:
            continue
        if int(st.get("pid", -1)) != pid or st.get("status") != "running":
            continue
        job_id = st.get("job_id") or sp.name[: -len(".state.json")]
        st["exit_code"] = code
        st["completed_unix"] = now()
        st["updated_unix"] = now()
        if code == 0:
            st["status"] = "success"
            st["reason"] = "process exited 0 (auto-done)"
            write_json(sp, st)
            mark_job_file(root, job_id, "completed", "auto-done: exit 0")
        elif code > 0:
            st["status"] = "failed"
            st["reason"] = f"process exited {code}"
            write_json(sp, st)
            mark_job_file(root, job_id, "failed", f"auto-fail: exit {code}")
        else:
            st["status"] = "killed"
            st["reason"] = f"terminated by signal {-code} (transient; retry allowed)"
            write_json(sp, st)
        return


def reap_children(root: Path) -> None:
    """Reapt beendete Kindprozesse und verbucht ihre Exit-Codes (Auto-Done).

    Der Runner startet Jobs detached, bleibt aber Parent: ohne wait()
    wurden fertige Jobs zu Zombies (pid_alive sah sie als running), und
    nach einem Daemon-Neustart wurden fertige Jobs mangels Erfolgs-
    kriterium NEU gestartet (Vorfaelle 2026-06-12/13, u. a. 16.5h-Job).
    """
    while True:
        try:
            pid, status = os.waitpid(-1, os.WNOHANG)
        except (ChildProcessError, OSError):
            return
        if pid == 0:
            return
        finalize_job_by_pid(root, pid, _exit_code_from_status(status))


def get_free_mem_gb() -> float | None:
    system = platform.system()
    if system == "Linux":
        try:
            meminfo = Path("/proc/meminfo").read_text(encoding="utf-8")
        except Exception:
            return None
        values: dict[str, int] = {}
        for line in meminfo.splitlines():
            if ":" in line:
                key, rest = line.split(":", 1)
                parts = rest.strip().split()
                if parts and parts[0].isdigit():
                    values[key] = int(parts[0])
        kb = values.get("MemAvailable") or values.get("MemFree")
        return None if kb is None else kb / (1024 * 1024)
    if system == "Darwin":
        try:
            out = subprocess.check_output(["vm_stat"], text=True)
        except Exception:
            return None
        page_size = 4096
        m = re.search(r"page size of (\d+) bytes", out)
        if m:
            page_size = int(m.group(1))
        pages = 0
        for label in [
            "Pages free",
            "Pages inactive",
            "Pages speculative",
            "Pages purgeable",
        ]:
            mm = re.search(rf"{re.escape(label)}:\s+(\d+)", out)
            if mm:
                pages += int(mm.group(1))
        return pages * page_size / (1024**3)
    return None


def loadavg_1min() -> float | None:
    try:
        return os.getloadavg()[0]
    except Exception:
        return None


def nested_get(payload: dict[str, Any], dotted: str) -> Any:
    cur: Any = payload
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def output_success(root: Path, job: dict[str, Any]) -> tuple[bool, str]:
    expected = [root / p for p in job.get("expected_outputs", [])]
    if expected and not all(path.exists() for path in expected):
        missing = [str(path.relative_to(root)) for path in expected if not path.exists()]
        return False, "missing outputs: " + ", ".join(missing)
    spec = job.get("success_json")
    if spec:
        path = root / spec["path"]
        if not path.exists():
            return False, f"success json missing: {spec['path']}"
        try:
            data = read_json(path)
        except Exception as exc:
            return False, f"success json unreadable: {exc}"
        value = nested_get(data, spec["field"])
        if value != spec.get("equals"):
            return False, f"success field {spec['field']}={value!r}"
    return bool(expected or spec), "outputs accepted"


def sage_script_backend_for_bindir(bindir: Path) -> tuple[str | None, str]:
    python_path = bindir / "python"
    if not python_path.exists() or not os.access(python_path, os.X_OK):
        return None, f"python missing in {bindir}"
    env = os.environ.copy()
    env["PATH"] = str(bindir) + os.pathsep + env.get("PATH", "")
    try:
        proc = subprocess.run(
            [str(python_path), "-c", "import sage.all"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=env,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        return None, f"sage import timeout in {bindir}"
    if proc.returncode != 0:
        return None, f"sage import failed in {bindir}"
    q_bindir = shlex.quote(str(bindir))
    q_python = shlex.quote(str(python_path))
    return f"PATH={q_bindir}:$PATH {q_python}", f"sage python at {python_path}"


def native_sage_works(path: str) -> bool:
    try:
        proc = subprocess.run(
            [path, "-v"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        return False
    return proc.returncode == 0


def docker_image_present(image: str) -> bool:
    docker = shutil.which("docker")
    if not docker:
        return False
    proc = subprocess.run(
        [docker, "image", "inspect", image],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return proc.returncode == 0


def sage_command(root: Path, job: dict[str, Any]) -> tuple[str | None, str]:
    home = Path.home()
    for bindir in [
        home / "mamba" / "envs" / "sage" / "bin",
        home / "micromamba" / "envs" / "sage" / "bin",
    ]:
        if bindir.exists():
            cmd, reason = sage_script_backend_for_bindir(bindir)
            if cmd:
                return cmd, reason

    native = shutil.which("sage")
    if native and native_sage_works(native):
        return shlex.quote(native), "native sage"

    backend = job.get("backend", {})
    if backend.get("allow_docker"):
        docker = shutil.which("docker")
        image = backend.get("docker_image", "sagemath/sagemath:latest")
        if not docker:
            return None, "no native sage and no docker"
        if not docker_image_present(image):
            return None, f"docker image not present: {image}"
        cmd = (
            f"{shlex.quote(docker)} run --rm -e HOME=/tmp "
            f"-v {shlex.quote(str(root))}:/work -w /work "
            f"{shlex.quote(image)} sage"
        )
        return cmd, f"docker sage ({image})"

    return None, "no sage backend"


def state_path(root: Path, job_id: str) -> Path:
    return root / QUEUE_DIR / "state" / f"{job_id}.state.json"


def load_state(root: Path, job_id: str) -> dict[str, Any]:
    path = state_path(root, job_id)
    if path.exists():
        try:
            return read_json(path)
        except Exception:
            return {}
    return {}


def active_queue_job(root: Path, jobs: list[dict[str, Any]]) -> dict[str, Any] | None:
    for job in jobs:
        st = load_state(root, job["id"])
        if st.get("status") == "running" and pid_alive(int(st.get("pid", 0))):
            return {"job": job["id"], "pid": st.get("pid")}
    return None


def dependencies_met(root: Path, job: dict[str, Any]) -> tuple[bool, str]:
    for dep in job.get("depends_on_success", []):
        dep_state = load_state(root, dep)
        if dep_state.get("status") != "success":
            return False, f"dependency not successful: {dep}"
    return True, "dependencies ok"


def job_eligible(root: Path, job: dict[str, Any], jobs: list[dict[str, Any]]) -> tuple[bool, str, dict[str, Any]]:
    job_status = str(job.get("status", "pending")).lower()
    if job_status in {"paused", "blocked", "disabled", "completed", "done", "failed"}:
        note = (job.get('pause_reason') or job.get('block_reason')
                or job.get('completed_reason') or job.get('resolution') or 'manual hold')
        return False, f"job status {job_status}: {note}", {}

    aliases = host_aliases()
    allowed = {str(x) for x in job.get("allowed_hosts", [])}
    disallowed = {str(x) for x in job.get("disallowed_hosts", [])}
    if aliases & disallowed:
        return False, f"host disallowed: {sorted(aliases & disallowed)}", {}
    if allowed and not (aliases & allowed):
        return False, f"host not in allowed set: aliases={sorted(aliases)}", {}

    ok, reason = output_success(root, job)
    if ok:
        st = load_state(root, job["id"])
        st.update({"status": "success", "reason": reason, "updated_unix": now()})
        write_json(state_path(root, job["id"]), st)
        jp = job.get("_path")
        if jp:
            try:
                jd = read_json(Path(jp))
                if str(jd.get("status", "")).lower() not in {"completed", "done"}:
                    jd["status"] = "completed"
                    jd["completed_unix"] = now()
                    jd["completed_reason"] = reason
                    write_json(Path(jp), jd)
            except Exception:
                pass
        return False, "already successful", {}

    st = load_state(root, job["id"])
    if st.get("status") == "finished_unverified":
        return False, ("finished unverified: pid gone without exit info -- "
                       "verify outputs, then mark job done or requeue (delete state)"), {}
    if st.get("status") == "failed":
        return False, f"state failed: {st.get('reason', 'exit != 0')} -- requeue manually", {}
    if st.get("status") == "running":
        pid = int(st.get("pid", 0))
        if pid_alive(pid):
            return False, f"already running pid={pid}", {}
        # PID weg, aber kein Exit-Code eingesammelt (z. B. Runner-Neustart
        # dazwischen, Kind von launchd adoptiert): NICHT blind neu starten
        # (Vorfall 2026-06-13: fertiger 16.5h-Job wurde rerun-gestartet).
        st.update({"status": "finished_unverified", "updated_unix": now(),
                   "reason": "pid gone, exit code unknown (runner restart between?)"})
        write_json(state_path(root, job["id"]), st)
        return False, "finished_unverified: pid gone without exit info", {}

    active = active_queue_job(root, jobs)
    if active:
        # Ein Queue-Job laeuft bereits. Ein weiterer (Extra-Slot) ist nur erlaubt,
        # wenn der Watchdog Kapazitaet signalisiert (pull_ok). pull_ok wird vom
        # Watchdog nach jedem Start in den Cooldown gesetzt -> hoechstens 1 Extra
        # gleichzeitig in flight (User-Slot-Modell).
        slot = read_slot_status()
        if not slot.get("pull_ok"):
            why = "pressure/cooldown" if slot else "no fresh watchdog slot status"
            return False, f"queue job running, kein Pull-Slot ({why}): {active}", {}
        # pull_ok=true -> Extra-Slot erlaubt, weiter pruefen.
        # HINWEIS: Kein oberer RAM-Guard hier -- falls der gestartete Job das
        # System in Level 4 drueckt, faengt der Watchdog das ab (Schritt 3:
        # pausiert + overflow_locked). resource_policy bleibt Per-Job-Untergrenze.

    ok, reason = dependencies_met(root, job)
    if not ok:
        return False, reason, {}

    blockers = process_matches(job.get("defer_while_process_regex", []))
    if blockers:
        return False, "deferred by blocker process: " + blockers[0], {"blockers": blockers[:10]}

    policy = job.get("resource_policy", {})
    free_mem = get_free_mem_gb()
    if free_mem is not None and float(policy.get("min_free_mem_gb", 0)) > free_mem:
        return False, f"free memory too low: {free_mem:.2f} GB", {"free_mem_gb": free_mem}
    load1 = loadavg_1min()
    if load1 is not None and float(policy.get("max_load_1min", 999999)) < load1:
        return False, f"load too high: {load1:.2f}", {"load_1min": load1}

    sage, backend_reason = sage_command(root, job)
    if not sage:
        return False, "backend unavailable: " + backend_reason, {}
    return True, "eligible", {"sage": sage, "backend": backend_reason}


def launch_job(root: Path, job: dict[str, Any], ctx: dict[str, Any], dry_run: bool) -> dict[str, Any]:
    raw_cmd = job["command"]
    cmd = raw_cmd.replace("{sage}", ctx["sage"])
    log_dir = root / QUEUE_DIR / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"{job['id']}.log"
    state = {
        "job_id": job["id"],
        "status": "dry_run" if dry_run else "running",
        "host": platform.node(),
        "aliases": sorted(host_aliases()),
        "backend": ctx.get("backend"),
        "command": cmd,
        "log": str(log_path.relative_to(root)),
        "started_unix": now(),
        "date": DATE,
    }
    if dry_run:
        write_json(state_path(root, job["id"]), state)
        return state

    log_handle = log_path.open("ab")
    proc = subprocess.Popen(
        cmd,
        shell=True,
        cwd=str(root),
        stdout=log_handle,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    state["pid"] = proc.pid
    write_json(state_path(root, job["id"]), state)
    register_runner_job(job["id"], proc.pid)
    return state


def collect_jobs(root: Path) -> list[dict[str, Any]]:
    jobs_dir = root / QUEUE_DIR / "jobs"
    jobs = []
    for path in sorted(jobs_dir.glob("*.json")):
        job = read_json(path)
        job["_path"] = str(path)
        jobs.append(job)
    jobs.sort(key=lambda item: int(item.get("priority", 1000)))
    return jobs


def run_once(root: Path, dry_run: bool = False) -> dict[str, Any]:
    reap_children(root)
    cleanup_runner_jobs()
    jobs = collect_jobs(root)
    decisions = []
    for job in jobs:
        eligible, reason, ctx = job_eligible(root, job, jobs)
        decisions.append({"job": job["id"], "eligible": eligible, "reason": reason})
        if eligible:
            launch = launch_job(root, job, ctx, dry_run=dry_run)
            return {"action": "launched" if not dry_run else "dry_run", "job": job["id"], "state": launch, "decisions": decisions}
    return {"action": "none", "decisions": decisions}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--loop", action="store_true")
    parser.add_argument("--interval", type=int, default=300)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--status-json", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    if not (root / QUEUE_DIR).exists():
        print(f"queue dir missing under {root}", file=sys.stderr)
        return 2

    if not args.once and not args.loop:
        args.once = True

    while True:
        result = run_once(root, dry_run=args.dry_run)
        result["host"] = platform.node()
        result["aliases"] = sorted(host_aliases())
        result["checked_unix"] = now()
        if args.status_json:
            write_json(args.status_json, result)
        print(json.dumps(result, ensure_ascii=False))
        if not args.loop:
            break
        time.sleep(max(30, int(args.interval)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
