#!/usr/bin/env python3
"""Sage profile for the p=2 parity class in Manin-symbol coordinates.

This script reconstructs the same fixed GF(3863) two-term quotient classes as
the S5 repair run, maps quotient columns back to representative Manin symbols,
and profiles the unique pre-T7 parity vector exported by
``mstar_s5_p2_cokernel_from_witness.py``.

Run inside a Sage Python environment, for example:

    micromamba run -p /root/sage-env python _scripts/mstar_s5_p2_parity_class_manin_profile.py \
      --input-json _results/mstar_s5_p2_cokernel_from_witness_60168_raw_2026-05-13.json \
      --out-json _results/mstar_s5_p2_parity_class_manin_profile_60168_raw_2026-05-13.json \
      --out-md _results/mstar_s5_p2_parity_class_manin_profile_60168_raw_2026-05-13.md
"""

from __future__ import annotations

import argparse
import collections
import json
import math
from pathlib import Path
from typing import Any


def counter_dict(counter: collections.Counter[Any], limit: int | None = None) -> list[dict[str, Any]]:
    items = counter.most_common(limit)
    return [{"key": str(key), "count": int(count)} for key, count in items]


def symbol_tuple_from_raw(raw_symbol: Any) -> tuple[int, int]:
    raw = tuple(int(x) for x in raw_symbol)
    if len(raw) >= 3:
        return raw[-2], raw[-1]
    if len(raw) == 2:
        return raw[0], raw[1]
    raise ValueError(f"unexpected Manin symbol tuple: {raw!r}")


class WeightedUnionFind:
    """Union-find for two-term relations over F_q.

    The invariant is ``x_i = weight[i] * x_parent[i]`` after path compression.
    A relation ``a*x_i + b*x_j = 0`` identifies components up to the scalar
    forced by the relation.  Contradictory same-component relations mark the
    whole component as zero.
    """

    def __init__(self, size: int, q: int):
        self.parent = list(range(size))
        self.weight = [1] * size
        self.zero = [False] * size
        self.q = int(q)

    def inv(self, value: int) -> int:
        return pow(value % self.q, -1, self.q)

    def find(self, item: int) -> tuple[int, int]:
        parent = self.parent[item]
        if parent == item:
            return item, 1
        root, root_weight = self.find(parent)
        self.weight[item] = (self.weight[item] * root_weight) % self.q
        self.parent[item] = root
        return root, self.weight[item]

    def mark_zero(self, item: int) -> None:
        root, _ = self.find(item)
        self.zero[root] = True

    def union_relation(self, i: int, a: int, j: int, b: int) -> None:
        q = self.q
        a %= q
        b %= q
        if a == 0 and b == 0:
            return
        if a == 0:
            self.mark_zero(j)
            return
        if b == 0:
            self.mark_zero(i)
            return

        root_i, weight_i = self.find(i)
        root_j, weight_j = self.find(j)
        if root_i == root_j:
            if (a * weight_i + b * weight_j) % q != 0:
                self.zero[root_i] = True
            return

        # a*(weight_i*root_i) + b*(weight_j*root_j) = 0,
        # hence root_i = factor * root_j.
        factor = (-b * weight_j * self.inv(a * weight_i)) % q

        # Choose the smallest symbol index as canonical representative.  This
        # preserves the first-seen quotient column order used by the existing
        # row witnesses, while representatives may differ by a nonzero scalar
        # from Sage's sparse_2term_quotient representatives.
        if root_i < root_j:
            self.parent[root_j] = root_i
            self.weight[root_j] = self.inv(factor)
            self.zero[root_i] = self.zero[root_i] or self.zero[root_j]
        else:
            self.parent[root_i] = root_j
            self.weight[root_i] = factor
            self.zero[root_j] = self.zero[root_i] or self.zero[root_j]


def build_fast_two_term_columns(syms: Any, q: int, sign: int, mod_s_relations: Any, mod_i_relations: Any) -> dict[int, int]:
    nsyms = len(syms)
    uf = WeightedUnionFind(nsyms, q)
    relations = list(mod_s_relations(syms))
    if sign in (-1, 1):
        relations.extend(list(mod_i_relations(syms, sign)))
    for rel in relations:
        (i, a), (j, b) = rel
        uf.union_relation(int(i), int(a), int(j), int(b))
    for i in range(nsyms):
        uf.find(i)

    rep_to_col: dict[int, int] = {}
    col_to_rep: dict[int, int] = {}
    for i in range(nsyms):
        root, weight = uf.find(i)
        if uf.zero[uf.find(root)[0]] or weight % q == 0:
            continue
        if root not in rep_to_col:
            col = len(rep_to_col)
            rep_to_col[root] = col
            col_to_rep[col] = root
    return col_to_rep


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", type=int, default=60168)
    parser.add_argument("--weight", type=int, default=2)
    parser.add_argument("--q", type=int, default=3863)
    parser.add_argument("--sign", type=int, choices=(-1, 0, 1), default=1)
    parser.add_argument("--input-json", type=Path, required=True)
    parser.add_argument("--sample-limit", type=int, default=80)
    parser.add_argument(
        "--include-modular-symbol-rep",
        action="store_true",
        help="Also call Sage modular_symbol_rep() for samples. This can be slow at large level.",
    )
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    args = parser.parse_args()

    # Sage import order matters on this installation: import sage.all first.
    print("importing Sage modules", flush=True)
    import sage.all  # type: ignore
    from sage.modular.modsym.manin_symbol_list import ManinSymbolList_gamma0  # type: ignore
    from sage.modular.modsym.relation_matrix import modI_relations, modS_relations  # type: ignore

    data = json.loads(args.input_json.read_text(encoding="utf-8"))
    support = [int(col) for col in data["kernel_support"]]
    support_set = set(support)
    t7_support = [int(col) for col in data.get("t7_support_mod2", [])]

    print("building ManinSymbolList", flush=True)
    syms = ManinSymbolList_gamma0(int(args.level), int(args.weight))
    nsyms = len(syms)
    raw_symbol_list = list(getattr(syms, "_symbol_list"))
    print(f"building fast two-term quotient nsyms={nsyms}", flush=True)
    col_to_rep = build_fast_two_term_columns(syms, int(args.q), int(args.sign), modS_relations, modI_relations)

    ncols = len(col_to_rep)
    if ncols != int(data["ncols"]):
        raise RuntimeError(f"column mismatch: quotient has {ncols}, input has {data['ncols']}")

    support_gcd_u: collections.Counter[int] = collections.Counter()
    support_gcd_v: collections.Counter[int] = collections.Counter()
    complement_gcd_u: collections.Counter[int] = collections.Counter()
    complement_gcd_v: collections.Counter[int] = collections.Counter()
    support_u_mod_24: collections.Counter[int] = collections.Counter()
    support_v_mod_24: collections.Counter[int] = collections.Counter()
    support_rep_index_parity: collections.Counter[int] = collections.Counter()
    complement_rep_index_parity: collections.Counter[int] = collections.Counter()
    rule_mismatch_count = 0
    rule_mismatches: list[dict[str, Any]] = []

    samples: list[dict[str, Any]] = []
    t7_columns: list[dict[str, Any]] = []

    print(f"profiling ncols={ncols}", flush=True)
    for col in range(ncols):
        rep = int(col_to_rep[col])
        raw_symbol = raw_symbol_list[rep]
        u, v = symbol_tuple_from_raw(raw_symbol)
        symbol_text = f"({u},{v})"
        in_support = col in support_set
        gcd_u = math.gcd(u, int(args.level))
        rule_prediction = (v % 2 == 0) or (gcd_u % 2 == 0) or (gcd_u % 109 == 0)
        if rule_prediction != in_support:
            rule_mismatch_count += 1
            if len(rule_mismatches) < 25:
                rule_mismatches.append(
                    {
                        "col": col,
                        "rep": rep,
                        "u": u,
                        "v": v,
                        "gcd_u_level": gcd_u,
                        "predicted": rule_prediction,
                        "actual": in_support,
                    }
                )
        if in_support:
            support_gcd_u[gcd_u] += 1
            support_gcd_v[math.gcd(v, int(args.level))] += 1
            support_u_mod_24[u % 24] += 1
            support_v_mod_24[v % 24] += 1
            support_rep_index_parity[rep % 2] += 1
            if len(samples) < int(args.sample_limit):
                samples.append(
                    {
                        "col": col,
                        "rep": rep,
                        "symbol": symbol_text,
                        "u": u,
                        "v": v,
                        "modular_symbol_rep": str(syms[rep].modular_symbol_rep())
                        if args.include_modular_symbol_rep
                        else None,
                    }
                )
        else:
            complement_gcd_u[gcd_u] += 1
            complement_gcd_v[math.gcd(v, int(args.level))] += 1
            complement_rep_index_parity[rep % 2] += 1
        if col in t7_support:
            t7_columns.append(
                {
                    "col": col,
                    "in_kernel_support": in_support,
                    "rep": rep,
                    "symbol": symbol_text,
                    "u": u,
                    "v": v,
                    "modular_symbol_rep": str(syms[rep].modular_symbol_rep())
                    if args.include_modular_symbol_rep
                    else None,
                }
            )

    payload = {
        "tool": "mstar_s5_p2_parity_class_manin_profile",
        "input_json": str(args.input_json),
        "level": int(args.level),
        "q": int(args.q),
        "sign": int(args.sign),
        "quotient_method": "fast-weighted-union-find-on-S-I-relations",
        "include_modular_symbol_rep": bool(args.include_modular_symbol_rep),
        "representative_note": "canonical representatives are minimum-index class reps; quotient column order matches the fixed witness, representatives may differ by nonzero scalars from sparse_2term_quotient",
        "nsyms": nsyms,
        "ncols": ncols,
        "support_size": len(support),
        "support_density": len(support) / ncols,
        "exact_support_rule": "in_support iff (v is even) or (2 divides gcd(u,N)) or (109 divides gcd(u,N)); equivalently, complement iff v is odd and gcd(u,N) divides 69",
        "exact_support_rule_mismatch_count": rule_mismatch_count,
        "exact_support_rule_mismatch_examples": rule_mismatches,
        "t7_support_mod2": t7_support,
        "t7_columns": t7_columns,
        "support_gcd_u_top": counter_dict(support_gcd_u, 30),
        "support_gcd_v_top": counter_dict(support_gcd_v, 30),
        "complement_gcd_u_top": counter_dict(complement_gcd_u, 30),
        "complement_gcd_v_top": counter_dict(complement_gcd_v, 30),
        "support_u_mod_24": counter_dict(support_u_mod_24),
        "support_v_mod_24": counter_dict(support_v_mod_24),
        "support_rep_index_parity": counter_dict(support_rep_index_parity),
        "complement_rep_index_parity": counter_dict(complement_rep_index_parity),
        "support_samples": samples,
    }
    args.out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# S5 p=2 Parity Class Manin Profile",
        "",
        f"Input: `{args.input_json}`",
        "",
        "## Summary",
        "",
        f"- level: `{args.level}`",
        f"- q: `{args.q}`",
        f"- sign: `{args.sign}`",
        "- quotient method: `fast-weighted-union-find-on-S-I-relations`",
        f"- Manin symbols: `{nsyms}`",
        f"- quotient columns: `{ncols}`",
        f"- support size: `{len(support)}`",
        f"- support density: `{len(support) / ncols:.6f}`",
        "- exact support rule: `support iff v even or 2|gcd(u,N) or 109|gcd(u,N)`",
        f"- support rule mismatches: `{rule_mismatch_count}`",
        "",
        "## T7 Columns",
        "",
        "| col | in support | rep | symbol | modular symbol |",
        "|---:|---|---:|---|---|",
    ]
    for item in t7_columns:
        lines.append(
            f"| {item['col']} | {item['in_kernel_support']} | {item['rep']} | "
            f"`{item['symbol']}` | `{item['modular_symbol_rep']}` |"
        )
    lines.extend(
        [
            "",
            "## Top gcd(u,N) In Support",
            "",
            "| gcd | count |",
            "|---:|---:|",
        ]
    )
    for item in payload["support_gcd_u_top"][:20]:
        lines.append(f"| {item['key']} | {item['count']} |")
    lines.extend(
        [
            "",
            "## Top gcd(v,N) In Support",
            "",
            "| gcd | count |",
            "|---:|---:|",
        ]
    )
    for item in payload["support_gcd_v_top"][:20]:
        lines.append(f"| {item['key']} | {item['count']} |")
    lines.extend(
        [
            "",
            "## Support Samples",
            "",
            "| col | rep | symbol | modular symbol |",
            "|---:|---:|---|---|",
        ]
    )
    for item in samples:
        lines.append(
            f"| {item['col']} | {item['rep']} | `{item['symbol']}` | "
            f"`{item['modular_symbol_rep']}` |"
        )
    lines.append("")
    args.out_md.write_text("\n".join(lines), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
