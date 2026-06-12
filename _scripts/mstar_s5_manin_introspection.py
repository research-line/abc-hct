#!/usr/bin/env python3
"""Small Sage introspection for ManinSymbolList objects used by S5."""

from __future__ import annotations

import json
from pathlib import Path


def main() -> int:
    import sage.all  # type: ignore  # noqa: F401
    from sage.modular.modsym.manin_symbol_list import ManinSymbolList_gamma0  # type: ignore

    syms = ManinSymbolList_gamma0(60168, 2)
    sample_indices = [0, 1, 2, 3, 4, 5, 6, 7, 60169, 75211, 95267, 36102, 102788]

    def value(obj: object, name: str) -> object:
        attr = getattr(obj, name)
        return attr() if callable(attr) else attr

    payload = {
        "type_syms": str(type(syms)),
        "len": len(syms),
        "public_syms_methods": [m for m in dir(syms) if not m.startswith("_")],
        "samples": [
            {
                "index": i,
                "repr": repr(syms[i]),
                "str": str(syms[i]),
                "type": str(type(syms[i])),
                "tuple": [int(x) for x in value(syms[i], "tuple")],
                "u": int(value(syms[i], "u")),
                "v": int(value(syms[i], "v")),
                "modular_symbol_rep": str(value(syms[i], "modular_symbol_rep")),
                "public_symbol_methods": [m for m in dir(syms[i]) if not m.startswith("_")],
            }
            for i in sample_indices
        ],
    }
    out = Path("_results/mstar_s5_manin_introspection_2026-05-13.json")
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md = Path("_results/mstar_s5_manin_introspection_2026-05-13.md")
    lines = [
        "# S5 Manin Introspection",
        "",
        f"Type: `{payload['type_syms']}`",
        f"Length: `{payload['len']}`",
        "",
        "## Sample Symbols",
        "",
        "| index | symbol | tuple | u | v | modular_symbol_rep |",
        "|---:|---|---|---:|---:|---|",
    ]
    for sample in payload["samples"]:
        lines.append(
            f"| {sample['index']} | `{sample['str']}` | `{sample['tuple']}` | "
            f"{sample['u']} | {sample['v']} | `{sample['modular_symbol_rep']}` |"
        )
    lines.extend(["", "## Public List Methods", "", "```text"])
    lines.extend(payload["public_syms_methods"])
    lines.extend(["```", ""])
    md.write_text("\n".join(lines), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
