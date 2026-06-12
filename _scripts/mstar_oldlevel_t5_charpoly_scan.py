"""Loop 98 T5-charpoly filter for heavy old levels modulo 3863.

This is a lighter necessary test than the Loop 97 kernel-intersection scan.
For a level M to contain the Reyssat residual system in its newspace, the
Reyssat trace a_5 must be an eigenvalue of T_5 on S_2(Gamma0(M))^new modulo
3863.  The script tests that condition with per-level subprocess timeouts.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from sage.all import CuspForms, EllipticCurve, GF, Gamma0, factor


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-05-09"
JSON_OUT = ROOT / "_results" / f"mstar_oldlevel_t5_charpoly_scan_{DATE}.json"

Q = 3863
P = 5
DEFAULT_LEVELS = [109, 218, 327, 872, 1744, 2507, 3488, 15042, 20056, 40112, 80224, 120336, 60168]
DEFAULT_TIMEOUT = 180


def factor_string(n: int) -> str:
    return str(factor(int(n)))


def reyssat_curve(mode: str):
    a_raw = 2
    b_raw = 3**10 * 109
    if mode == "raw":
        a, b = a_raw, b_raw
    elif mode == "anc":
        a, b = b_raw, a_raw
    else:
        raise ValueError(f"unknown mode {mode}")
    return EllipticCurve([0, b - a, 0, -a * b, 0])


def root_multiplicity(poly, root) -> int:
    R = poly.parent()
    x = R.gen()
    divisor = x - root
    current = poly
    multiplicity = 0
    while current.degree() > 0 and current(root) == 0:
        q, r = current.quo_rem(divisor)
        if r != 0:
            break
        current = q
        multiplicity += 1
    return multiplicity


def hecke_polynomial_for_newspace(level: int, prime: int) -> tuple[Any, str, int, int]:
    space = CuspForms(Gamma0(level), 2)
    total_dim = int(space.dimension())
    newspace = space.new_subspace()
    new_dim = int(newspace.dimension())
    if hasattr(newspace, "hecke_polynomial"):
        return newspace.hecke_polynomial(prime), "newspace.hecke_polynomial", total_dim, new_dim
    if hasattr(newspace, "hecke_matrix"):
        return newspace.hecke_matrix(prime).charpoly(), "newspace.hecke_matrix.charpoly", total_dim, new_dim
    raise RuntimeError("newspace has no hecke_polynomial or hecke_matrix method")


def worker(level: int, mode: str) -> dict[str, Any]:
    start = time.perf_counter()
    F = GF(Q)
    E = reyssat_curve(mode)
    a_p = int(E.ap(P))
    a_mod = F(a_p)
    poly, method, total_dim, new_dim = hecke_polynomial_for_newspace(level, P)
    poly_mod = poly.change_ring(F)
    value = poly_mod(a_mod)
    mult = root_multiplicity(poly_mod, a_mod) if value == 0 else 0
    elapsed = time.perf_counter() - start
    return {
        "level": level,
        "level_factor": factor_string(level),
        "mode": mode,
        "status": "ok",
        "elapsed_seconds": elapsed,
        "q": Q,
        "prime": P,
        "a_p": a_p,
        "a_p_mod_q": int(a_mod),
        "method": method,
        "total_cusp_dimension": total_dim,
        "new_dimension": new_dim,
        "charpoly_degree": int(poly.degree()),
        "value_at_a_p_mod_q": int(value),
        "a_p_is_root_mod_q": value == 0,
        "root_multiplicity_mod_q": mult,
    }


def run_worker(args: argparse.Namespace) -> None:
    print(json.dumps(worker(args.level, args.mode), ensure_ascii=False))


def run_manager(args: argparse.Namespace) -> None:
    levels = [int(x) for x in args.levels.split(",") if x.strip()]
    rows = []

    def write_payload() -> dict[str, Any]:
        hits = [row for row in rows if row.get("status") == "ok" and row.get("a_p_is_root_mod_q")]
        payload = {
            "date": DATE,
            "purpose": "Necessary oldlevel filter: whether Reyssat a_5 is a T_5 newspace eigenvalue modulo 3863.",
            "guardrail": "Per-level subprocess timeout; T5-only necessary condition, not a full residual-system proof.",
            "q": Q,
            "prime": P,
            "levels": levels,
            "timeout_seconds_per_worker": args.timeout_seconds,
            "summary": {
                "worker_count": len(rows),
                "ok_count": sum(1 for row in rows if row.get("status") == "ok"),
                "timeout_count": sum(1 for row in rows if row.get("status") == "timeout"),
                "error_count": sum(1 for row in rows if row.get("status") == "error"),
                "hit_count": len(hits),
                "hits": [
                    {
                        "level": row["level"],
                        "mode": row["mode"],
                        "new_dimension": row.get("new_dimension"),
                        "root_multiplicity_mod_q": row.get("root_multiplicity_mod_q"),
                        "elapsed_seconds": row.get("elapsed_seconds"),
                    }
                    for row in hits
                ],
            },
            "rows": rows,
        }
        JSON_OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return payload

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
            ]
            start = time.perf_counter()
            try:
                proc = subprocess.run(cmd, text=True, capture_output=True, timeout=args.timeout_seconds, check=False)
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
                            "status": "error",
                            "returncode": proc.returncode,
                            "elapsed_seconds": elapsed,
                            "stdout_tail": proc.stdout[-2000:],
                            "stderr_tail": proc.stderr[-2000:],
                        }
                    )
            except subprocess.TimeoutExpired as exc:
                rows.append(
                    {
                        "level": level,
                        "mode": mode,
                        "status": "timeout",
                        "timeout_seconds": args.timeout_seconds,
                        "stdout_tail": (exc.stdout or "")[-2000:] if isinstance(exc.stdout, str) else "",
                        "stderr_tail": (exc.stderr or "")[-2000:] if isinstance(exc.stderr, str) else "",
                        }
                    )
            write_payload()

    payload = write_payload()
    print(JSON_OUT)
    print(json.dumps(payload["summary"], indent=2, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--level", type=int)
    parser.add_argument("--mode", choices=["raw", "anc"], default="raw")
    parser.add_argument("--levels", default=",".join(str(x) for x in DEFAULT_LEVELS))
    parser.add_argument("--timeout-seconds", type=int, default=DEFAULT_TIMEOUT)
    args = parser.parse_args()
    if args.worker:
        if args.level is None:
            raise SystemExit("--level is required in worker mode")
        run_worker(args)
    else:
        run_manager(args)


if __name__ == "__main__":
    main()
