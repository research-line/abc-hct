#!/usr/bin/env python3
"""Check the P^1 normalizer mirror used in the S5 p=2 handproof skeleton."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import time
from typing import Any


def write_md(payload: dict[str, Any], out_md: Path) -> None:
    lines = [
        "# S5 p=2 P1 Normalizer Mirror Check",
        "",
        "## Summary",
        "",
        f"- level: `{payload['level']}`",
        f"- checked divisor-u representatives: `{payload['checked_divisor_u']}`",
        f"- same-u normalizer hits: `{payload['same_u_hits']}`",
        f"- bad same-u mirrors: `{payload['bad_same_u_mirror_count']}`",
        f"- D-axis representatives in P1List: `{payload['d_axis_p1_count']}`",
        f"- bad D-axis mirrors: `{payload['bad_d_axis_mirror_count']}`",
        "",
        "## Statement Checked",
        "",
        "For every normalized pair `(u,v)` with `u|N` and `u!=0`:",
        "",
        "```text",
        "normalize(-u,v) = (u,w)  =>  w+v ≡ 0 mod N/u.",
        "```",
        "",
        "On the D-axis this is the `same-u` mirror used in the S5-p=2",
        "CRT-/Boundary handproof skeleton.",
        "",
        "## Bad Examples",
        "",
        "```json",
        json.dumps(payload["bad_examples"], indent=2, ensure_ascii=False),
        "```",
        "",
    ]
    out_md.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", type=int, default=60168)
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    args = parser.parse_args()

    started = time.perf_counter()
    import sage.all  # type: ignore  # noqa: F401
    from sage.all import gcd  # type: ignore
    from sage.modular.modsym.p1list import P1List  # type: ignore

    level = int(args.level)
    p1 = P1List(level)

    checked = 0
    same_u_hits = 0
    bad_same_u = 0
    d_axis_count = 0
    bad_d_axis = 0
    bad_examples: list[dict[str, Any]] = []

    for u_raw, v_raw in p1.list():
        u = int(u_raw)
        v = int(v_raw)
        if not u or level % u:
            continue
        checked += 1
        uu_raw, vv_raw = p1.normalize(-u, v)
        uu = int(uu_raw)
        vv = int(vv_raw)
        if uu == u:
            same_u_hits += 1
            modulus = level // u
            if (vv + v) % modulus != 0:
                bad_same_u += 1
                if len(bad_examples) < 20:
                    bad_examples.append(
                        {
                            "source_uv": [u, v],
                            "normalized_minus_u_v": [uu, vv],
                            "modulus": modulus,
                            "mirror_residue": (vv + v) % modulus,
                        }
                    )

        is_d_axis = bool(v % 2 and u == gcd(u, level) and u % 2 and u % 109 == 0)
        if is_d_axis:
            d_axis_count += 1
            modulus = level // u
            if uu != u or (vv + v) % modulus != 0:
                bad_d_axis += 1
                if len(bad_examples) < 20:
                    bad_examples.append(
                        {
                            "source_uv": [u, v],
                            "normalized_minus_u_v": [uu, vv],
                            "modulus": modulus,
                            "d_axis": True,
                        }
                    )

    payload = {
        "tool": "mstar_s5_p1_normalizer_mirror_check",
        "level": level,
        "checked_divisor_u": checked,
        "same_u_hits": same_u_hits,
        "bad_same_u_mirror_count": bad_same_u,
        "d_axis_p1_count": d_axis_count,
        "bad_d_axis_mirror_count": bad_d_axis,
        "bad_examples": bad_examples,
        "seconds_total": time.perf_counter() - started,
    }
    args.out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_md(payload, args.out_md)
    print(f"wrote {args.out_json} and {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

