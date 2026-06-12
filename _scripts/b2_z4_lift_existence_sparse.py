#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sparse GF(2) solver for the B2 Z/4 lift test.

This is a faster companion to b2_z4_lift_existence.py.  It solves

    M w = r (mod 2),  r = (M v mod 4) / 2,

where v is the p=2 kernel vector and M is the symmetrically lifted integer
rc3c witness matrix.  If solvable, v + 2w is verified directly modulo 4 on
the original sparse rows.
"""

from __future__ import annotations

import json
import time
from datetime import date
from pathlib import Path

Q = 3863
N = 31680

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "_results" / "rc3c_source_witness_60168_raw_2026-05-12" / "N60168_raw_sign1" / "source_rows.jsonl"
CK = ROOT / "_results" / "mstar_s5_p2_cokernel_from_witness_60168_raw_2026-05-13.json"
OUT_JSON = ROOT / "_results" / f"b2_z4_lift_existence_sparse_{date.today()}.json"
OUT_MD = ROOT / "_results" / f"b2_z4_lift_existence_sparse_{date.today()}.md"


def sym_lift(value: int) -> int:
    return value if value <= Q // 2 else value - Q


def iter_rows(support: set[int]):
    with SRC.open("r", encoding="utf-8") as f:
        for line in f:
            raw = json.loads(line)
            coeff_bits = 0
            dot_mod4 = 0
            row_data = []
            for c, value in raw["row"]:
                value = sym_lift(int(value))
                c = int(c)
                row_data.append((c, value))
                if value & 1:
                    coeff_bits ^= 1 << c
                if c in support:
                    dot_mod4 = (dot_mod4 + value) % 4
            if dot_mod4 % 2:
                raise RuntimeError("S1 failed: Mv is odd modulo 4")
            rhs = dot_mod4 // 2
            yield coeff_bits, rhs, row_data


def solve_gf2(support: set[int]):
    col_mask = (1 << N) - 1
    aug_bit = 1 << N
    basis: dict[int, int] = {}
    rank = 0
    nrows = 0
    rhs_ones = 0
    inconsistent = 0
    t0 = time.time()

    for coeff_bits, rhs, _ in iter_rows(support):
        nrows += 1
        rhs_ones += int(rhs)
        row = coeff_bits | (aug_bit if rhs else 0)

        while row & col_mask:
            pivot = (row & col_mask).bit_length() - 1
            old = basis.get(pivot)
            if old is None:
                basis[pivot] = row
                rank += 1
                break
            row ^= old
        else:
            if row & aug_bit:
                inconsistent += 1

        if nrows % 4000 == 0:
            print(f"rows {nrows} rank {rank} inconsistent {inconsistent} ({time.time() - t0:.1f}s)", flush=True)

    return basis, {
        "nrows": nrows,
        "rank_mod2": rank,
        "kernel_dim_mod2": N - rank,
        "r_ones": rhs_ones,
        "n_inconsistent": inconsistent,
        "z4_lift_exists": inconsistent == 0,
        "solve_seconds": time.time() - t0,
    }


def back_substitute(basis: dict[int, int]) -> int:
    col_mask = (1 << N) - 1
    aug_bit = 1 << N
    solution = 0

    for pivot in sorted(basis):
        row = basis[pivot]
        lower = row & col_mask & ~(1 << pivot)
        parity = (lower & solution).bit_count() & 1
        rhs = 1 if (row & aug_bit) else 0
        if rhs ^ parity:
            solution |= 1 << pivot
    return solution


def verify_lift(support: set[int], w_bits: int):
    value_counts = {0: 0, 1: 0, 2: 0, 3: 0}
    for c in range(N):
        vt = (1 if c in support else 0) + (2 if ((w_bits >> c) & 1) else 0)
        value_counts[vt % 4] += 1

    failures = 0
    max_abs_mod4 = 0
    for _, _, row_data in iter_rows(support):
        total = 0
        for c, value in row_data:
            vt = (1 if c in support else 0) + (2 if ((w_bits >> c) & 1) else 0)
            total = (total + value * vt) % 4
        if total != 0:
            failures += 1
            max_abs_mod4 = max(max_abs_mod4, total)

    return {
        "verification_Mvtilde_mod4_zero": failures == 0,
        "verification_failures": failures,
        "max_residue_mod4": max_abs_mod4,
        "vtilde_value_counts": {str(k): int(v) for k, v in value_counts.items()},
    }


def write_markdown(result: dict):
    exists = "JA" if result["z4_lift_exists"] else "NEIN"
    verified = result.get("verification_Mvtilde_mod4_zero")
    verified_txt = "nicht ausgeführt"
    if verified is not None:
        verified_txt = "JA" if verified else "NEIN"

    lines = [
        f"# B2(m): Z/4-Lift-Existenz, sparse Solver ({date.today()})",
        "",
        "## Ergebnis",
        "",
        f"- Z/4-Lift existiert: **{exists}**",
        f"- Unabhängige Mod-4-Verifikation: **{verified_txt}**",
        f"- Rang über F2: `{result['rank_mod2']}` von `{N}`; Kerndimension `{result['kernel_dim_mod2']}`",
        f"- Rechte Seite r: `{result['r_ones']}` Einsen in `{result['nrows']}` Zeilen",
        f"- Inkonsistente Zeilen: `{result['n_inconsistent']}`",
        f"- Laufzeit Solver: `{result['solve_seconds']:.1f}s`; Gesamt: `{result['total_seconds']:.1f}s`",
        "",
        "## Lesart",
        "",
        "Der Test löst exakt das lineare F2-System `M w = (M v mod 4)/2`.",
        "Bei positivem Ergebnis ist `v + 2w` ein direkt verifizierter Z/4-Kernvektor",
        "des symmetrisch gelifteten rc3c-Witness-Systems. Damit ist die offene",
        "Lift-Komponente des Frustrationsgesetzes nicht mehr nur ein Programm,",
        "sondern für den 60168/raw-Zeugen rechnerisch geschlossen.",
        "",
        f"JSON: `{OUT_JSON.name}`",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    t0 = time.time()
    support = set(json.loads(CK.read_text(encoding="utf-8"))["kernel_support"])
    basis, result = solve_gf2(support)
    if result["z4_lift_exists"]:
        w_bits = back_substitute(basis)
        result.update(verify_lift(support, w_bits))
        import numpy as _np
        _vt = _np.zeros(N, dtype=_np.int8)
        for _c in range(N):
            _vt[_c] = (1 if _c in support else 0) + (2 if ((w_bits >> _c) & 1) else 0)
        _np.save(str(ROOT / "_results" / "b2_z4_lift_vtilde_60168.npy"), _vt)
    result["date"] = str(date.today())
    result["script"] = str(Path(__file__).name)
    result["source_rows"] = str(SRC.relative_to(ROOT))
    result["kernel_source"] = str(CK.relative_to(ROOT))
    result["total_seconds"] = time.time() - t0

    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_markdown(result)
    print(json.dumps(result, indent=2, ensure_ascii=False), flush=True)
    print(f"MD: {OUT_MD}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
