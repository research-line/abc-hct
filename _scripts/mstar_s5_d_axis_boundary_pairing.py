#!/usr/bin/env python3
"""Check that the S5 D-axis is one half of the P1 mirror-paired boundary axis."""

from __future__ import annotations

import argparse
import collections
import json
import math
from pathlib import Path
import time
from typing import Any


def symbol_tuple_from_raw(raw_symbol: Any) -> tuple[int, int]:
    raw = tuple(int(x) for x in raw_symbol)
    if len(raw) >= 3:
        return raw[-2], raw[-1]
    if len(raw) == 2:
        return raw[0], raw[1]
    raise ValueError(f"unexpected Manin symbol tuple: {raw!r}")


def counter_items(counter: collections.Counter[Any]) -> list[dict[str, Any]]:
    return [{"key": str(key), "count": int(value)} for key, value in counter.most_common()]


def write_md(payload: dict[str, Any], out_md: Path) -> None:
    lines = [
        "# S5 p=2 D-Axis Boundary Pairing",
        "",
        "## Summary",
        "",
        f"- level: `{payload['level']}`",
        f"- P1 D representatives: `{payload['p1_d_representative_count']}`",
        f"- mirror pairs: `{payload['mirror_pair_count']}`",
        f"- quotient D columns: `{payload['quotient_d_column_count']}`",
        f"- quotient hits per mirror pair: `{payload['quotient_hits_per_pair_distribution']}`",
        f"- bad pairs: `{len(payload['bad_pairs'])}`",
        f"- mirror residue failures: `{payload['mirror_residue_failures']}`",
        "",
        "## Statement Checked",
        "",
        "The raw D-axis in `P^1(Z/NZ)` consists of representatives",
        "`u=gcd(u,N)`, `u` odd, `109|u`, `v` odd. The mirror",
        "`normalize(-u,v)` pairs them two by two, and the sparse quotient",
        "selects exactly one representative from each pair.",
        "",
        "This is the boundary-spiegel reading of the 109 correction.",
        "",
        "## Pair u Distribution",
        "",
        "| u | pairs |",
        "|---:|---:|",
    ]
    for item in payload["pair_u_distribution"]:
        lines.append(f"| {item['key']} | {item['count']} |")
    if payload["bad_pairs"]:
        lines.extend(["", "## Bad Pairs", "", "```json"])
        lines.append(json.dumps(payload["bad_pairs"], indent=2, ensure_ascii=False))
        lines.extend(["```", ""])
    out_md.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", type=int, default=60168)
    parser.add_argument("--weight", type=int, default=2)
    parser.add_argument("--sign", type=int, choices=[-1, 0, 1], default=1)
    parser.add_argument("--q", type=int, default=3863)
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    args = parser.parse_args()

    started = time.perf_counter()
    import sage.all  # type: ignore  # noqa: F401
    from sage.all import GF  # type: ignore
    from sage.modular.modsym.manin_symbol_list import ManinSymbolList_gamma0  # type: ignore
    from sage.modular.modsym.p1list import P1List  # type: ignore
    from sage.modular.modsym.relation_matrix import modI_relations, modS_relations, sparse_2term_quotient  # type: ignore

    level = int(args.level)
    field_q = GF(int(args.q))

    syms = ManinSymbolList_gamma0(level, int(args.weight))
    raw_symbol_list = list(getattr(syms, "_symbol_list"))
    rels = set(modS_relations(syms))
    if int(args.sign) in (-1, 1):
        rels.update(modI_relations(syms, int(args.sign)))
    mod = sparse_2term_quotient(rels, len(syms), field_q)

    rep_to_col: dict[int, int] = {}
    col_to_rep: dict[int, int] = {}
    for rep, scalar in mod:
        if scalar == 0:
            continue
        rep_i = int(rep)
        if rep_i not in rep_to_col:
            col = len(rep_to_col)
            rep_to_col[rep_i] = col
            col_to_rep[col] = rep_i

    quotient_d: set[tuple[int, int]] = set()
    quotient_d_u_counter: collections.Counter[int] = collections.Counter()
    for col, rep in col_to_rep.items():
        u, v = symbol_tuple_from_raw(raw_symbol_list[rep])
        gcd_u = math.gcd(u, level)
        if v % 2 and gcd_u % 2 and gcd_u % 109 == 0 and u == gcd_u:
            quotient_d.add((u, v))
            quotient_d_u_counter[u] += 1

    p1 = P1List(level)

    def is_d(pair: tuple[int, int]) -> bool:
        u, v = pair
        return bool(v % 2 and u == math.gcd(u, level) and u % 2 and u % 109 == 0)

    p1_d: set[tuple[int, int]] = set()
    for u_raw, v_raw in p1.list():
        pair = (int(u_raw), int(v_raw))
        if is_d(pair):
            p1_d.add(pair)

    pairs: set[tuple[tuple[int, int], tuple[int, int]]] = set()
    mirror_residue_failures = 0
    bad_pairs: list[dict[str, Any]] = []
    for pair in p1_d:
        u, v = pair
        mirror = tuple(int(x) for x in p1.normalize(-u, v))
        if mirror not in p1_d:
            if len(bad_pairs) < 20:
                bad_pairs.append({"pair": list(pair), "mirror": list(mirror), "reason": "mirror not in p1 D"})
            continue
        if (mirror[1] + v) % (level // u) != 0:
            mirror_residue_failures += 1
        pairs.add(tuple(sorted((pair, mirror))))

    hits_per_pair: collections.Counter[int] = collections.Counter()
    pair_u_counter: collections.Counter[int] = collections.Counter()
    for a, b in pairs:
        hits = int(a in quotient_d) + int(b in quotient_d)
        hits_per_pair[hits] += 1
        pair_u_counter[a[0]] += 1
        if hits != 1 and len(bad_pairs) < 20:
            bad_pairs.append(
                {
                    "pair": [list(a), list(b)],
                    "quotient_hits": hits,
                    "a_in_quotient": a in quotient_d,
                    "b_in_quotient": b in quotient_d,
                }
            )

    payload = {
        "tool": "mstar_s5_d_axis_boundary_pairing",
        "level": level,
        "weight": int(args.weight),
        "sign": int(args.sign),
        "q": int(args.q),
        "p1_d_representative_count": len(p1_d),
        "mirror_pair_count": len(pairs),
        "quotient_d_column_count": len(quotient_d),
        "quotient_d_u_distribution": counter_items(quotient_d_u_counter),
        "quotient_hits_per_pair_distribution": counter_items(hits_per_pair),
        "pair_u_distribution": counter_items(pair_u_counter),
        "mirror_residue_failures": mirror_residue_failures,
        "bad_pairs": bad_pairs,
        "seconds_total": time.perf_counter() - started,
    }
    args.out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_md(payload, args.out_md)
    print(f"wrote {args.out_json} and {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
