#!/usr/bin/env python3
"""Budget the matrix-free source-Gram operator for Q_B-3.

The target operator is

    A v = C_source B_AL C_source^T v

where C_source is sparse but A would be dense.  This ledger records why the
large-level verifier should stream/apply the factors instead of materializing A.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-05-23"
DEFAULT_INPUTS = [
    ROOT / "_results" / "mstar_h3a_restline_kernel_quotient_80224_raw_2026-05-17.json",
    ROOT / "_results" / "mstar_h3a_restline_kernel_quotient_80224_anc_2026-05-17.json",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def bytes_to_mib(value: float) -> float:
    return value / (1024.0 * 1024.0)


def analyze(path: Path, fallback_nnz: int | None = None) -> dict[str, Any]:
    data = load_json(path)
    d = int(data["quotient_ncols"])
    n = d - 1
    source_rows = int(data["hecke_rows"])
    source_rank = int(data["quotient_rank"])
    matrix_entries = data.get("matrix_entries")
    nnz_c = int(matrix_entries) if matrix_entries is not None else fallback_nnz
    c_density = None
    if nnz_c is not None and source_rows * d:
        c_density = nnz_c / (source_rows * d)

    dense_a_entries = n * n
    symmetric_a_entries = n * (n + 1) // 2
    return {
        "input_json": str(path.relative_to(ROOT)),
        "level": int(data["level"]),
        "mode": data.get("mode"),
        "q": int(data["q"]),
        "quotient_dim": d,
        "source_rows": source_rows,
        "source_rank": source_rank,
        "rank_A_target": n,
        "C_nnz_estimate": nnz_c,
        "C_density_estimate": c_density,
        "dense_A_entries": dense_a_entries,
        "symmetric_A_entries": symmetric_a_entries,
        "dense_A_uint16_mib": round(bytes_to_mib(dense_a_entries * 2), 3),
        "dense_A_uint32_mib": round(bytes_to_mib(dense_a_entries * 4), 3),
        "dense_A_uint64_mib": round(bytes_to_mib(dense_a_entries * 8), 3),
        "operator_shape": "A = C_source B_AL C_source^T",
        "recommended_verifier": "matrix-free rank certificate for A",
    }


def build_payload(inputs: list[Path]) -> dict[str, Any]:
    raw_nnz = None
    for path in inputs:
        data = load_json(path)
        if data.get("matrix_entries") is not None:
            raw_nnz = int(data["matrix_entries"])
            break
    rows = [analyze(path, fallback_nnz=raw_nnz) for path in inputs]
    return {
        "tool": "qb3_source_gram_operator_budget",
        "date": DATE,
        "rows": rows,
        "recommendation": (
            "Do not materialize A.  Store/project C_source sparsely and implement "
            "the product C_source * (B_AL * (C_source^T v))."
        ),
    }


def fmt_pct(value: float | None) -> str:
    if value is None:
        return "?"
    return f"{100.0 * value:.4f}%"


def write_md(payload: dict[str, Any], out_md: Path) -> None:
    lines = [
        "# Q_B-3 Source-Gram Operator Budget",
        "",
        f"Datum: `{payload['date']}`",
        "",
        "## Empfehlung",
        "",
        payload["recommendation"],
        "",
        "## Fälle",
        "",
        "| Level | Mode | d | rank(A) target | nnz(C) | density(C) | dense A entries | uint64 MiB |",
        "|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in payload["rows"]:
        lines.append(
            "| {level} | {mode} | {d} | {target} | {nnz} | {density} | {a_entries} | {mib} |".format(
                level=row["level"],
                mode=row["mode"],
                d=row["quotient_dim"],
                target=row["rank_A_target"],
                nnz=row["C_nnz_estimate"] if row["C_nnz_estimate"] is not None else "?",
                density=fmt_pct(row["C_density_estimate"]),
                a_entries=row["dense_A_entries"],
                mib=row["dense_A_uint64_mib"],
            )
        )
    lines.extend([
        "",
        "## Operator-Form",
        "",
        "```text",
        "input v in F_q^(d-1)",
        "u = C_source^T v          sparse accumulation",
        "w = B_AL u                Atkin-Lehner pairing application",
        "out = C_source w          sparse row dot products",
        "```",
        "",
        "Der Rangverifier soll also nur Matvecs mit `A` brauchen.  Das ist",
        "genau die Form, in der ein Wiedemann-/Lanczos-artiger finite-field",
        "Rank-Test später angesetzt werden kann.",
        "",
    ])
    out_md.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", nargs="*", type=Path, default=DEFAULT_INPUTS)
    parser.add_argument(
        "--out-json",
        type=Path,
        default=ROOT / "_results" / f"qb3_source_gram_operator_budget_{DATE}.json",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=ROOT / "_results" / f"qb3_source_gram_operator_budget_{DATE}.md",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload([path.resolve() for path in args.inputs])
    args.out_json.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_md(payload, args.out_md)
    print(json.dumps({
        "rows": len(payload["rows"]),
        "recommendation": payload["recommendation"],
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
