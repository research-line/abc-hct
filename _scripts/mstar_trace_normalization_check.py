#!/usr/bin/env python3
"""Check Frey trace normalization for the M* no-Magma Hecke tests.

The no-Magma quotient uses T_p - a_p(E) for p in {5,7,11,13}.  This script
recomputes those a_p values directly from the Frey model

    E_{a,b}: y^2 = x(x-a)(x+b)

by counting points over finite fields.  It is deliberately independent of the
Manin-symbol quotient code path except for using the same numerical inputs.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path


DATE = "2026-05-12"
RAW_A = 2
RAW_B = 3**10 * 109
DEFAULT_PRIMES = [5, 7, 11, 13]


@dataclass
class TraceRow:
    mode: str
    a: int
    b: int
    p: int
    point_count: int
    ap_by_count: int
    ap_by_legendre_sum: int
    expected_ap: int
    ok: bool


def legendre_symbol(n: int, p: int) -> int:
    n %= p
    if n == 0:
        return 0
    r = pow(n, (p - 1) // 2, p)
    return -1 if r == p - 1 else int(r)


def rhs(a: int, b: int, x: int, p: int) -> int:
    return (x * (x - a) * (x + b)) % p


def point_count(a: int, b: int, p: int) -> int:
    total = 1  # point at infinity
    for x in range(p):
        chi = legendre_symbol(rhs(a, b, x, p), p)
        total += 1 + chi
    return total


def ap_by_legendre(a: int, b: int, p: int) -> int:
    return -sum(legendre_symbol(rhs(a, b, x, p), p) for x in range(p))


def rows_for(primes: list[int]) -> list[TraceRow]:
    expected = {5: 2, 7: 0, 11: 0, 13: -6}
    modes = {
        "raw": (RAW_A, RAW_B),
        "anc": (RAW_B, RAW_A),
    }
    rows: list[TraceRow] = []
    for mode, (a, b) in modes.items():
        for p in primes:
            count = point_count(a, b, p)
            ap_count = p + 1 - count
            ap_legendre = ap_by_legendre(a, b, p)
            exp = expected[p]
            rows.append(
                TraceRow(
                    mode=mode,
                    a=a,
                    b=b,
                    p=p,
                    point_count=count,
                    ap_by_count=ap_count,
                    ap_by_legendre_sum=ap_legendre,
                    expected_ap=exp,
                    ok=(ap_count == ap_legendre == exp),
                )
            )
    return rows


def write_markdown(payload: dict[str, object], path: Path) -> None:
    lines: list[str] = []
    lines.append("# M*: Frey-Trace-Normalisierung")
    lines.append("")
    lines.append(f"Datum: {payload['date']}")
    lines.append("")
    lines.append("## Modell")
    lines.append("")
    lines.append("Geprüft wird das Frey-Modell")
    lines.append("")
    lines.append("$$E_{a,b}: y^2=x(x-a)(x+b).$$")
    lines.append("")
    lines.append("Für gute Primzahlen gilt")
    lines.append("")
    lines.append("$$a_p(E)=p+1-\\#E(\\mathbb F_p)")
    lines.append("=-\\sum_{x\\in\\mathbb F_p}\\left(\\frac{x(x-a)(x+b)}{p}\\right).$$")
    lines.append("")
    lines.append("## Ergebnis")
    lines.append("")
    lines.append("| Mode | a | b | p | #E(F_p) | a_p count | a_p sum | expected | OK |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---|")
    for row in payload["rows"]:  # type: ignore[index]
        mark = "ok" if row["ok"] else "FAIL"
        lines.append(
            f"| {row['mode']} | {row['a']} | {row['b']} | {row['p']} | "
            f"{row['point_count']} | {row['ap_by_count']} | "
            f"{row['ap_by_legendre_sum']} | {row['expected_ap']} | {mark} |"
        )
    lines.append("")
    lines.append("## Schluss")
    lines.append("")
    if payload["all_ok"]:
        lines.append(
            "Die Trace-Normalisierung für die No-Magma-Hecke-Tests ist geschlossen: "
            "raw und anc liefern bei p=5,7,11,13 dieselben Werte "
            "`a_5=2`, `a_7=0`, `a_11=0`, `a_13=-6`."
        )
    else:
        lines.append("Mindestens ein Trace-Wert weicht ab; die Hecke-Tests müssen geprüft werden.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--primes", type=int, nargs="+", default=DEFAULT_PRIMES)
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    args = parser.parse_args()

    rows = rows_for(args.primes)
    payload = {
        "date": DATE,
        "model": "y^2 = x(x-a)(x+b)",
        "rows": [asdict(row) for row in rows],
        "all_ok": all(row.ok for row in rows),
    }
    args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    write_markdown(payload, args.out_md)
    return 0 if payload["all_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
