#!/usr/bin/env python3
"""Loop 150: Probe practical open-source alternatives to Magma.

The main non-Magma candidate for the Wiese/Newform handoff is Sage's Brandt
module machinery.  This manager runs small Sage workers through the existing
WSL/micromamba Sage environment and records which cases are viable.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-05-10"
JSON_OUT = ROOT / "_results" / f"mstar_magma_alternatives_probe_{DATE}.json"
MD_OUT = ROOT / "_results" / f"mstar_magma_alternatives_probe_{DATE}.md"

DEFAULT_SAGE_RUN = "/root/.local/micromamba/bin/micromamba run -n sage"
HECKE_PRIMES = [5, 7, 11, 13]


@dataclass(frozen=True)
class Case:
    label: str
    N: int
    M: int
    timeout: int
    note: str


QUICK_CASES = [
    Case("smoke_109", 109, 1, 45, "Known small Frey/base level."),
    Case("smoke_218", 109, 2, 45, "Known small oldlevel smoke."),
    Case(
        "rest_60168_prime_ramified_109",
        109,
        552,
        60,
        "Prime-ramified Brandt model for target oldlevel 60168.",
    ),
    Case(
        "rest_60168_multiramified_ideal",
        7521,
        8,
        30,
        "Ideal multi-ramified presentation 3*23*109 times 2^3, if supported.",
    ),
]

FULL_EXTRA_CASES = [
    Case("rest_60168_prime_ramified_23", 23, 2616, 60, "Alternative prime ramification."),
    Case("rest_60168_prime_ramified_3", 3, 20056, 60, "Alternative prime ramification."),
    Case("rest_80224_prime_ramified_109", 109, 736, 60, "Target oldlevel 80224."),
    Case("rest_80224_prime_ramified_23", 23, 3488, 60, "Target oldlevel 80224."),
    Case("rest_120336_prime_ramified_109", 109, 1104, 60, "Target oldlevel 120336."),
    Case("rest_240672_prime_ramified_109", 109, 2208, 60, "True-new level 240672."),
]


SAGE_WORKER = r"""
from sage.all import *
import json
import os
import time
import traceback

N = Integer(os.environ["BRANDT_N"])
M = Integer(os.environ["BRANDT_M"])
primes = [Integer(x) for x in os.environ["HECKE_PRIMES"].split(",") if x]

result = {
    "N": int(N),
    "M": int(M),
    "level": int(N * M),
    "factor_N": str(factor(N)),
    "factor_M": str(factor(M)),
    "status": "unknown",
    "timings": {},
    "hecke": [],
}

start = time.perf_counter()
try:
    build_start = time.perf_counter()
    B = BrandtModule(N, M)
    result["timings"]["construct_seconds"] = time.perf_counter() - build_start
    result["dimension"] = int(B.dimension())
    result["reported_level"] = str(B.level())
    try:
        result["is_cuspidal"] = bool(B.is_cuspidal())
    except Exception as exc:
        result["is_cuspidal_error"] = f"{type(exc).__name__}: {exc}"

    for n in primes:
        row = {"n": int(n)}
        if gcd(n, N * M) != 1:
            row["status"] = "skip_divides_level"
            result["hecke"].append(row)
            continue
        hstart = time.perf_counter()
        try:
            T = B.hecke_matrix(n, algorithm="direct", sparse=True, B=2)
            row.update(
                {
                    "status": "ok",
                    "seconds": time.perf_counter() - hstart,
                    "nrows": int(T.nrows()),
                    "ncols": int(T.ncols()),
                    "nnz": int(len(T.nonzero_positions())),
                }
            )
        except Exception as exc:
            row.update(
                {
                    "status": "error",
                    "seconds": time.perf_counter() - hstart,
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
        result["hecke"].append(row)
    result["status"] = "ok"
except Exception as exc:
    result["status"] = "error"
    result["error"] = f"{type(exc).__name__}: {exc}"
    result["traceback"] = traceback.format_exc()
finally:
    result["timings"]["total_seconds"] = time.perf_counter() - start
    print("JSON_RESULT " + json.dumps(result, ensure_ascii=False, sort_keys=True), flush=True)
"""


def run_case(case: Case, sage_run: str) -> dict[str, Any]:
    command = (
        f"BRANDT_N={case.N} BRANDT_M={case.M} "
        f"HECKE_PRIMES={','.join(str(x) for x in HECKE_PRIMES)} "
        f"{sage_run} timeout {case.timeout} python -u -"
    )
    started = time.perf_counter()
    proc = subprocess.run(
        ["wsl", "-e", "bash", "-lc", command],
        input=SAGE_WORKER,
        text=True,
        capture_output=True,
        timeout=case.timeout + 45,
    )
    elapsed = time.perf_counter() - started

    row: dict[str, Any] = {
        "label": case.label,
        "N": case.N,
        "M": case.M,
        "level": case.N * case.M,
        "timeout_seconds": case.timeout,
        "note": case.note,
        "returncode": proc.returncode,
        "elapsed_seconds": elapsed,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }
    for line in proc.stdout.splitlines():
        if line.startswith("JSON_RESULT "):
            row["worker_result"] = json.loads(line[len("JSON_RESULT ") :])
            break
    if proc.returncode == 124:
        row["status"] = "timeout"
    elif "worker_result" in row:
        row["status"] = row["worker_result"].get("status", "unknown")
    else:
        row["status"] = "runner_error"
    return row


def write_markdown(payload: dict[str, Any]) -> None:
    lines: list[str] = []
    lines.append("# M*: Magma-Alternativen-Probe")
    lines.append("")
    lines.append(f"Datum: {payload['date']}")
    lines.append("")
    lines.append("## Kurzfazit")
    lines.append("")
    lines.append(
        "Sage-Brandt ist lokal real und läuft auf den Smoke-Levels 109 und 218. "
        "Für das erste harte Restlevel 60168 timeoutet die prime-ramified "
        "Brandt-Konstruktion im Kurzlauf; die mathematisch passendere "
        "multi-ramified Präsentation wird von Sage derzeit nicht implementiert."
    )
    lines.append("")
    lines.append("## Ergebnisse")
    lines.append("")
    lines.append("| Fall | Level | Status | Dimension | Hecke-Befund |")
    lines.append("|---|---:|---|---:|---|")
    for row in payload["rows"]:
        worker = row.get("worker_result") or {}
        dim = worker.get("dimension", "")
        hecke = worker.get("hecke") or []
        hecke_ok = ",".join(f"T{x['n']}" for x in hecke if x.get("status") == "ok")
        if row["status"] == "timeout":
            finding = f"Timeout nach {row['timeout_seconds']}s"
        elif worker.get("status") == "error":
            finding = worker.get("error", "error")
        else:
            finding = hecke_ok or row["status"]
        lines.append(
            f"| `{row['label']}` | {row['level']} | {row['status']} | {dim} | {finding} |"
        )
    lines.append("")
    lines.append("## Konsequenz")
    lines.append("")
    lines.append(
        "Die beste Magma-Alternative ist nicht PARI/GP oder OSCAR, sondern "
        "Sage-Brandt plus zusätzliche Splitting-/Quotientenarbeit. Als direkter "
        "Ersatz für Wiese/Kilford-local-Hecke-Algebras reicht sie lokal noch "
        "nicht: Sage kann multi-ramified Brandt-Module nicht, und die "
        "prime-ramified Darstellung ist für 60168 zu schwer im Kurzlauf."
    )
    lines.append("")
    lines.append(
        "Nächster sinnvoller Nicht-Magma-Schritt: Sage-Brandt nicht verwerfen, "
        "sondern einen kleineren Quotientenpfad bauen: zuerst nur Konstruktion "
        "und Dimension/Ideal-Klassen cachen, dann Heckeoperatoren faktorweise "
        "und mit längeren Läufen auf Mac Studio oder einer größeren Linux-VM."
    )
    lines.append("")
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")


def write_payload(rows: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    payload = {
        "date": DATE,
        "purpose": "Evaluate non-Magma alternatives for M* restlevel Hecke computations.",
        "sage_run": args.sage_run,
        "mode": "full" if args.full else "quick",
        "rows": rows,
        "summary": {
            "ok": sum(1 for row in rows if row["status"] == "ok"),
            "timeout": sum(1 for row in rows if row["status"] == "timeout"),
            "error": sum(1 for row in rows if row["status"] == "error"),
            "runner_error": sum(1 for row in rows if row["status"] == "runner_error"),
        },
    }
    JSON_OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", action="store_true", help="Run extra target-level cases.")
    parser.add_argument("--sage-run", default=DEFAULT_SAGE_RUN)
    args = parser.parse_args()

    cases = list(QUICK_CASES)
    if args.full:
        cases.extend(FULL_EXTRA_CASES)

    rows = []
    for case in cases:
        print(f"[probe] {case.label}: N={case.N} M={case.M} timeout={case.timeout}s", flush=True)
        rows.append(run_case(case, args.sage_run))

    payload = write_payload(rows, args)
    print(json.dumps(payload["summary"], indent=2, ensure_ascii=False))
    print(str(JSON_OUT))
    print(str(MD_OUT))


if __name__ == "__main__":
    main()
