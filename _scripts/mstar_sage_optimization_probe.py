#!/usr/bin/env python3
"""Loop 140: Sage API probe for optimizing the restlevel cascade.

Run under Sage/Python.  The manager executes small API probes in subprocesses
with timeouts, so unstable constructors are recorded instead of hanging the
session.  The probe intentionally uses small levels only; it is infrastructure
triage, not a mathematical test of the restlevels.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from sage.all import CuspForms, GF, Gamma0, ModularSymbols, identity_matrix


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "_results"
DATE = "2026-05-10"
JSON_OUT = RESULTS / f"mstar_sage_optimization_probe_{DATE}.json"
MD_OUT = RESULTS / f"mstar_sage_optimization_probe_{DATE}.md"

Q = 3863
DEFAULT_TIMEOUT = 60


def method_names(obj: Any, pattern: str) -> list[str]:
    return [name for name in dir(obj) if pattern.lower() in name.lower()][:40]


def probe_cuspforms_newspace(level: int, prime: int) -> dict[str, Any]:
    start = time.perf_counter()
    space = CuspForms(Gamma0(level), 2)
    newspace = space.new_subspace()
    matrix = newspace.hecke_matrix(prime)
    return {
        "probe": "cuspforms_newspace_hecke_matrix",
        "level": level,
        "prime": prime,
        "status": "ok",
        "total_dimension": int(space.dimension()),
        "new_dimension": int(newspace.dimension()),
        "matrix_nrows": int(matrix.nrows()),
        "matrix_parent": str(matrix.parent())[:180],
        "elapsed_seconds": time.perf_counter() - start,
    }


def probe_cuspforms_methods(level: int) -> dict[str, Any]:
    start = time.perf_counter()
    space = CuspForms(Gamma0(level), 2)
    newspace = space.new_subspace()
    return {
        "probe": "cuspforms_newspace_methods",
        "level": level,
        "status": "ok",
        "total_dimension": int(space.dimension()),
        "new_dimension": int(newspace.dimension()),
        "atkin_methods": method_names(newspace, "atkin"),
        "decomp_methods": method_names(newspace, "decomp"),
        "new_methods": method_names(newspace, "new"),
        "modular_symbol_methods": method_names(newspace, "symbol"),
        "elapsed_seconds": time.perf_counter() - start,
    }


def probe_modsym_qq(level: int, prime: int) -> dict[str, Any]:
    start = time.perf_counter()
    module = ModularSymbols(Gamma0(level), 2, sign=0)
    cuspidal = module.cuspidal_subspace()
    newspace = cuspidal.new_subspace()
    matrix = newspace.hecke_matrix(prime)
    return {
        "probe": "modularsymbols_QQ_newspace_hecke_matrix",
        "level": level,
        "prime": prime,
        "status": "ok",
        "ambient_dimension": int(module.dimension()),
        "cuspidal_dimension": int(cuspidal.dimension()),
        "new_dimension": int(newspace.dimension()),
        "matrix_nrows": int(matrix.nrows()),
        "matrix_parent": str(matrix.parent())[:180],
        "atkin_methods": method_names(newspace, "atkin"),
        "decomp_methods": method_names(newspace, "decomp"),
        "elapsed_seconds": time.perf_counter() - start,
    }


def probe_modsym_gf(level: int, prime: int) -> dict[str, Any]:
    start = time.perf_counter()
    field = GF(Q)
    module = ModularSymbols(Gamma0(level), 2, sign=0, base_ring=field)
    cuspidal = module.cuspidal_subspace()
    has_new = hasattr(cuspidal, "new_subspace")
    result: dict[str, Any] = {
        "probe": "modularsymbols_GF_newspace_hecke_matrix",
        "level": level,
        "prime": prime,
        "status": "ok",
        "q": Q,
        "ambient_dimension": int(module.dimension()),
        "cuspidal_dimension": int(cuspidal.dimension()),
        "cuspidal_has_new_subspace": bool(has_new),
    }
    if has_new:
        newspace = cuspidal.new_subspace()
        matrix = newspace.hecke_matrix(prime)
        operator = matrix - field(0) * identity_matrix(field, int(matrix.nrows()))
        result.update(
            {
                "new_dimension": int(newspace.dimension()),
                "matrix_nrows": int(matrix.nrows()),
                "matrix_parent": str(matrix.parent())[:180],
                "rank_zero_shift": int(operator.rank()),
                "atkin_methods": method_names(newspace, "atkin"),
                "decomp_methods": method_names(newspace, "decomp"),
            }
        )
    result["elapsed_seconds"] = time.perf_counter() - start
    return result


def worker(args: argparse.Namespace) -> dict[str, Any]:
    if args.probe == "cuspforms_newspace":
        return probe_cuspforms_newspace(args.level, args.prime)
    if args.probe == "cuspforms_methods":
        return probe_cuspforms_methods(args.level)
    if args.probe == "modsym_qq":
        return probe_modsym_qq(args.level, args.prime)
    if args.probe == "modsym_gf":
        return probe_modsym_gf(args.level, args.prime)
    raise ValueError(f"unknown probe {args.probe}")


def run_worker(args: argparse.Namespace) -> None:
    print(json.dumps(worker(args), ensure_ascii=False))


def run_manager(args: argparse.Namespace) -> None:
    tasks = [
        {"probe": "cuspforms_methods", "level": 109, "prime": 5},
        {"probe": "cuspforms_newspace", "level": 109, "prime": 5},
        {"probe": "modsym_qq", "level": 109, "prime": 5},
        {"probe": "modsym_gf", "level": 11, "prime": 5},
        {"probe": "modsym_gf", "level": 109, "prime": 5},
    ]
    rows: list[dict[str, Any]] = []
    for task in tasks:
        cmd = [
            sys.executable,
            str(Path(__file__).resolve()),
            "--worker",
            "--probe",
            task["probe"],
            "--level",
            str(task["level"]),
            "--prime",
            str(task["prime"]),
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
                        **task,
                        "status": "error",
                        "returncode": proc.returncode,
                        "elapsed_seconds": elapsed,
                        "stdout_tail": proc.stdout[-3000:],
                        "stderr_tail": proc.stderr[-3000:],
                    }
                )
        except subprocess.TimeoutExpired as exc:
            rows.append(
                {
                    **task,
                    "status": "timeout",
                    "timeout_seconds": args.timeout_seconds,
                    "stdout_tail": (exc.stdout or "")[-3000:] if isinstance(exc.stdout, str) else "",
                    "stderr_tail": (exc.stderr or "")[-3000:] if isinstance(exc.stderr, str) else "",
                }
            )
        write_outputs(args, rows)
    payload = write_outputs(args, rows)
    print(JSON_OUT)
    print(json.dumps(payload["summary"], indent=2, ensure_ascii=False))


def write_outputs(args: argparse.Namespace, rows: list[dict[str, Any]]) -> dict[str, Any]:
    payload = {
        "date": DATE,
        "purpose": "Small-level Sage API triage for optimizing restlevel kernel cascade.",
        "q": Q,
        "timeout_seconds_per_probe": args.timeout_seconds,
        "summary": {
            "probe_count": len(rows),
            "ok_count": sum(1 for row in rows if row.get("status") == "ok"),
            "timeout_count": sum(1 for row in rows if row.get("status") == "timeout"),
            "error_count": sum(1 for row in rows if row.get("status") == "error"),
            "modsym_gf_ok": [
                {"level": row.get("level"), "elapsed_seconds": row.get("elapsed_seconds")}
                for row in rows
                if row.get("probe") == "modularsymbols_GF_newspace_hecke_matrix"
                and row.get("status") == "ok"
            ],
            "modsym_gf_failed": [
                {"level": row.get("level"), "status": row.get("status")}
                for row in rows
                if row.get("probe") in {"modsym_gf", "modularsymbols_GF_newspace_hecke_matrix"}
                and row.get("status") != "ok"
            ],
        },
        "rows": rows,
    }
    JSON_OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# M*: Sage-Optimierungs-API-Probe",
        "",
        f"Datum: {DATE}",
        "",
        "## Kurzbefund",
        "",
        f"- Probes: {payload['summary']['probe_count']}.",
        f"- OK: {payload['summary']['ok_count']}.",
        f"- Timeouts: {payload['summary']['timeout_count']}.",
        f"- Errors: {payload['summary']['error_count']}.",
        "",
        "## Ergebnisse",
        "",
        "| Probe | Level | Status | Dimensionen | Zeit | Hinweis |",
        "|---|---:|---|---|---:|---|",
    ]
    for row in rows:
        dims = []
        for key in ("total_dimension", "ambient_dimension", "cuspidal_dimension", "new_dimension"):
            if key in row:
                dims.append(f"{key}={row[key]}")
        hint = ""
        if row.get("atkin_methods"):
            hint = "Atkin-Methoden: " + ", ".join(row["atkin_methods"][:5])
        if row.get("status") == "timeout":
            hint = "timeout"
        if row.get("status") == "error":
            hint = (row.get("stderr_tail") or row.get("stdout_tail") or "error")[:120]
        lines.append(
            f"| {row.get('probe')} | {row.get('level')} | {row.get('status')} | "
            f"{'; '.join(dims)} | {float(row.get('elapsed_seconds', 0.0)):.3f} | {hint} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Diese Probe entscheidet nur über verfügbare Sage-APIs auf kleinen Levels.",
            "Ein positiver kleiner Test heißt nicht, dass die Restlevels leicht werden.",
            "Ein Timeout oder Fehler schließt aber eine Optimierungsroute als naiv",
            "nutzbar aus.",
            "",
        ]
    )
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--probe", default="cuspforms_methods")
    parser.add_argument("--level", type=int, default=109)
    parser.add_argument("--prime", type=int, default=5)
    parser.add_argument("--timeout-seconds", type=int, default=DEFAULT_TIMEOUT)
    args = parser.parse_args()
    if args.worker:
        run_worker(args)
    else:
        run_manager(args)


if __name__ == "__main__":
    main()
