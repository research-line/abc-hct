#!/usr/bin/env python3
"""Loop 139: Sage worker for the restlevel mod-q determinant/kernel cascade.

Run with Sage/Python, for example from the configured WSL Sage environment.
The manager launches one worker per (level, orientation) and writes JSON after
each worker, so long computations leave usable partial results.

Default target set deliberately excludes the full level 240672.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from sage.all import CuspForms, GF, Gamma0, Matrix, ModularSymbols, VectorSpace, factor, identity_matrix


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-05-10"
JSON_OUT = ROOT / "_results" / f"mstar_restlevel_kernel_cascade_{DATE}.json"

Q = 3863
DEFAULT_LEVELS = [60168, 80224, 120336]
DEFAULT_PRIMES = [5, 7, 11, 13]
DEFAULT_TIMEOUT = 900

RAW_A = 2
RAW_B = 3**10 * 109


def factor_string(n: int) -> str:
    return str(factor(int(n)))


def legendre_symbol(n: int, p: int) -> int:
    n %= p
    if n == 0:
        return 0
    value = pow(n, (p - 1) // 2, p)
    return 1 if value == 1 else -1


def frey_ab(mode: str) -> tuple[int, int]:
    if mode == "raw":
        return RAW_A, RAW_B
    if mode == "anc":
        return RAW_B, RAW_A
    raise ValueError(f"unknown mode {mode}")


def frey_ap(mode: str, p: int) -> int:
    a, b = frey_ab(mode)
    total = 0
    for x in range(p):
        total += legendre_symbol(x * (x - a) * (x + b), p)
    return -total


def hecke_matrix_mod_q(newspace: Any, prime: int, field: Any) -> Any:
    matrix = newspace.hecke_matrix(prime)
    return Matrix(field, matrix)


def build_newspace(level: int, field: Any, backend: str) -> tuple[Any, dict[str, Any]]:
    if backend == "cuspforms_newspace":
        space = CuspForms(Gamma0(level), 2)
        newspace = space.new_subspace()
        return newspace, {
            "backend": backend,
            "total_cusp_dimension": int(space.dimension()),
            "new_dimension": int(newspace.dimension()),
            "ambient_dimension": None,
            "cuspidal_dimension": None,
        }
    if backend == "modsym_gf":
        module = ModularSymbols(Gamma0(level), 2, sign=0, base_ring=field)
        cuspidal = module.cuspidal_subspace()
        newspace = cuspidal.new_subspace()
        return newspace, {
            "backend": backend,
            "total_cusp_dimension": None,
            "ambient_dimension": int(module.dimension()),
            "cuspidal_dimension": int(cuspidal.dimension()),
            "new_dimension": int(newspace.dimension()),
        }
    raise ValueError(f"unknown backend {backend}")


def worker(level: int, mode: str, primes: list[int], backend: str) -> dict[str, Any]:
    start = time.perf_counter()
    field = GF(Q)
    newspace, space_info = build_newspace(level, field, backend)
    new_dim = int(space_info["new_dimension"])
    ambient = VectorSpace(field, new_dim)
    current = ambient
    rows: list[dict[str, Any]] = []

    for index, prime in enumerate(primes):
        step_start = time.perf_counter()
        ap = frey_ap(mode, prime)
        hecke = hecke_matrix_mod_q(newspace, prime, field)
        operator = hecke - field(ap) * identity_matrix(field, new_dim)
        determinant = operator.det() if index == 0 else None
        kernel = operator.right_kernel()
        current = current.intersection(kernel)
        rows.append(
            {
                "prime": prime,
                "a_p": ap,
                "a_p_mod_q": int(field(ap)),
                "operator_rank": int(operator.rank()),
                "operator_nullity": int(new_dim - operator.rank()),
                "determinant_mod_q": None if determinant is None else int(determinant),
                "determinant_nonzero": None if determinant is None else bool(determinant != 0),
                "kernel_dimension_after_intersection": int(current.dimension()),
                "elapsed_seconds": time.perf_counter() - step_start,
            }
        )
        if current.dimension() == 0:
            break
        if index == 0 and determinant is not None and determinant != 0:
            break

    elapsed = time.perf_counter() - start
    return {
        "level": level,
        "level_factor": factor_string(level),
        "mode": mode,
        "status": "ok",
        "q": Q,
        "backend": backend,
        "tested_primes": primes,
        **space_info,
        "new_dimension": new_dim,
        "steps": rows,
        "final_kernel_dimension": int(current.dimension()),
        "killed": int(current.dimension()) == 0,
        "first_step_determinant_nonzero": rows[0]["determinant_nonzero"] if rows else None,
        "elapsed_seconds": elapsed,
    }


def run_worker(args: argparse.Namespace) -> None:
    primes = [int(x) for x in args.primes.split(",") if x.strip()]
    if args.level is None:
        raise SystemExit("--level is required in worker mode")
    print(json.dumps(worker(args.level, args.mode, primes, args.backend), ensure_ascii=False))


def write_payload(args: argparse.Namespace, rows: list[dict[str, Any]]) -> dict[str, Any]:
    payload = {
        "date": DATE,
        "purpose": "Restlevel mod-3863 determinant/kernel cascade for Reyssat orientations.",
        "guardrail": "Default levels exclude 240672; manager writes partial JSON after every worker.",
        "q": Q,
        "levels": [int(x) for x in args.levels.split(",") if x.strip()],
        "primes": [int(x) for x in args.primes.split(",") if x.strip()],
        "backend": args.backend,
        "timeout_seconds_per_worker": args.timeout_seconds,
        "summary": {
            "worker_count": len(rows),
            "ok_count": sum(1 for row in rows if row.get("status") == "ok"),
            "timeout_count": sum(1 for row in rows if row.get("status") == "timeout"),
            "error_count": sum(1 for row in rows if row.get("status") == "error"),
            "survivor_count": sum(
                1
                for row in rows
                if row.get("status") == "ok" and int(row.get("final_kernel_dimension", 0)) > 0
            ),
            "survivors": [
                {
                    "level": row["level"],
                    "mode": row["mode"],
                    "backend": row.get("backend"),
                    "final_kernel_dimension": row.get("final_kernel_dimension"),
                    "new_dimension": row.get("new_dimension"),
                    "elapsed_seconds": row.get("elapsed_seconds"),
                }
                for row in rows
                if row.get("status") == "ok" and int(row.get("final_kernel_dimension", 0)) > 0
            ],
        },
        "rows": rows,
    }
    JSON_OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return payload


def run_manager(args: argparse.Namespace) -> None:
    levels = [int(x) for x in args.levels.split(",") if x.strip()]
    rows: list[dict[str, Any]] = []
    for level in levels:
        for mode in ("raw", "anc"):
            cmd = [
                sys.executable,
                str(Path(__file__).resolve()),
                "--worker",
                "--level",
                str(level),
                "--mode",
                mode,
                "--primes",
                args.primes,
                "--backend",
                args.backend,
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
                            "mode": mode,
                            "backend": args.backend,
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
                        "mode": mode,
                        "backend": args.backend,
                        "status": "timeout",
                        "timeout_seconds": args.timeout_seconds,
                        "stdout_tail": (exc.stdout or "")[-4000:] if isinstance(exc.stdout, str) else "",
                        "stderr_tail": (exc.stderr or "")[-4000:] if isinstance(exc.stderr, str) else "",
                    }
                )
            write_payload(args, rows)

    payload = write_payload(args, rows)
    print(JSON_OUT)
    print(json.dumps(payload["summary"], indent=2, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--level", type=int)
    parser.add_argument("--mode", choices=["raw", "anc"], default="raw")
    parser.add_argument("--levels", default=",".join(str(x) for x in DEFAULT_LEVELS))
    parser.add_argument("--primes", default=",".join(str(x) for x in DEFAULT_PRIMES))
    parser.add_argument("--backend", choices=["cuspforms_newspace", "modsym_gf"], default="cuspforms_newspace")
    parser.add_argument("--timeout-seconds", type=int, default=DEFAULT_TIMEOUT)
    args = parser.parse_args()
    if args.worker:
        run_worker(args)
    else:
        run_manager(args)


if __name__ == "__main__":
    main()
