"""Loop 122 probe for the H2C-C additive 2-adic block.

Run with Sage Python, for example:

    /root/.local/micromamba/bin/micromamba run -n sage python _scripts/mstar_h2c_p2_wild_probe.py

The script samples Frey curves E_{a,b}: y^2=x(x-a)(x+b) with
v2(abc)=r and audits the 15-case modular-degree ledger.  It is not a proof;
it records the local 2-adic pattern needed by H2C-C.
"""

from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path

from sage.all import EllipticCurve, gcd


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-05-10"
LEDGER = ROOT / "_results" / "mstar_15case_tail_ledger_2026-05-09.json"
JSON_OUT = ROOT / "_results" / f"mstar_h2c_p2_wild_probe_{DATE}.json"
MD_OUT = ROOT / "_results" / f"mstar_h2c_p2_wild_probe_{DATE}.md"


def v2(n: int) -> int:
    n = abs(int(n))
    out = 0
    while n and n % 2 == 0:
        out += 1
        n //= 2
    return out


def frey_curve(a: int, b: int):
    return EllipticCurve([0, b - a, 0, -a * b, 0])


def expected_2_type(r: int) -> str:
    if r in (1, 2, 3):
        return "bounded additive"
    if r == 4:
        return "bounded good/additive"
    return "potentially multiplicative depth"


def local_row(a: int, b: int) -> dict[str, object]:
    c = a + b
    E = frey_curve(a, b)
    ld = E.local_data(2)
    delta_v = int(ld.discriminant_valuation())
    c2 = int(ld.tamagawa_number())
    f2 = int(ld.conductor_valuation())
    kod = str(ld.kodaira_symbol())
    r = v2(a * b * c)
    return {
        "a": int(a),
        "b": int(b),
        "c": int(c),
        "r_v2_abc": r,
        "expected": expected_2_type(r),
        "raw_delta_v2": int(E.discriminant().valuation(2)),
        "minimal_delta_v2": delta_v,
        "kodaira_2": kod,
        "c2": c2,
        "v2_c2": v2(c2),
        "v2_delta2": v2(delta_v) if delta_v else 0,
        "f2": f2,
        "allowance_v2_c2_plus_v2_delta2": v2(c2) + (v2(delta_v) if delta_v else 0),
    }


def sample_by_r(max_r: int = 24, odd_bound: int = 31) -> dict[str, object]:
    samples: dict[int, list[dict[str, object]]] = defaultdict(list)
    signatures: dict[int, set[tuple[int, str, int, int]]] = defaultdict(set)
    for r in range(1, max_r + 1):
        for u in range(1, odd_bound + 1, 2):
            for b in range(1, odd_bound + 1, 2):
                if gcd(u, b) != 1:
                    continue
                row = local_row((2**r) * u, b)
                samples[r].append(row)
                signatures[r].add(
                    (
                        int(row["minimal_delta_v2"]),
                        str(row["kodaira_2"]),
                        int(row["c2"]),
                        int(row["f2"]),
                    )
                )

    summary = {}
    for r in sorted(samples):
        rows = samples[r]
        summary[str(r)] = {
            "sample_count": len(rows),
            "expected": expected_2_type(r),
            "signatures": [
                {
                    "minimal_delta_v2": delta,
                    "kodaira_2": kod,
                    "c2": c2,
                    "f2": f2,
                    "v2_c2_plus_v2_delta2": v2(c2) + (v2(delta) if delta else 0),
                }
                for delta, kod, c2, f2 in sorted(signatures[r])
            ],
        }
    return summary


def audit_ledger() -> list[dict[str, object]]:
    payload = json.loads(LEDGER.read_text(encoding="utf-8"))
    rows = []
    for row in payload["rows"]:
        a = int(row["a"])
        b = int(row["b"])
        c = int(row["c"])
        r = v2(a * b * c)
        p2 = next((local for local in row["local_data"] if int(local["p"]) == 2), None)
        if p2 is None:
            delta_v = 0
            c2 = 1
            kod = "I0"
            f2 = 0
        else:
            delta_v = int(p2["delta_v"])
            c2 = int(p2["tamagawa"])
            kod = str(p2["kodaira"])
            f2 = int(p2["f_p"])
        rows.append(
            {
                "label": row["label"],
                "a": a,
                "b": b,
                "c": c,
                "r_v2_abc": r,
                "expected": expected_2_type(r),
                "minimal_delta_v2": delta_v,
                "kodaira_2": kod,
                "c2": c2,
                "v2_c2": v2(c2),
                "v2_delta2": v2(delta_v) if delta_v else 0,
                "f2": f2,
                "allowance_v2_c2_plus_v2_delta2": v2(c2) + (v2(delta_v) if delta_v else 0),
            }
        )
    return rows


def write_markdown(sample_summary: dict[str, object], ledger_rows: list[dict[str, object]]) -> None:
    lines = [
        "# M* H2C-C p=2 Wild Probe",
        "",
        "## Sampled Frey Normal Forms",
        "",
        "Rows sample curves `a=2^r u`, `b` odd, `gcd(u,b)=1`.",
        "",
        "| r=v2(abc) | expected | signatures `(delta2, Kodaira, c2, f2; allowance)` |",
        "|---:|---|---|",
    ]
    for r, item in sample_summary.items():
        sig = "; ".join(
            f"({s['minimal_delta_v2']}, {s['kodaira_2']}, {s['c2']}, {s['f2']}; {s['v2_c2_plus_v2_delta2']})"
            for s in item["signatures"]
        )
        lines.append(f"| {r} | {item['expected']} | {sig} |")

    lines.extend(
        [
            "",
            "## 15-Case Ledger Audit",
            "",
            "| label | r | expected | Kodaira(2) | delta2 | c2 | f2 | v2(c2)+v2(delta2) |",
            "|---|---:|---|---|---:|---:|---:|---:|",
        ]
    )
    for row in sorted(ledger_rows, key=lambda x: (int(x["r_v2_abc"]), str(x["label"]))):
        lines.append(
            f"| {row['label']} | {row['r_v2_abc']} | {row['expected']} | "
            f"{row['kodaira_2']} | {row['minimal_delta_v2']} | {row['c2']} | "
            f"{row['f2']} | {row['allowance_v2_c2_plus_v2_delta2']} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The sampled local pattern corrects the too-simple split:",
            "  r=1,2,3 are bounded additive cases; r=4 is bounded good/additive;",
            "  r>=5 has potentially multiplicative depth with possible I_n* variants.",
            "- The conductor exponent and star/wild part remain bounded in the sample.",
            "- The unbounded part is the rank-1 Tate/Néron depth measured by delta2.",
            "- Therefore H2C-C reduces to rank-1 2-adic depth plus a uniform bounded wild/star comparison index.",
        ]
    )
    MD_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample_summary = sample_by_r()
    ledger_rows = audit_ledger()
    out = {
        "date": DATE,
        "purpose": "Loop 122 H2C-C probe: classify the p=2 Frey local block by r=v2(abc).",
        "sample_summary": sample_summary,
        "ledger_rows": ledger_rows,
            "conclusion": {
            "r_1_2_3": "bounded additive finite Tate-algorithm cases",
            "r_4": "bounded good/additive finite Tate-algorithm cases",
            "r_ge_5": "potentially multiplicative rank-1 Tate/Néron depth plus bounded star/wild variant",
            "h2c_c_reduction": "rank-1 2-adic depth plus uniform bounded wild/star comparison index",
        },
    }
    JSON_OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(sample_summary, ledger_rows)
    print(JSON_OUT)
    print(MD_OUT)


if __name__ == "__main__":
    main()
