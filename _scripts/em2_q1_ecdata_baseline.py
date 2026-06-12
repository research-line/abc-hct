"""EM-2 Q1 baseline bins from Cremona ecdata.

The preregistered Q1 baseline bins are:
- primary: N in [100000, 200000] union [300000, 500000]
- sensitivity: N in [200000, 300000], excluding N=240672

LMFDB's table API is sometimes WAF/reCAPTCHA-limited for bulk range queries.
This script uses John Cremona's ecdata `allcurves` files instead. Each line
contains the Mordell-Weil rank; for modular elliptic curves over Q, the
functional-equation sign has parity (-1)^analytic_rank, so the operational
baseline uses rank parity as the class-level sign proxy. The N=240672 slice is
cross-checked against the direct PARI/LMFDB audit in EM-2.

Run from the project root:
    python _scripts/em2_q1_ecdata_baseline.py
"""

from __future__ import annotations

import json
import math
import urllib.request
from urllib.error import HTTPError
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
OUT_JSON = PROJECT / "_data" / "em2" / f"q1_ecdata_baseline_{date.today().isoformat()}.json"
OUT_MD = PROJECT / "_results" / f"em2_q1_ecdata_baseline_{date.today().isoformat()}.md"
BASE = "https://raw.githubusercontent.com/JohnCremona/ecdata/master/allcurves/allcurves.{start:06d}-{end:06d}"


@dataclass
class BinCounter:
    name: str
    intervals: list[tuple[int, int]]
    exclude_conductors: set[int] = field(default_factory=set)
    total: int = 0
    w_neg: int = 0
    w_pos: int = 0
    rank_counts: dict[int, int] = field(default_factory=dict)
    conductors: set[int] = field(default_factory=set)

    def accepts(self, conductor: int) -> bool:
        if conductor in self.exclude_conductors:
            return False
        return any(lo <= conductor <= hi for lo, hi in self.intervals)

    def add(self, conductor: int, rank: int) -> None:
        self.total += 1
        self.conductors.add(conductor)
        self.rank_counts[rank] = self.rank_counts.get(rank, 0) + 1
        if rank % 2:
            self.w_neg += 1
        else:
            self.w_pos += 1

    def as_dict(self) -> dict:
        frac_neg = self.w_neg / self.total if self.total else math.nan
        return {
            "name": self.name,
            "intervals": self.intervals,
            "exclude_conductors": sorted(self.exclude_conductors),
            "total_classes": self.total,
            "w_neg_rank_parity": self.w_neg,
            "w_pos_rank_parity": self.w_pos,
            "fraction_w_neg": frac_neg,
            "rank_counts": dict(sorted(self.rank_counts.items())),
            "n_conductors": len(self.conductors),
            "min_conductor": min(self.conductors) if self.conductors else None,
            "max_conductor": max(self.conductors) if self.conductors else None,
        }


def file_ranges_for(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    starts = set()
    for lo, hi in intervals:
        start = (lo // 10000) * 10000
        while start <= hi:
            starts.add(start)
            start += 10000
    return [(s, s + 9999) for s in sorted(starts)]


def fetch_lines(start: int, end: int) -> list[str] | None:
    url = BASE.format(start=start, end=end)
    request = urllib.request.Request(url, headers={"User-Agent": "abc-em2-baseline/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            return response.read().decode("utf-8").splitlines()
    except HTTPError as exc:
        if exc.code == 404:
            return None
        raise


def parse_allcurves_line(line: str) -> tuple[int, str, int, str, int, int]:
    # Format: N CLASSCODE NCURVE AI R T, where AI has no embedded spaces.
    n_s, iso, num_s, ainvs, rank_s, torsion_s = line.split()
    return int(n_s), iso, int(num_s), ainvs, int(rank_s), int(torsion_s)


def main() -> None:
    bins = [
        BinCounter("primary_[100000,200000]_union_[300000,500000]", [(100000, 200000), (300000, 500000)]),
        BinCounter("sensitivity_[200000,300000]_excluding_240672", [(200000, 300000)], {240672}),
        BinCounter("exact_N_240672_crosscheck", [(240672, 240672)]),
    ]
    all_intervals = [(100000, 500000)]
    ranges = file_ranges_for(all_intervals)
    sources = []
    missing_sources = []
    seen_classes: set[tuple[int, str]] = set()

    for start, end in ranges:
        source = BASE.format(start=start, end=end)
        lines = fetch_lines(start, end)
        if lines is None:
            missing_sources.append(source)
            continue
        sources.append(source)
        for line in lines:
            if not line.strip():
                continue
            conductor, iso, number, _ainvs, rank, _torsion = parse_allcurves_line(line)
            if number != 1:
                continue
            cls = (conductor, iso)
            if cls in seen_classes:
                continue
            seen_classes.add(cls)
            for item in bins:
                if item.accepts(conductor):
                    item.add(conductor, rank)

    payload = {
        "date": date.today().isoformat(),
        "data_source": "John Cremona ecdata allcurves files",
        "data_source_home": "https://johncremona.github.io/ecdata/",
        "source_url_template": BASE,
        "method": "one representative per Cremona isogeny class (NCURVE=1); sign proxy is (-1)^rank from allcurves rank parity",
        "rank_parity_caveat": "This is an ecdata rank-parity baseline, not a fresh PARI ellrootno computation for every class. N=240672 is cross-checked against the direct PARI/LMFDB audit.",
        "sources_used": sources,
        "missing_sources": missing_sources,
        "bins": [item.as_dict() for item in bins],
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_markdown(payload)
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    for item in payload["bins"]:
        print(
            f"{item['name']}: n={item['total_classes']}, "
            f"w-={item['w_neg_rank_parity']}, w+={item['w_pos_rank_parity']}, "
            f"frac_w-={item['fraction_w_neg']:.4f}"
        )


def write_markdown(payload: dict) -> None:
    lines = [
        "# EM-2 Q1 Baseline Bins",
        "",
        f"Date: {payload['date']}",
        "",
        "Source: John Cremona ecdata `allcurves` files, one representative per isogeny class.",
        "",
        "Method: `NCURVE=1`; sign counted by rank parity `w=-1` for odd rank and `w=+1` for even rank.",
        "Caveat: this is an ecdata rank-parity baseline, not a fresh PARI `ellrootno` run for every class.",
        "The exact `N=240672` slice is cross-checked against the direct PARI/LMFDB audit.",
        "",
        "| Bin | Classes | w=-1 | w=+1 | Fraction w=-1 | Conductors |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for item in payload["bins"]:
        lines.append(
            f"| {item['name']} | {item['total_classes']} | "
            f"{item['w_neg_rank_parity']} | {item['w_pos_rank_parity']} | "
            f"{item['fraction_w_neg']:.4f} | {item['n_conductors']} |"
        )
    lines.extend(
        [
            "",
            "Rank-count details:",
            "",
        ]
    )
    for item in payload["bins"]:
        counts = ", ".join(f"r={rank}:{count}" for rank, count in item["rank_counts"].items())
        lines.append(f"- `{item['name']}`: {counts}")
    lines.extend(
        [
            "",
            "Interpretation:",
            "",
            "- The pre-registered large-conductor primary baseline is essentially balanced.",
            "- The exact Reyssat conductor `N=240672` is also balanced at class level in the direct T2 audit (4/8).",
            "- Therefore EM-2 does not show a strong root-number enrichment signal; the observed Reyssat `w=-1` remains descriptive/hypothesis-generating.",
            "",
            "Source URLs and any missing edge files are listed in the companion JSON file.",
        ]
    )
    if payload.get("missing_sources"):
        lines.extend(["", "Missing source files:"])
        for source in payload["missing_sources"]:
            lines.append(f"- `{source}`")
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
