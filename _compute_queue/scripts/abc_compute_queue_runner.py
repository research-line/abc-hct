#!/usr/bin/env python3
"""Small remote compute queue runner for abc/HCT jobs.

The runner is intentionally conservative:
- it is meant to run on Mac Studio / server / desktop, not on the laptop;
- it starts at most one queued job at a time;
- each job is declared as JSON under _compute_queue/jobs;
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
QUEUE_DIR = "_compute_queue"


def now() -> float:
    return time.time()


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
        if "abc_compute_queue_runner.py" in row:
            continue
        for pat in patterns:
            if re.search(pat, row):
                hits.append(row)
                break
    return hits


def pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


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
    if job_status in {"paused", "blocked", "disabled"}:
        return False, f"job status {job_status}: {job.get('pause_reason') or job.get('block_reason') or 'manual hold'}", {}

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
        return False, "already successful", {}

    st = load_state(root, job["id"])
    if st.get("status") == "running":
        pid = int(st.get("pid", 0))
        if pid_alive(pid):
            return False, f"already running pid={pid}", {}
        st.update({"status": "stopped_or_failed", "updated_unix": now(), "reason": "pid not alive"})
        write_json(state_path(root, job["id"]), st)

    active = active_queue_job(root, jobs)
    if active:
        return False, f"another queue job is running: {active}", {}

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
