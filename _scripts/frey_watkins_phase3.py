#!/usr/bin/env sage -python
"""
Phase 3 of the Frey-Watkins quality-conditional saturation test.

This is an independent Sage run, not a post-processing of the earlier PARI
Phase-3 note.  It builds a deterministic 50-100 point sample of primitive
abc triples, computes Frey conductors and modular degrees, and reports

    rho   = log m(E) / log N(E)
    q     = log c / log rad(abc)
    delta = rho - (q - 1)

with a separate analysis of the high-quality zone q >= 1.5.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import time
from dataclasses import dataclass
from pathlib import Path

from sage.all import EllipticCurve, Integer, QQ, RR


ROOT = Path(__file__).resolve().parents[1]


KNOWN_CONTROLS = [
    # Phase-2 controls and classic abc examples.
    (1, 8, 9),
    (1, 80, 81),
    (3, 125, 128),
    (32, 49, 81),
    (13, 243, 256),
    (5, 27, 32),
    (1, 48, 49),
    (1, 99, 100),
    (1, 288, 289),
    (1, 728, 729),
    (625, 2048, 2673),
    (1, 2400, 2401),
    (1, 5831, 5832),
    (3, 1024, 1027),
    (2, 6436341, 6436343),  # Reyssat: 2 + 3^10*109 = 23^5.
    # Extra stress/control points from the abc-HCT notes.
    (1, 624, 625),
    (9, 16, 25),
    (1, 15624, 15625),
    (1, 143, 144),
    (1, 575, 576),
    (49, 576, 625),
    (1, 168, 169),
    (1, 224, 225),
    (4, 121, 125),
    (27, 32, 59),
    (1, 4374, 4375),
    (4, 729, 733),
    (1, 4095, 4096),
    (1, 1023, 1024),
    (1, 2047, 2048),
    (1, 8191, 8192),
    (1, 323, 324),
    (1, 440, 441),
    (1, 675, 676),
    (3, 4096, 4099),
    (1, 3124, 3125),
    (16, 243, 259),
    (1, 9800, 9801),
    (4, 243, 247),
    (121, 2187, 2308),
    (1, 124, 125),
]


@dataclass(frozen=True)
class TripleCandidate:
    a: int
    b: int
    c: int
    rad: int
    quality: float
    origin: str

    @property
    def key(self) -> tuple[int, int, int]:
        return (self.a, self.b, self.c)


def radical_sieve(limit: int) -> list[int]:
    rad = [1] * (limit + 1)
    is_prime = [True] * (limit + 1)
    if limit >= 0:
        is_prime[0] = False
    if limit >= 1:
        is_prime[1] = False
    for p in range(2, limit + 1):
        if not is_prime[p]:
            continue
        for k in range(p, limit + 1, p):
            rad[k] *= p
            if k > p:
                is_prime[k] = False
    return rad


def canonical(a: int, b: int, c: int) -> tuple[int, int, int]:
    if a > b:
        a, b = b, a
    return int(a), int(b), int(c)


def quality_from_rad(c: int, rad_abc: int) -> float:
    return float(math.log(c) / math.log(rad_abc))


def build_candidate_pool(cmax: int) -> list[TripleCandidate]:
    rad = radical_sieve(cmax)
    candidates: list[TripleCandidate] = []
    for c in range(3, cmax + 1):
        rc = rad[c]
        for a in range(1, c // 2 + 1):
            if math.gcd(a, c) != 1:
                continue
            b = c - a
            rad_abc = rad[a] * rad[b] * rc
            q = quality_from_rad(c, rad_abc)
            candidates.append(TripleCandidate(a, b, c, rad_abc, q, "sieve"))
    return candidates


def add_candidate(
    out: list[TripleCandidate],
    seen: set[tuple[int, int, int]],
    a: int,
    b: int,
    c: int,
    origin: str,
    rad_lookup: list[int] | None = None,
) -> None:
    a, b, c = canonical(a, b, c)
    if a + b != c or math.gcd(a, b) != 1:
        return
    key = (a, b, c)
    if key in seen:
        return
    if rad_lookup is not None and c < len(rad_lookup):
        rad_abc = rad_lookup[a] * rad_lookup[b] * rad_lookup[c]
    else:
        rad_abc = int(Integer(abs(a * b * c)).radical())
    seen.add(key)
    out.append(TripleCandidate(a, b, c, rad_abc, quality_from_rad(c, rad_abc), origin))


def evenly_spaced(items: list[TripleCandidate], count: int) -> list[TripleCandidate]:
    if len(items) <= count:
        return items
    if count <= 1:
        return [items[0]]
    picks = []
    last = len(items) - 1
    for i in range(count):
        picks.append(items[round(i * last / (count - 1))])
    return picks


def select_sample(cmax: int, sample_size: int) -> list[TripleCandidate]:
    pool = build_candidate_pool(cmax)
    rad_lookup = radical_sieve(cmax)
    selected: list[TripleCandidate] = []
    seen: set[tuple[int, int, int]] = set()

    for a, b, c in KNOWN_CONTROLS:
        add_candidate(selected, seen, a, b, c, "control", rad_lookup)

    # Force all high-quality sieve hits into the sample first.
    high_quality = sorted((x for x in pool if x.quality >= 1.5), key=lambda x: (-x.quality, x.c, x.a))
    for x in high_quality:
        add_candidate(selected, seen, x.a, x.b, x.c, "sieve_high_q", rad_lookup)

    # Then take the top-quality front, where FWS-c is most relevant for abc.
    top_quality = sorted(pool, key=lambda x: (-x.quality, x.c, x.a))
    for x in top_quality[: max(20, sample_size // 2)]:
        add_candidate(selected, seen, x.a, x.b, x.c, "sieve_top_q", rad_lookup)

    # Add deterministic strata so the delta minimum is not only searched near high q.
    bins = [
        (0.0, 0.8, 8),
        (0.8, 1.0, 10),
        (1.0, 1.1, 10),
        (1.1, 1.2, 10),
        (1.2, 1.35, 10),
        (1.35, 1.5, 10),
    ]
    for lo, hi, count in bins:
        bucket = [x for x in pool if lo <= x.quality < hi]
        bucket.sort(key=lambda x: (x.c, x.a))
        for x in evenly_spaced(bucket, count):
            add_candidate(selected, seen, x.a, x.b, x.c, f"sieve_bin_{lo:.1f}_{hi:.2f}", rad_lookup)

    # If still short, fill by quality.
    for x in top_quality:
        if len(selected) >= sample_size:
            break
        add_candidate(selected, seen, x.a, x.b, x.c, "sieve_fill_top_q", rad_lookup)

    return selected[:sample_size]


def rational_to_json(x) -> str:
    try:
        return str(QQ(x))
    except Exception:
        return str(x)


def compute_row(candidate: TripleCandidate) -> dict[str, object]:
    a, b, c = candidate.a, candidate.b, candidate.c
    t0 = time.time()
    E = EllipticCurve([0, b - a, 0, -a * b, 0]).minimal_model()
    N = int(E.conductor())
    m = E.modular_degree()
    m_float = float(RR(m))
    rho = float(RR(math.log(m_float) / math.log(N))) if N > 1 and m_float > 0 else None
    delta = rho - (candidate.quality - 1.0) if rho is not None else None
    row = {
        "triple": [a, b, c],
        "origin": candidate.origin,
        "rad_abc": candidate.rad,
        "quality": candidate.quality,
        "N": N,
        "modular_degree": rational_to_json(m),
        "modular_degree_float": m_float,
        "rho": rho,
        "delta": delta,
        "tamagawa_product": int(E.tamagawa_product()),
        "root_number": int(E.root_number()),
        "seconds": round(time.time() - t0, 3),
    }
    return row


def mean(xs: list[float]) -> float | None:
    return float(statistics.mean(xs)) if xs else None


def median(xs: list[float]) -> float | None:
    return float(statistics.median(xs)) if xs else None


def corr(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 2 or len(xs) != len(ys):
        return None
    mx, my = statistics.mean(xs), statistics.mean(ys)
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    if vx == 0 or vy == 0:
        return None
    return float(sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / math.sqrt(vx * vy))


def summarize(rows: list[dict[str, object]]) -> dict[str, object]:
    ok = [r for r in rows if r.get("rho") is not None and r.get("delta") is not None]
    deltas = [float(r["delta"]) for r in ok]
    rhos = [float(r["rho"]) for r in ok]
    qs = [float(r["quality"]) for r in ok]
    log_tamas = [math.log(float(r["tamagawa_product"])) for r in ok if float(r["tamagawa_product"]) > 0]
    rhos_for_tama = [float(r["rho"]) for r in ok if float(r["tamagawa_product"]) > 0]
    high_q = [r for r in ok if float(r["quality"]) >= 1.5]
    high_deltas = [float(r["delta"]) for r in high_q]
    high_rhos = [float(r["rho"]) for r in high_q]
    low_delta = sorted(ok, key=lambda r: float(r["delta"]))[:10]
    high_q_sorted = sorted(high_q, key=lambda r: (-float(r["quality"]), r["triple"]))
    rho_lt_one = [r for r in ok if float(r["rho"]) < 1.0]
    return {
        "n": len(rows),
        "n_ok": len(ok),
        "delta_min": min(deltas) if deltas else None,
        "delta_mean": mean(deltas),
        "delta_median": median(deltas),
        "delta_max": max(deltas) if deltas else None,
        "rho_min": min(rhos) if rhos else None,
        "rho_mean": mean(rhos),
        "rho_max": max(rhos) if rhos else None,
        "quality_min": min(qs) if qs else None,
        "quality_mean": mean(qs),
        "quality_max": max(qs) if qs else None,
        "corr_delta_quality": corr(deltas, qs),
        "corr_rho_quality": corr(rhos, qs),
        "corr_rho_log_tamagawa": corr(rhos_for_tama, log_tamas),
        "rho_lt_one_count": len(rho_lt_one),
        "rho_lt_one": rho_lt_one,
        "low_delta_top10": low_delta,
        "high_quality": {
            "threshold": 1.5,
            "n": len(high_q),
            "delta_min": min(high_deltas) if high_deltas else None,
            "delta_mean": mean(high_deltas),
            "rho_min": min(high_rhos) if high_rhos else None,
            "rho_mean": mean(high_rhos),
            "rows": high_q_sorted,
        },
    }


def fmt_float(x, digits: int = 4) -> str:
    if x is None:
        return "n/a"
    return f"{float(x):.{digits}f}"


def row_label(row: dict[str, object]) -> str:
    a, b, c = row["triple"]
    if [a, b, c] == [2, 6436341, 6436343]:
        return "Reyssat (2, 6436341, 6436343)"
    return f"({a}, {b}, {c})"


def write_markdown(path: Path, payload: dict[str, object]) -> None:
    rows = payload["rows"]
    summary = payload["summary"]
    hq = summary["high_quality"]
    lines = [
        "# Phase-3b-Test der Frey-Watkins-Saturation (eigener Sage-Lauf)",
        "",
        "Datum: 2026-05-17",
        "Skript: `_scripts/frey_watkins_phase3.py`",
        f"Stichprobe: n = {summary['n_ok']} erfolgreich berechnete Frey-Datenpunkte",
        "",
        "## Kurzbefund",
        "",
        f"- `delta_min = {fmt_float(summary['delta_min'], 4)}`.",
        f"- `delta_mean = {fmt_float(summary['delta_mean'], 4)}`.",
        f"- `delta_median = {fmt_float(summary['delta_median'], 4)}`.",
        f"- `rho < 1` tritt {summary['rho_lt_one_count']} mal auf.",
        f"- Korrelation `delta` gegen `q`: `{fmt_float(summary['corr_delta_quality'], 4)}`.",
        f"- Korrelation `rho` gegen `q`: `{fmt_float(summary['corr_rho_quality'], 4)}`.",
        f"- Korrelation `rho` gegen `log(Tamagawa)`: `{fmt_float(summary['corr_rho_log_tamagawa'], 4)}`.",
        "",
        "## Delta-Minimum",
        "",
        "| Rang | Tripel | q | N | m | rho | delta | Tamagawa |",
        "|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for i, row in enumerate(summary["low_delta_top10"], start=1):
        lines.append(
            f"| {i} | {row_label(row)} | {fmt_float(row['quality'], 3)} | "
            f"{row['N']} | {row['modular_degree']} | {fmt_float(row['rho'], 3)} | "
            f"**{fmt_float(row['delta'], 3)}** | {row['tamagawa_product']} |"
        )
    lines.extend([
        "",
        "## Hochqualitätszone `q >= 1.5`",
        "",
        f"Anzahl: {hq['n']}",
        f"Delta-Minimum in der Zone: `{fmt_float(hq['delta_min'], 4)}`",
        f"Mittleres rho in der Zone: `{fmt_float(hq['rho_mean'], 4)}`",
        "",
        "| Tripel | q | N | m | rho | delta | Tamagawa |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ])
    for row in hq["rows"]:
        lines.append(
            f"| {row_label(row)} | {fmt_float(row['quality'], 3)} | {row['N']} | "
            f"{row['modular_degree']} | {fmt_float(row['rho'], 3)} | "
            f"{fmt_float(row['delta'], 3)} | {row['tamagawa_product']} |"
        )
    lines.extend([
        "",
        "## Vollständige Tabelle",
        "",
        "| # | Tripel | Herkunft | rad(abc) | q | N | m | rho | delta | Tamagawa | w(E) |",
        "|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for i, row in enumerate(rows, start=1):
        lines.append(
            f"| {i} | {row_label(row)} | {row['origin']} | {row['rad_abc']} | "
            f"{fmt_float(row['quality'], 3)} | {row['N']} | {row['modular_degree']} | "
            f"{fmt_float(row.get('rho'), 3)} | {fmt_float(row.get('delta'), 3)} | "
            f"{row['tamagawa_product']} | {row['root_number']} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "Dieser Lauf ist ein eigener Sage-Lauf neben der vorhandenen 41er-Notiz.",
        "Er testet dieselbe verfeinerte Hypothese",
        "",
        "```text",
        "rho >= (q - 1) + c_FWS",
        "```",
        "",
        "Der proof-relevante Wert ist das Minimum von `delta = rho-(q-1)`.",
        "Ein negativer oder gegen `0` driftender Wert würde FWS-c schwächen;",
        "ein stabiles positives Minimum hält die Route lebendig.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cmax", type=int, default=5000)
    parser.add_argument("--sample-size", type=int, default=80)
    parser.add_argument("--out-json", default=str(ROOT / "_results" / "frey_watkins_saturation_phase3b_2026-05-17.json"))
    parser.add_argument("--out-md", default=str(ROOT / "_results" / "frey_watkins_saturation_phase3b_2026-05-17.md"))
    parser.add_argument("--checkpoint-jsonl", default=str(ROOT / "_results" / "frey_watkins_saturation_phase3b_2026-05-17.rows.jsonl"))
    args = parser.parse_args()

    t0 = time.time()
    sample = select_sample(args.cmax, args.sample_size)
    rows = []
    checkpoint = Path(args.checkpoint_jsonl)
    checkpoint.parent.mkdir(parents=True, exist_ok=True)
    checkpoint.write_text("", encoding="utf-8")
    for idx, candidate in enumerate(sample, start=1):
        print(f"[{idx:03d}/{len(sample):03d}] {candidate.key} q={candidate.quality:.4f} origin={candidate.origin}", flush=True)
        try:
            row = compute_row(candidate)
        except Exception as exc:
            row = {
                "triple": list(candidate.key),
                "origin": candidate.origin,
                "rad_abc": candidate.rad,
                "quality": candidate.quality,
                "error": repr(exc)[:300],
            }
        rows.append(row)
        with checkpoint.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    payload = {
        "meta": {
            "script": "_scripts/frey_watkins_phase3.py",
            "date": "2026-05-17",
            "cmax": args.cmax,
            "sample_size_requested": args.sample_size,
            "seconds_total": round(time.time() - t0, 3),
        },
        "summary": summarize(rows),
        "rows": rows,
    }
    out_json = Path(args.out_json)
    out_md = Path(args.out_md)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(out_md, payload)
    print(f"WROTE {out_json}")
    print(f"WROTE {out_md}")
    print(json.dumps(payload["summary"], indent=2, ensure_ascii=False, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
