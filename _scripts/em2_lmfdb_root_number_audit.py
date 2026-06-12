"""LMFDB-side root-number audit for EM-2.

This script does not use PARI. It fetches LMFDB JSON pages for one curve per
isogeny class and computes:

- the product of finite local root numbers from ec_localdata
- the global functional-equation sign using w_infinity = -1 over Q

Run from the project root:
    python _scripts/em2_lmfdb_root_number_audit.py
"""

from __future__ import annotations

import json
import time
import urllib.request
from datetime import date
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
CONTROL_FILE = PROJECT / "_data" / "em1" / "lmfdb_controls_N240672.json"
OUT_JSON = PROJECT / "_results" / f"em2_lmfdb_root_number_audit_{date.today().isoformat()}.json"
OUT_MD = PROJECT / "_results" / f"em2_lmfdb_root_number_audit_{date.today().isoformat()}.md"


def fetch_lmfdb(label: str) -> dict:
    url = f"https://www.lmfdb.org/EllipticCurve/Q/data/{label}?_format=json"
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "abc-em2-root-number-audit/1.0"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        raw = response.read().decode("utf-8")
    if not raw.lstrip().startswith("{"):
        raise RuntimeError(f"LMFDB did not return JSON for {label}: {raw[:120]!r}")
    return json.loads(raw)


def table(data: dict, name: str):
    return data["data"][data["tables"].index(name)]


def audit_label(label: str) -> dict:
    data = fetch_lmfdb(label)
    curve = table(data, "ec_curvedata")[0]
    local = table(data, "ec_localdata")
    finite_product = 1
    local_rows = []
    for item in local:
        root = int(item["root_number"])
        finite_product *= root
        local_rows.append(
            {
                "prime": int(item["prime"]),
                "root_number": root,
                "reduction_type": int(item["reduction_type"]),
                "kodaira_symbol": int(item["kodaira_symbol"]),
                "conductor_valuation": int(item["conductor_valuation"]),
                "discriminant_valuation": int(item["discriminant_valuation"]),
            }
        )
    return {
        "label": label,
        "lmfdb_iso": curve["lmfdb_iso"],
        "rank": int(curve["rank"]),
        "analytic_rank": int(curve["analytic_rank"]),
        "sha": curve["sha"],
        "finite_root_product": finite_product,
        "archimedean_root_number": -1,
        "global_root_number": -finite_product,
        "local_data": local_rows,
        "source": f"https://www.lmfdb.org/EllipticCurve/Q/data/{label}?_format=json",
    }


def one_label_per_isogeny_class() -> list[str]:
    controls = json.loads(CONTROL_FILE.read_text(encoding="utf-8"))
    labels = []
    seen = set()
    for curve in controls["curves"]:
        label = curve["label"]
        iso = ".".join(label.split(".")[:2])
        if iso in seen:
            continue
        seen.add(iso)
        labels.append(label)
    return labels


def write_markdown(results: list[dict]) -> None:
    lines = [
        "# EM-2 LMFDB Root-Number Audit",
        "",
        f"Date: {date.today().isoformat()}",
        "",
        "Convention: global_root_number = - finite_root_product, using w_infinity = -1 over Q.",
        "",
        "| Label | Isogeny class | Rank | Sha | Finite product | Global sign | Local roots |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for item in results:
        roots = ", ".join(f"p={r['prime']}:{r['root_number']:+d}" for r in item["local_data"])
        lines.append(
            f"| {item['label']} | {item['lmfdb_iso']} | {item['rank']} | {item['sha']} | "
            f"{item['finite_root_product']:+d} | {item['global_root_number']:+d} | {roots} |"
        )
    lines.append("")
    lines.append("Source: LMFDB JSON data pages listed in the companion JSON file.")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    labels = one_label_per_isogeny_class()
    results = []
    for label in labels:
        results.append(audit_label(label))
        time.sleep(0.1)
    payload = {
        "date": date.today().isoformat(),
        "convention": "global_root_number = archimedean_root_number * finite_root_product, with archimedean_root_number = -1 over Q",
        "labels": labels,
        "results": results,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_markdown(results)
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    for item in results:
        print(
            f"{item['label']}: finite={item['finite_root_product']:+d}, "
            f"global={item['global_root_number']:+d}, rank={item['rank']}"
        )


if __name__ == "__main__":
    main()
