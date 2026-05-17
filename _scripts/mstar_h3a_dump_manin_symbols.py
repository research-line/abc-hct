#!/usr/bin/env python3
"""Dump selected Sage Manin symbols for prefix-structure inspection."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", type=int, required=True)
    parser.add_argument("--weight", type=int, default=2)
    parser.add_argument("--indices", nargs="+", type=int, required=True)
    parser.add_argument("--out-json", type=Path)
    args = parser.parse_args()

    from sage.modular.modsym.manin_symbol_list import ManinSymbolList_gamma0  # type: ignore

    syms = ManinSymbolList_gamma0(args.level, args.weight)
    records = []
    for index in args.indices:
        if index < 0 or index >= len(syms):
            value = None
        else:
            value = repr(syms[index])
        records.append({"index": index, "symbol": value})
    payload = {
        "level": args.level,
        "weight": args.weight,
        "symbol_count": len(syms),
        "records": records,
    }
    text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if args.out_json:
        args.out_json.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
