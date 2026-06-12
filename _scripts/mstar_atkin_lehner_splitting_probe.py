#!/usr/bin/env python3
"""Loop 141: Atkin-Lehner splitting probe for the mod-q kernel cascade.

Run with Sage/Python. The script is intentionally a probe, not a replacement
for the restlevel worker: it validates the linear-algebra route on small
levels and can be pointed at one larger level with a hard manager timeout.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from sage.all import GF, Gamma0, Matrix, ModularSymbols, VectorSpace, factor, identity_matrix


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-05-10"
JSON_OUT = ROOT / "_results" / f"mstar_atkin_lehner_splitting_probe_{DATE}.json"
MD_OUT = ROOT / "_results" / f"mstar_atkin_lehner_splitting_probe_{DATE}.md"

Q = 3863
DEFAULT_LEVELS = [109, 218]
DEFAULT_ATKIN_DIVISORS = [109]
DEFAULT_PRIMES = [5, 7, 11, 13]
DEFAULT_TIMEOUT = 300

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


def build_modsym_newspace(level: int, field: Any) -> tuple[Any, dict[str, Any]]:
    module = ModularSymbols(Gamma0(level), 2, sign=0, base_ring=field)
    cuspidal = module.cuspidal_subspace()
    newspace = cuspidal.new_subspace()
    return newspace, {
        "backend": "modsym_gf",
        "ambient_dimension": int(module.dimension()),
        "cuspidal_dimension": int(cuspidal.dimension()),
        "new_dimension": int(newspace.dimension()),
    }


def worker(level: int, mode: str, primes: list[int], atkin_divisors: list[int]) -> dict[str, Any]:
    start = time.perf_counter()
    field = GF(Q)
    newspace, space_info = build_modsym_newspace(level, field)
    new_dim = int(space_info["new_dimension"])
    identity = identity_matrix(field, new_dim)
    hecke_kernels: dict[int, Any] = {}
    hecke_ranks: dict[int, int] = {}
    hecke_timings: dict[int, float] = {}

    atkin_rows: list[dict[str, Any]] = []
    for atkin_divisor in atkin_divisors:
        atkin_start = time.perf_counter()
        atkin_matrix = Matrix(field, newspace.atkin_lehner_operator(atkin_divisor).matrix())
        involution_defect_rank = int((atkin_matrix * atkin_matrix - identity).rank())
        sign_rows: list[dict[str, Any]] = []

        for sign in (1, -1):
            sign_start = time.perf_counter()
            sign_space = (atkin_matrix - field(sign) * identity).right_kernel()
            current = sign_space
            steps: list[dict[str, Any]] = []

            for prime in primes:
                step_start = time.perf_counter()
                if prime not in hecke_kernels:
                    hecke_start = time.perf_counter()
                    hecke = Matrix(field, newspace.hecke_matrix(prime))
                    ap = frey_ap(mode, prime)
                    operator = hecke - field(ap) * identity
                    hecke_kernels[prime] = operator.right_kernel()
                    hecke_ranks[prime] = int(operator.rank())
                    hecke_timings[prime] = time.perf_counter() - hecke_start

                before_dim = int(current.dimension())
                current = current.intersection(hecke_kernels[prime])
                after_dim = int(current.dimension())
                steps.append(
                    {
                        "prime": prime,
                        "a_p": frey_ap(mode, prime),
                        "a_p_mod_q": int(field(frey_ap(mode, prime))),
                        "full_operator_rank": hecke_ranks[prime],
                        "full_operator_nullity": int(new_dim - hecke_ranks[prime]),
                        "sign_kernel_dimension_before": before_dim,
                        "sign_kernel_dimension_after": after_dim,
                        "hecke_build_seconds": hecke_timings[prime],
                        "intersection_seconds": time.perf_counter() - step_start,
                    }
                )
                if current.dimension() == 0:
                    break

            sign_rows.append(
                {
                    "sign": sign,
                    "sign_space_dimension": int(sign_space.dimension()),
                    "steps": steps,
                    "final_kernel_dimension": int(current.dimension()),
                    "killed": int(current.dimension()) == 0,
                    "elapsed_seconds": time.perf_counter() - sign_start,
                }
            )

        atkin_rows.append(
            {
                "atkin_divisor": atkin_divisor,
                "involution_defect_rank": involution_defect_rank,
                "signs": sign_rows,
                "killed_all_signs": all(row["killed"] for row in sign_rows),
                "elapsed_seconds": time.perf_counter() - atkin_start,
            }
        )

    killed_all = all(row["killed_all_signs"] for row in atkin_rows)
    return {
        "level": level,
        "level_factor": factor_string(level),
        "mode": mode,
        "status": "ok",
        "q": Q,
        "tested_primes": primes,
        "atkin_divisors": atkin_divisors,
        **space_info,
        "atkin_rows": atkin_rows,
        "killed_all_atkin_splits": killed_all,
        "elapsed_seconds": time.perf_counter() - start,
    }


def run_worker(args: argparse.Namespace) -> None:
    primes = [int(x) for x in args.primes.split(",") if x.strip()]
    atkin_divisors = [int(x) for x in args.atkin_divisors.split(",") if x.strip()]
    if args.level is None:
        raise SystemExit("--level is required in worker mode")
    print(json.dumps(worker(args.level, args.mode, primes, atkin_divisors), ensure_ascii=False))


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    ok_rows = [row for row in rows if row.get("status") == "ok"]
    survivor_rows = [
        {
            "level": row["level"],
            "mode": row["mode"],
            "new_dimension": row.get("new_dimension"),
            "atkin_divisors": row.get("atkin_divisors"),
            "elapsed_seconds": row.get("elapsed_seconds"),
        }
        for row in ok_rows
        if not row.get("killed_all_atkin_splits")
    ]
    return {
        "worker_count": len(rows),
        "ok_count": len(ok_rows),
        "timeout_count": sum(1 for row in rows if row.get("status") == "timeout"),
        "error_count": sum(1 for row in rows if row.get("status") == "error"),
        "survivor_count": len(survivor_rows),
        "survivors": survivor_rows,
    }


def write_markdown(payload: dict[str, Any]) -> None:
    lines: list[str] = []
    lines.append("# M*: Atkin-Lehner-Splitting-Probe")
    lines.append("")
    lines.append(f"Datum: {payload['date']}")
    lines.append("")
    lines.append("## Zweck")
    lines.append("")
    lines.append(
        "Die Probe bildet im Sage-ModularSymbols-Newspace über "
        "GF(3863) die Atkin-Lehner-Sign-Unterräume und schneidet sie "
        "mit den Kernen der Operatoren T_l-a_l(E)."
    )
    lines.append("")
    lines.append("## Zusammenfassung")
    lines.append("")
    summary = payload["summary"]
    lines.append(f"- Worker: {summary['worker_count']}")
    lines.append(f"- OK: {summary['ok_count']}")
    lines.append(f"- Timeouts: {summary['timeout_count']}")
    lines.append(f"- Fehler: {summary['error_count']}")
    lines.append(f"- Nicht getötete Worker: {summary['survivor_count']}")
    lines.append("")
    lines.append("## Resultate")
    lines.append("")
    lines.append("| Level | Mode | Status | Newdim | Atkin-Divisoren | Befund | Zeit |")
    lines.append("|---:|---|---|---:|---|---|---:|")
    for row in payload["rows"]:
        if row.get("status") != "ok":
            lines.append(
                f"| {row.get('level')} | {row.get('mode')} | {row.get('status')} |  | "
                f"{row.get('atkin_divisors', payload.get('atkin_divisors'))} | "
                f"{row.get('stderr_tail', '')[:80]} |  |"
            )
            continue
        finding = "alle Signräume getötet" if row["killed_all_atkin_splits"] else "Survivor in Signraum"
        lines.append(
            f"| {row['level']} | {row['mode']} | ok | {row['new_dimension']} | "
            f"{','.join(str(x) for x in row['atkin_divisors'])} | {finding} | "
            f"{row['elapsed_seconds']:.3f}s |"
        )
    lines.append("")
    lines.append("## Detail")
    lines.append("")
    for row in payload["rows"]:
        if row.get("status") != "ok":
            continue
        lines.append(f"### Level {row['level']} / {row['mode']}")
        lines.append("")
        for atkin in row["atkin_rows"]:
            lines.append(
                f"- W_{atkin['atkin_divisor']}: "
                f"involution_defect_rank={atkin['involution_defect_rank']}, "
                f"killed_all_signs={atkin['killed_all_signs']}"
            )
            for sign_row in atkin["signs"]:
                first_after = sign_row["steps"][0]["sign_kernel_dimension_after"] if sign_row["steps"] else None
                lines.append(
                    f"  - sign {sign_row['sign']}: dim={sign_row['sign_space_dimension']}, "
                    f"after first Hecke cut={first_after}, "
                    f"final={sign_row['final_kernel_dimension']}"
                )
        lines.append("")
    lines.append("## Schluss")
    lines.append("")
    lines.append(
        "Die kleine API-Probe validiert die Signraum-Route. Sie schließt noch "
        "keinen Restlevel und ersetzt keinen FOG-FC-Beweis; sie liefert aber "
        "den nächsten sinnvollen Workerpfad vor schweren Level-60168-Läufen."
    )
    lines.append("")
    MD_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_payload(args: argparse.Namespace, rows: list[dict[str, Any]]) -> dict[str, Any]:
    payload = {
        "date": DATE,
        "purpose": "Atkin-Lehner sign-space probe for the mod-3863 kernel cascade.",
        "q": Q,
        "levels": [int(x) for x in args.levels.split(",") if x.strip()],
        "primes": [int(x) for x in args.primes.split(",") if x.strip()],
        "atkin_divisors": [int(x) for x in args.atkin_divisors.split(",") if x.strip()],
        "timeout_seconds_per_worker": args.timeout_seconds,
        "summary": summarize_rows(rows),
        "rows": rows,
    }
    JSON_OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(payload)
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
                "--atkin-divisors",
                args.atkin_divisors,
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
    parser.add_argument("--mode", choices=["raw", "anc"], default="raw")
    parser.add_argument("--levels", default=",".join(str(x) for x in DEFAULT_LEVELS))
    parser.add_argument("--primes", default=",".join(str(x) for x in DEFAULT_PRIMES))
    parser.add_argument("--atkin-divisors", default=",".join(str(x) for x in DEFAULT_ATKIN_DIVISORS))
    parser.add_argument("--timeout-seconds", type=int, default=DEFAULT_TIMEOUT)
    args = parser.parse_args()
    if args.worker:
        run_worker(args)
    else:
        run_manager(args)


if __name__ == "__main__":
    main()
