#!/usr/bin/env sage -python
"""Canonical Sage calibration for the N=109 H3a trace quotient.

Run with:

    sage -python _scripts/mstar_h3a_n109_sage_canonical_probe.py

Unlike the RC3d source-minor probe, this works after Sage's modular-symbol
Manin quotient.  It measures the Smith/Fitting content of canonical trace
operators T_l-a_l on the 9-dimensional sign-plus quotient.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

from sage.all import (  # type: ignore
    Gamma0,
    ModularSymbols,
    QQ,
    ZZ,
    factor,
    identity_matrix,
    matrix,
)


RAW_A = 2
RAW_B = 3**10 * 109


def legendre_symbol_plain(n: int, p: int) -> int:
    n %= p
    if n == 0:
        return 0
    value = pow(n, (p - 1) // 2, p)
    return -1 if value == p - 1 else int(value)


def frey_ap(mode: str, p: int) -> int:
    if mode == "raw":
        a, b = RAW_A, RAW_B
    elif mode == "anc":
        a, b = RAW_B, RAW_A
    else:
        raise ValueError(f"unknown mode {mode!r}")
    total = 0
    for x in range(p):
        total += legendre_symbol_plain(x * (x - a) * (x + b), p)
    return -total


def factor_dict(value: Any) -> dict[str, int]:
    value = abs(ZZ(value))
    if value == 0:
        return {}
    return {str(prime): int(exp) for prime, exp in factor(value)}


def smith_diagonal(mat: Any) -> list[int]:
    smith = mat.change_ring(ZZ).smith_form()[0]
    diagonal: list[int] = []
    for i in range(min(smith.nrows(), smith.ncols())):
        value = abs(ZZ(smith[i, i]))
        if value:
            diagonal.append(int(value))
    return diagonal


def matrix_rows(mat: Any) -> list[list[Any]]:
    return [list(mat.row(i)) for i in range(mat.nrows())]


def integral_trace_operator(module: Any, ell: int, ap: int) -> Any:
    """Return T_ell-a_p on Sage's integral modular-symbol structure."""
    if hasattr(module, "integral_hecke_matrix"):
        hecke = module.integral_hecke_matrix(ell).change_ring(ZZ)
    else:
        hecke = module.hecke_matrix(ell).change_ring(ZZ)
    return hecke - ap * identity_matrix(ZZ, hecke.nrows())


def analyze(level: int, sign: int, mode: str, primes: list[int]) -> dict[str, Any]:
    started = time.perf_counter()
    module = ModularSymbols(Gamma0(level), weight=2, sign=sign, base_ring=QQ)
    dimension = int(module.dimension())
    decomposition = module.decomposition()
    component_data: list[dict[str, Any]] = []
    for index, subspace in enumerate(decomposition):
        trace_data: dict[str, Any] = {}
        for ell in primes:
            mat = subspace.hecke_matrix(ell)
            record: dict[str, Any] = {"charpoly": str(mat.charpoly())}
            if subspace.dimension() == 1:
                record["eigenvalue"] = str(mat[0, 0])
                record["frey_difference"] = str(mat[0, 0] - frey_ap(mode, ell))
            trace_data[str(ell)] = record
        component_data.append(
            {
                "index": index,
                "dimension": int(subspace.dimension()),
                "traces": trace_data,
            }
        )

    intersections: list[dict[str, Any]] = []
    for i, left in enumerate(decomposition):
        for j in range(i + 1, len(decomposition)):
            right = decomposition[j]
            intersections.append(
                {
                    "left": i,
                    "right": j,
                    "intersection_number": int(left.intersection_number(right)),
                }
            )

    factor_vs_complement: list[dict[str, Any]] = []
    for i, subspace in enumerate(decomposition):
        complement = None
        for j, other in enumerate(decomposition):
            if i == j:
                continue
            complement = other if complement is None else complement + other
        factor_vs_complement.append(
            {
                "factor": i,
                "dimension": int(subspace.dimension()),
                "intersection_number": int(subspace.intersection_number(complement)),
            }
        )

    operators: list[dict[str, Any]] = []
    matrices: list[tuple[int, int, Any]] = []

    for ell in primes:
        ap = frey_ap(mode, ell)
        op = integral_trace_operator(module, ell, ap)
        diag = smith_diagonal(op)
        det = ZZ(op.det()) if op.nrows() == op.ncols() else None
        operators.append(
            {
                "prime": int(ell),
                "frey_ap": int(ap),
                "rank_Q": int(op.rank()),
                "shape": [int(op.nrows()), int(op.ncols())],
                "determinant": int(det) if det is not None else None,
                "determinant_factorization": factor_dict(det)
                if det is not None
                else {},
                "smith_diagonal": diag,
                "smith_nonunit": [value for value in diag if value != 1],
            }
        )
        matrices.append((ell, ap, op))

    stacks: list[dict[str, Any]] = []
    for upto in range(1, len(matrices) + 1):
        rows: list[list[Any]] = []
        label: list[str] = []
        for ell, _ap, mat in matrices[:upto]:
            label.append(str(ell))
            rows.extend(matrix_rows(mat))
        stacked = matrix(ZZ, rows)
        diag = smith_diagonal(stacked)
        index = ZZ(1)
        for value in diag:
            index *= ZZ(value)
        stacks.append(
            {
                "label": "+".join(label),
                "rank_Q": int(stacked.rank()),
                "shape": [int(stacked.nrows()), int(stacked.ncols())],
                "smith_diagonal": diag,
                "smith_nonunit": [value for value in diag if value != 1],
                "index": int(index),
                "index_factorization": factor_dict(index),
            }
        )

    return {
        "level": int(level),
        "sign": int(sign),
        "mode": mode,
        "dimension": dimension,
        "primes": [int(p) for p in primes],
        "decomposition_dimensions": [
            int(sub.dimension()) for sub in decomposition
        ],
        "components": component_data,
        "intersections": intersections,
        "factor_vs_complement": factor_vs_complement,
        "operators": operators,
        "stacks": stacks,
        "seconds": time.perf_counter() - started,
    }


def write_markdown(result: dict[str, Any], out_path: Path) -> None:
    lines: list[str] = []
    lines.append(f"# H3a N={result['level']} Sage Canonical Probe")
    lines.append("")
    lines.append(
        f"Level `{result['level']}`, sign `{result['sign']}`, mode `{result['mode']}`, "
        f"dimension `{result['dimension']}`."
    )
    lines.append(f"Decomposition dimensions: `{result['decomposition_dimensions']}`.")
    lines.append("")
    lines.append("## Decomposition Trace Data")
    lines.append("")
    lines.append("| Component | Dimension | Trace data |")
    lines.append("|---:|---:|---|")
    for component in result["components"]:
        lines.append(
            f"| {component['index']} | {component['dimension']} | `{component['traces']}` |"
        )
    lines.append("")
    lines.append("## Intersection Numbers")
    lines.append("")
    lines.append("| Pair | Intersection number |")
    lines.append("|---|---:|")
    for item in result["intersections"]:
        lines.append(
            f"| `{item['left']}-{item['right']}` | {item['intersection_number']} |"
        )
    lines.append("")
    lines.append("| Factor vs complement | Intersection number |")
    lines.append("|---|---:|")
    for item in result["factor_vs_complement"]:
        lines.append(
            f"| `{item['factor']}` | {item['intersection_number']} |"
        )
    lines.append("")
    lines.append("## Individual Operators")
    lines.append("")
    lines.append("| l | a_l(E) | det(T_l-a_l) | factorization | non-unit Smith factors |")
    lines.append("|---:|---:|---:|---|---|")
    for op in result["operators"]:
        lines.append(
            f"| {op['prime']} | {op['frey_ap']} | {op['determinant']} | "
            f"`{op['determinant_factorization']}` | `{op['smith_nonunit']}` |"
        )
    lines.append("")
    lines.append("## Stacked Trace Presentations")
    lines.append("")
    lines.append("| Stack | Shape | Rank | Index | Factorization | non-unit Smith factors |")
    lines.append("|---|---|---:|---:|---|---|")
    for stack in result["stacks"]:
        lines.append(
            f"| `{stack['label']}` | `{stack['shape']}` | {stack['rank_Q']} | "
            f"{stack['index']} | `{stack['index_factorization']}` | "
            f"`{stack['smith_nonunit']}` |"
        )
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    first_stack = result["stacks"][0]
    final_stack = result["stacks"][-1]
    lines.append(
        f"On the canonical {result['dimension']}-dimensional Sage quotient, "
        f"the first trace presentation `{first_stack['label']}` has index "
        f"{first_stack['index']}, while the full tested stack "
        f"`{final_stack['label']}` has index {final_stack['index']} with "
        f"factorization `{final_stack['index_factorization']}`.  This is the "
        "canonical Trace-Fitting datum to compare with H3a-B; arbitrary "
        "source-row minors remain rank certificates and should not be read as "
        "intrinsic congruence modules."
    )
    if result["level"] == 109:
        lines.append(
            "For N=109, the residual index 4 is visibly explained by the "
            "1-dimensional component 1: it has T5=6 and T7=8, hence trace "
            "differences 4 and 8 against the Frey target (2,0)."
        )
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", type=int, default=109)
    parser.add_argument("--sign", type=int, default=1)
    parser.add_argument("--mode", choices=["raw", "anc"], default="raw")
    parser.add_argument("--primes", nargs="*", type=int, default=[5, 7, 11, 13])
    parser.add_argument(
        "--out-json",
        type=Path,
        default=Path("_results/mstar_h3a_n109_sage_canonical_probe_2026-05-16.json"),
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=Path("_results/mstar_h3a_n109_sage_canonical_probe_2026-05-16.md"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = analyze(args.level, args.sign, args.mode, args.primes)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )
    write_markdown(result, args.out_md)
    print(f"wrote {args.out_json}")
    print(f"wrote {args.out_md}")


if __name__ == "__main__":
    main()
