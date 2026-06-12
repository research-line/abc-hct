"""Loop 97 targeted old-level scan modulo 3863.

Manager mode launches worker subprocesses with per-level timeouts.  Worker mode
builds a modular-symbol module over GF(3863), tries to use the new cuspidal
submodule, and intersects kernels of T_p - a_p(E) for the Reyssat raw/ANC
trace systems.

This is diagnostic, not a proof-grade full Sturm computation.  It tells us
which old levels are small enough for the current Sage setup and whether a
candidate m_3863 eigenspace survives the first Hecke primes.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from sage.all import EllipticCurve, GF, Gamma0, ModularSymbols, factor, prime_range


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-05-09"
JSON_OUT = ROOT / "_results" / f"mstar_oldlevel_3863_scan_{DATE}.json"

N = 240_672
Q = 3863
WEIGHT = 2
DEFAULT_LEVELS = [109, 218, 327, 872, 1744, 2507, 3488]
TOP_OLDLEVELS = [15042, 40112, 80224, 120336, 20056, 60168]
DEFAULT_TIMEOUT = 90
DEFAULT_PRIME_COUNT = 16


def factor_string(n: int) -> str:
    return str(factor(int(n)))


def module_dimension(module) -> int:
    for name in ("dimension", "rank"):
        if hasattr(module, name):
            return int(getattr(module, name)())
    raise RuntimeError(f"cannot determine dimension for {module!r}")


def cuspidal_module(module):
    for name in ("cuspidal_submodule", "cuspidal_subspace"):
        if hasattr(module, name):
            return getattr(module, name)()
    return module


def try_new_module(module) -> tuple[Any, str, str | None]:
    """Return (module, method_label, error_if_any)."""
    errors: list[str] = []
    cusp = cuspidal_module(module)
    for obj_label, obj in (("cuspidal", cusp), ("ambient", module)):
        for name in ("new_submodule", "new_subspace"):
            if hasattr(obj, name):
                try:
                    return getattr(obj, name)(), f"{obj_label}.{name}", None
                except Exception as exc:  # noqa: BLE001 - diagnostic
                    errors.append(f"{obj_label}.{name}: {type(exc).__name__}: {exc}")
    return cusp, "cuspidal_fallback_no_new_method", "; ".join(errors) if errors else None


def hecke_matrix(module, p: int):
    if hasattr(module, "hecke_matrix"):
        return module.hecke_matrix(p)
    if hasattr(module, "hecke_operator"):
        return module.hecke_operator(p).matrix()
    raise RuntimeError("no Hecke matrix/operator method")


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


def good_primes(limit_count: int) -> list[int]:
    primes = []
    for p in prime_range(2, 10000):
        p = int(p)
        if N % p == 0 or p == Q:
            continue
        primes.append(p)
        if len(primes) >= limit_count:
            return primes
    return primes


def eigenspace_scan(level: int, mode: str, prime_count: int) -> dict[str, Any]:
    start = time.perf_counter()
    F = GF(Q)
    E = reyssat_curve(mode)
    primes = good_primes(prime_count)
    M0 = ModularSymbols(Gamma0(level), WEIGHT, sign=1, base_ring=F)
    ambient_dim = module_dimension(M0)
    M, new_method, new_error = try_new_module(M0)
    dim = module_dimension(M)
    V = F**dim
    current = V
    trace = []

    for p in primes:
        before = int(current.dimension())
        A = hecke_matrix(M, p)
        aq = F(int(E.ap(p)))
        K = (A - aq).right_kernel()
        current = current.intersection(K)
        after = int(current.dimension())
        trace.append({"p": p, "a_p_mod_q": int(aq), "before": before, "kernel_dim": int(K.dimension()), "after": after})
        if after == 0:
            break

    elapsed = time.perf_counter() - start
    return {
        "level": level,
        "level_factor": factor_string(level),
        "mode": mode,
        "q": Q,
        "prime_count_requested": prime_count,
        "primes_used": [row["p"] for row in trace],
        "status": "ok",
        "elapsed_seconds": elapsed,
        "ambient_sign_plus_dimension": ambient_dim,
        "module_method": new_method,
        "module_method_error": new_error,
        "module_dimension": dim,
        "surviving_dimension": int(current.dimension()),
        "survives_all_used_primes": int(current.dimension()) > 0 and len(trace) == len(primes),
        "trace": trace,
    }


def run_worker(args: argparse.Namespace) -> None:
    result = eigenspace_scan(args.level, args.mode, args.prime_count)
    print(json.dumps(result, ensure_ascii=False))


def run_manager(args: argparse.Namespace) -> None:
    levels = [int(x) for x in args.levels.split(",") if x.strip()]
    rows = []
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
                "--prime-count",
                str(args.prime_count),
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

    survivors = [row for row in rows if row.get("status") == "ok" and row.get("surviving_dimension", 0) > 0]
    payload = {
        "date": DATE,
        "purpose": "Targeted old-level GF(3863) Hecke eigenspace scan for the Reyssat residual trace system.",
        "guardrail": "Diagnostic finite-prime scan with per-level subprocess timeout; not a full Sturm proof.",
        "q": Q,
        "levels": levels,
        "prime_count": args.prime_count,
        "timeout_seconds_per_worker": args.timeout_seconds,
        "summary": {
            "worker_count": len(rows),
            "ok_count": sum(1 for row in rows if row.get("status") == "ok"),
            "timeout_count": sum(1 for row in rows if row.get("status") == "timeout"),
            "error_count": sum(1 for row in rows if row.get("status") == "error"),
            "survivor_count": len(survivors),
            "survivors": [
                {
                    "level": row["level"],
                    "mode": row["mode"],
                    "module_dimension": row.get("module_dimension"),
                    "surviving_dimension": row.get("surviving_dimension"),
                    "primes_used": row.get("primes_used"),
                    "module_method": row.get("module_method"),
                }
                for row in survivors
            ],
        },
        "rows": rows,
    }
    JSON_OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(JSON_OUT)
    print(json.dumps(payload["summary"], indent=2, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--level", type=int)
    parser.add_argument("--mode", choices=["raw", "anc"], default="raw")
    parser.add_argument("--levels", default=",".join(str(x) for x in DEFAULT_LEVELS))
    parser.add_argument("--prime-count", type=int, default=DEFAULT_PRIME_COUNT)
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
