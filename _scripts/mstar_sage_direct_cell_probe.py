#!/usr/bin/env python3
"""Loop 144: Probe direct Sage access to smaller modular-symbol cells.

This checks whether using the +1 modular-symbol quotient gets us to
newspace/decomposition data before the large sign=0 construction bottleneck.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from sage.all import GF, Gamma0, ModularSymbols, factor


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-05-10"
JSON_OUT = ROOT / "_results" / f"mstar_sage_direct_cell_probe_{DATE}.json"
MD_OUT = ROOT / "_results" / f"mstar_sage_direct_cell_probe_{DATE}.md"

Q = 3863
DEFAULT_LEVELS = [109, 218, 60168]
DEFAULT_TIMEOUT = 90


def factor_string(n: int) -> str:
    return str(factor(int(n)))


def worker(level: int, sign: int) -> dict[str, Any]:
    start = time.perf_counter()
    field = GF(Q)
    module_start = time.perf_counter()
    module = ModularSymbols(Gamma0(level), 2, sign=sign, base_ring=field)
    module_seconds = time.perf_counter() - module_start
    cuspidal_start = time.perf_counter()
    cuspidal = module.cuspidal_subspace()
    cuspidal_seconds = time.perf_counter() - cuspidal_start
    new_start = time.perf_counter()
    newspace = cuspidal.new_subspace()
    new_seconds = time.perf_counter() - new_start

    decomp_rows: list[dict[str, Any]] = []
    for name, fn in [
        ("cuspidal_decomposition_bound5", lambda: cuspidal.decomposition(bound=5)),
        ("newspace_decomposition_bound5", lambda: newspace.decomposition(bound=5)),
        ("cuspidal_star_decomposition", lambda: cuspidal.star_decomposition()),
        ("newspace_star_decomposition", lambda: newspace.star_decomposition()),
    ]:
        step_start = time.perf_counter()
        try:
            pieces = fn()
            decomp_rows.append(
                {
                    "name": name,
                    "status": "ok",
                    "count": len(pieces),
                    "dims": [int(piece.dimension()) for piece in pieces],
                    "elapsed_seconds": time.perf_counter() - step_start,
                }
            )
        except Exception as exc:
            decomp_rows.append(
                {
                    "name": name,
                    "status": "error",
                    "error": f"{type(exc).__name__}: {exc}",
                    "elapsed_seconds": time.perf_counter() - step_start,
                }
            )

    return {
        "level": level,
        "level_factor": factor_string(level),
        "sign": sign,
        "status": "ok",
        "q": Q,
        "ambient_dimension": int(module.dimension()),
        "cuspidal_dimension": int(cuspidal.dimension()),
        "new_dimension": int(newspace.dimension()),
        "timings": {
            "module_seconds": module_seconds,
            "cuspidal_seconds": cuspidal_seconds,
            "newspace_seconds": new_seconds,
            "total_seconds": time.perf_counter() - start,
        },
        "decompositions": decomp_rows,
    }


def run_worker(args: argparse.Namespace) -> None:
    if args.level is None:
        raise SystemExit("--level is required in worker mode")
    print(json.dumps(worker(args.level, args.sign), ensure_ascii=False))


def write_markdown(payload: dict[str, Any]) -> None:
    lines: list[str] = []
    lines.append("# M*: Sage-Direktzugriff auf kleine Zellen")
    lines.append("")
    lines.append(f"Datum: {payload['date']}")
    lines.append("")
    lines.append("## Ergebnis")
    lines.append("")
    lines.append("| Level | Sign | Status | Ambient | Newdim | Befund |")
    lines.append("|---:|---:|---|---:|---:|---|")
    for row in payload["rows"]:
        if row.get("status") != "ok":
            lines.append(
                f"| {row['level']} | {row.get('sign')} | {row['status']} |  |  | "
                f"Timeout {row.get('timeout_seconds')}s |"
            )
            continue
        decomp = next(
            (x for x in row["decompositions"] if x["name"] == "newspace_decomposition_bound5"),
            None,
        )
        finding = "decomp " + str(decomp["dims"]) if decomp and decomp["status"] == "ok" else "keine Zerlegung"
        lines.append(
            f"| {row['level']} | {row['sign']} | ok | {row['ambient_dimension']} | "
            f"{row['new_dimension']} | {finding} |"
        )
    lines.append("")
    lines.append("## Schluss")
    lines.append("")
    lines.append(
        "Auf kleinen Levels funktioniert der `sign=+1`-Quotient und liefert "
        "Zerlegungen. Auf \\(60168\\) timeoutet aber bereits der Aufbau des "
        "ModularSymbols-Raums. Lokaler Sage-Direktzugriff auf die kleinen "
        "LMFDB-AL-Zellen ist damit weiterhin blockiert."
    )
    lines.append("")
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")


def write_payload(args: argparse.Namespace, rows: list[dict[str, Any]]) -> dict[str, Any]:
    payload = {
        "date": DATE,
        "purpose": "Sage sign=+1 cell/decomposition access probe.",
        "q": Q,
        "levels": [int(x) for x in args.levels.split(",") if x.strip()],
        "sign": args.sign,
        "timeout_seconds_per_worker": args.timeout_seconds,
        "summary": {
            "worker_count": len(rows),
            "ok_count": sum(1 for row in rows if row.get("status") == "ok"),
            "timeout_count": sum(1 for row in rows if row.get("status") == "timeout"),
            "error_count": sum(1 for row in rows if row.get("status") == "error"),
        },
        "rows": rows,
    }
    JSON_OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(payload)
    return payload


def run_manager(args: argparse.Namespace) -> None:
    levels = [int(x) for x in args.levels.split(",") if x.strip()]
    rows: list[dict[str, Any]] = []
    for level in levels:
        cmd = [
            sys.executable,
            str(Path(__file__).resolve()),
            "--worker",
            "--level",
            str(level),
            "--sign",
            str(args.sign),
        ]
        start = time.perf_counter()
        try:
            proc = subprocess.run(
                cmd,
                text=True,
                capture_output=True,
                timeout=args.timeout_seconds,
                check=False,
            )
            elapsed = time.perf_counter() - start
            if proc.returncode == 0:
                parsed = json.loads(proc.stdout.strip().splitlines()[-1])
                parsed["manager_elapsed_seconds"] = elapsed
                rows.append(parsed)
            else:
                rows.append(
                    {
                        "level": level,
                        "sign": args.sign,
                        "status": "error",
                        "returncode": proc.returncode,
                        "elapsed_seconds": elapsed,
                        "stdout_tail": proc.stdout[-4000:],
                        "stderr_tail": proc.stderr[-4000:],
                    }
                )
        except subprocess.TimeoutExpired as exc:
            rows.append(
                {
                    "level": level,
                    "sign": args.sign,
                    "status": "timeout",
                    "timeout_seconds": args.timeout_seconds,
                    "stdout_tail": (exc.stdout or "")[-4000:] if isinstance(exc.stdout, str) else "",
                    "stderr_tail": (exc.stderr or "")[-4000:] if isinstance(exc.stderr, str) else "",
                }
            )
        write_payload(args, rows)

    payload = write_payload(args, rows)
    print(JSON_OUT)
    print(MD_OUT)
    print(json.dumps(payload["summary"], indent=2, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--level", type=int)
    parser.add_argument("--levels", default=",".join(str(x) for x in DEFAULT_LEVELS))
    parser.add_argument("--sign", type=int, default=1)
    parser.add_argument("--timeout-seconds", type=int, default=DEFAULT_TIMEOUT)
    args = parser.parse_args()
    if args.worker:
        run_worker(args)
    else:
        run_manager(args)


if __name__ == "__main__":
    main()
