#!/usr/bin/env sage -python
"""
Independent FWS-h check on the Phase-3b Frey-Watkins sample.

The earlier metaphor note used h_delta = log|Delta_min|/12 as a Faltings
proxy.  This script separates two nearby but distinct quantities:

  H_delta/log N  = log|Delta_min| / (12 log N)   (Szpiro/discriminant height)
  h_F/log N      = Sage's normalized Faltings height / log N

For abc/Szpiro, H_delta is the direct wall variable.  The normalized
Faltings height adds archimedean terms and should not be silently identified
with H_delta in proof notes.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path

from sage.all import EllipticCurve, RR, log


ROOT = Path(__file__).resolve().parents[1]


def corr(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 2 or len(xs) != len(ys):
        return None
    mx, my = statistics.mean(xs), statistics.mean(ys)
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    if vx == 0 or vy == 0:
        return None
    return float(sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / math.sqrt(vx * vy))


def linreg(xs: list[float], ys: list[float]) -> dict[str, float] | None:
    if len(xs) < 2 or len(xs) != len(ys):
        return None
    mx, my = statistics.mean(xs), statistics.mean(ys)
    vx = sum((x - mx) ** 2 for x in xs)
    if vx == 0:
        return None
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / vx
    intercept = my - slope * mx
    return {"slope": float(slope), "intercept": float(intercept)}


def fmt(x, digits=4) -> str:
    if x is None:
        return "n/a"
    return f"{float(x):.{digits}f}"


def label(row: dict) -> str:
    a, b, c = row["triple"]
    if [a, b, c] == [2, 6436341, 6436343]:
        return "Reyssat (2, 6436341, 6436343)"
    return f"({a}, {b}, {c})"


def summarize(rows: list[dict]) -> dict:
    qs = [r["quality"] for r in rows]
    rhos = [r["rho"] for r in rows]
    hds = [r["h_delta_over_logN"] for r in rows]
    hfs = [r["h_faltings_over_logN"] for r in rows]
    high = [r for r in rows if r["quality"] >= 1.5]
    return {
        "n": len(rows),
        "h_delta_min": min(hds),
        "h_delta_mean": statistics.mean(hds),
        "h_delta_max": max(hds),
        "h_faltings_min": min(hfs),
        "h_faltings_mean": statistics.mean(hfs),
        "h_faltings_max": max(hfs),
        "corr_h_delta_q": corr(hds, qs),
        "corr_h_faltings_q": corr(hfs, qs),
        "corr_rho_q": corr(rhos, qs),
        "reg_h_delta_q": linreg(qs, hds),
        "reg_h_faltings_q": linreg(qs, hfs),
        "high_quality": high,
        "high_quality_n": len(high),
        "top_h_delta": sorted(rows, key=lambda r: -r["h_delta_over_logN"])[:10],
        "top_h_faltings": sorted(rows, key=lambda r: -r["h_faltings_over_logN"])[:10],
        "low_h_faltings": sorted(rows, key=lambda r: r["h_faltings_over_logN"])[:10],
    }


def write_md(path: Path, payload: dict) -> None:
    s = payload["summary"]
    lines = [
        "# FWS-h Phase 3b: Diskriminantenhöhe versus Faltings-Höhe",
        "",
        "Datum: 2026-05-17",
        "Input: `_results/frey_watkins_saturation_phase3b_2026-05-17.json`",
        "Skript: `_scripts/frey_faltings_sandwich_phase3b.py`",
        "",
        "## Wichtige Korrektur",
        "",
        "Die proof-relevante Szpiro-Wand ist nicht die normalisierte Sage-Faltings-Höhe allein,",
        "sondern die Diskriminantenhöhe",
        "",
        "```text",
        "H_delta(E) = log |Delta_min(E)| / 12.",
        "```",
        "",
        "Die echte Faltings-Höhe enthält archimedische Terme. Sie ist eng verwandt,",
        "aber darf in Beweisnotizen nicht still mit `H_delta` identifiziert werden.",
        "",
        "## Kurzbefund",
        "",
        f"- `n = {s['n']}` Frey-Datenpunkte.",
        f"- `corr(H_delta/logN, q) = {fmt(s['corr_h_delta_q'])}`.",
        f"- `corr(h_F/logN, q) = {fmt(s['corr_h_faltings_q'])}`.",
        f"- `corr(rho, q) = {fmt(s['corr_rho_q'])}`.",
        f"- `H_delta/logN` liegt in `{fmt(s['h_delta_min'])} .. {fmt(s['h_delta_max'])}`.",
        f"- `h_F/logN` liegt in `{fmt(s['h_faltings_min'])} .. {fmt(s['h_faltings_max'])}`.",
        "",
        "## Hochqualitätszone `q >= 1.5`",
        "",
        "| Tripel | q | H_delta/logN | h_F/logN | rho |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in s["high_quality"]:
        lines.append(
            f"| {label(row)} | {fmt(row['quality'],3)} | {fmt(row['h_delta_over_logN'],3)} | "
            f"{fmt(row['h_faltings_over_logN'],3)} | {fmt(row['rho'],3)} |"
        )
    lines.extend([
        "",
        "## Höchste Diskriminantenhöhe",
        "",
        "| Rang | Tripel | q | H_delta/logN | h_F/logN | rho |",
        "|---:|---|---:|---:|---:|---:|",
    ])
    for i, row in enumerate(s["top_h_delta"], start=1):
        lines.append(
            f"| {i} | {label(row)} | {fmt(row['quality'],3)} | "
            f"{fmt(row['h_delta_over_logN'],3)} | {fmt(row['h_faltings_over_logN'],3)} | "
            f"{fmt(row['rho'],3)} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "Die User-Metapher landet weiterhin auf dem richtigen Objekt, aber das Objekt",
        "sollte präzise `Szpiro-/Diskriminantenhöhe` heißen. In dieser Form ist die",
        "Korrelation mit `q` deutlich stärker als beim Modulargrad und direkt an die",
        "abc/Szpiro-Wand gekoppelt.",
        "",
        "Die normalisierte Faltings-Höhe bleibt als Arakelov-Variante nützlich, ist",
        "aber für kleine Kurven stark archimedisch verschoben. Für die Backup-Route",
        "sollte daher `FWS-h_delta` die Primärform sein.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-json", default=str(ROOT / "_results" / "frey_watkins_saturation_phase3b_2026-05-17.json"))
    parser.add_argument("--out-json", default=str(ROOT / "_results" / "frey_faltings_sandwich_phase3b_2026-05-17.json"))
    parser.add_argument("--out-md", default=str(ROOT / "_results" / "frey_faltings_sandwich_phase3b_2026-05-17.md"))
    args = parser.parse_args()

    data = json.loads(Path(args.input_json).read_text(encoding="utf-8"))
    rows = []
    for base in data["rows"]:
        if "error" in base:
            continue
        a, b, c = base["triple"]
        E = EllipticCurve([0, b - a, 0, -a * b, 0]).minimal_model()
        N = int(E.conductor())
        logN = float(RR(log(N)))
        delta_min = abs(E.discriminant())
        h_delta = float(RR(log(delta_min) / 12))
        h_faltings = float(RR(E.faltings_height()))
        row = dict(base)
        row.update({
            "minimal_discriminant_abs": int(delta_min),
            "h_delta": h_delta,
            "h_delta_over_logN": h_delta / logN,
            "h_faltings_sage": h_faltings,
            "h_faltings_over_logN": h_faltings / logN,
            "height_difference_hF_minus_Hdelta": h_faltings - h_delta,
        })
        rows.append(row)
    payload = {
        "meta": {
            "script": "_scripts/frey_faltings_sandwich_phase3b.py",
            "date": "2026-05-17",
            "input": args.input_json,
        },
        "summary": summarize(rows),
        "rows": rows,
    }
    Path(args.out_json).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    write_md(Path(args.out_md), payload)
    print(json.dumps(payload["summary"], indent=2, ensure_ascii=False, default=str))
    print(f"WROTE {args.out_json}")
    print(f"WROTE {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
