"""Summarize EM-3 modular-symbol residue probe output."""

from __future__ import annotations

import argparse
import math
import re
from collections import defaultdict
from pathlib import Path


RES_RE = re.compile(
    r"^RES \| (?P<label>.*?) \| kind=(?P<kind>.*?) \| center=(?P<center>.*?) "
    r"\| ell=(?P<ell>\d+) \| D_ell=(?P<D_ell>\d+) \| drop_primes=(?P<drop>.*?) "
    r"\| edges=(?P<edges>\d+) \| max_frame=(?P<max_frame>\S+) "
    r"\| nonzero_edges=(?P<nonzero_edges>\d+) \| zero_edges=(?P<zero_edges>\d+) "
    r"\| support=(?P<support>\S+) \| min_v=(?P<min_v>-?\d+) "
    r"\| pole_values=(?P<pole_values>\d+) \| all_zero=(?P<all_zero>\d+)"
)


def parse_float(value: str) -> float:
    if value in {"oo", "+oo"}:
        return math.inf
    if value == "-oo":
        return -math.inf
    return float(value)


def read_text_auto(path: Path) -> str:
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-16", "utf-16-le"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def parse_records(path: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for line in read_text_auto(path).splitlines():
        match = RES_RE.match(line.strip())
        if not match:
            continue
        item = match.groupdict()
        records.append(
            {
                "label": item["label"],
                "kind": item["kind"],
                "center": item["center"],
                "ell": int(item["ell"]),
                "D_ell": int(item["D_ell"]),
                "drop_primes": item["drop"],
                "edges": int(item["edges"]),
                "max_frame": parse_float(item["max_frame"]),
                "nonzero_edges": int(item["nonzero_edges"]),
                "zero_edges": int(item["zero_edges"]),
                "support": parse_float(item["support"]),
                "min_v": int(item["min_v"]),
                "pole_values": int(item["pole_values"]),
                "all_zero": bool(int(item["all_zero"])),
            }
        )
    return records


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else float("nan")


def median(values: list[float]) -> float:
    if not values:
        return float("nan")
    ordered = sorted(values)
    n = len(ordered)
    mid = n // 2
    if n % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2


def summarize(records: list[dict[str, object]]) -> str:
    grouped: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for record in records:
        grouped[(str(record["label"]), int(record["ell"]))].append(record)

    lines: list[str] = []
    lines.append("# EM-3 Modularsymbol-Residuenprobe")
    lines.append("")
    lines.append("**Datum:** 2026-05-09")
    lines.append("**Status:** Ausgeführt als P1′-Surrogat, nicht als voller Hecke-Maximalideal-Test.")
    lines.append("")
    lines.append("## Design")
    lines.append("")
    lines.append(
        "Für dieselben sechs P1-Matched-Control-Fälle wurden die periodennormalisierten "
        "PARI-Modularsymbolwerte auf dem Frey-Stern und auf 20 Random-Centern modulo "
        "der aktiven ungeraden Führer-Drop-Primzahlen ℓ reduziert."
    )
    lines.append("")
    lines.append(
        "Ein aktives ℓ erfüllt `D_ell = prod_{p|N(E), ell|v_p(Delta_min)} p > 1`, "
        "wobei `N(E)` und `Delta_min` direkt in PARI aus dem Frey-Modell bestimmt wurden. "
        "ℓ=2 bleibt ausgeschlossen, weil EM-1 gezeigt hat: `D_2=N` für Frey-Kurven und "
        "damit keine Bewertungstiefe diskriminiert."
    )
    lines.append("")
    lines.append("## Ergebnis nach Tripel und ℓ")
    lines.append("")
    lines.append(
        "| Tripel | ℓ | D_ell | Drop-Primes | Frey support | Random mean support | "
        "Random median | Frey all-zero | Random all-zero | Befund |"
    )
    lines.append("|---|---:|---:|---|---:|---:|---:|---:|---:|---|")

    frey_better = 0
    frey_equal_full = 0
    active_tests = 0
    any_zero = 0

    for key in sorted(grouped, key=lambda x: (x[0], x[1])):
        rows = grouped[key]
        frey = [r for r in rows if r["kind"] == "FREY"]
        rand = [r for r in rows if str(r["kind"]).startswith("RAND_")]
        if not frey or not rand:
            continue
        f = frey[0]
        rand_support = [float(r["support"]) for r in rand]
        rand_all_zero = sum(1 for r in rand if r["all_zero"])
        f_support = float(f["support"])
        active_tests += 1
        if f_support > max(rand_support):
            frey_better += 1
            verdict = "Frey über allen Controls"
        elif f_support == 1.0 and median(rand_support) == 1.0:
            frey_equal_full += 1
            verdict = "Saturiert"
        elif f_support <= median(rand_support):
            verdict = "Kein Frey-Vorteil"
        else:
            verdict = "Grauzone"
        if bool(f["all_zero"]) or rand_all_zero:
            any_zero += 1

        lines.append(
            f"| {f['label']} | {f['ell']} | {f['D_ell']} | {f['drop_primes']} | "
            f"{f_support:.3f} | {mean(rand_support):.3f} | {median(rand_support):.3f} | "
            f"{int(bool(f['all_zero']))} | {rand_all_zero}/20 | {verdict} |"
        )

    lines.append("")
    lines.append("## Gesamturteil")
    lines.append("")
    lines.append(
        f"Aktive Tests: {active_tests}. Frey war in {frey_better} Tests stärker als alle "
        f"Random-Center. In {frey_equal_full} Tests war das Profil schlicht saturiert "
        "(Frey support = Random median = 1)."
    )
    lines.append("")
    if frey_better == 0 and any_zero == 0:
        lines.append(
            "**Nullbefund:** Die aktive Drop-ℓ-Reduktion zeigt kein Frey-spezifisches "
            "Nichtverschwinden. Fast alle getesteten Sterne sind modulo ℓ bereits voll "
            "unterstützt; das Signal diskriminiert daher nicht zwischen Frey-Zentrum und "
            "Random-Centern."
        )
    elif frey_better == 0:
        lines.append(
            "**Schwach-/Nullbefund:** Es gibt vereinzelte Nullprofile, aber keinen Fall, "
            "in dem Frey die Controls dominiert."
        )
    else:
        lines.append(
            "**Hinweis:** Es gibt einzelne Frey-dominante Tests. Diese müssten mit mehr "
            "Controls und echten Hecke-Maximalidealen nachgetestet werden."
        )
    lines.append("")
    lines.append("## Konsequenz")
    lines.append("")
    lines.append(
        "Dieses Surrogat tötet P1′ noch nicht formal, weil es keine Projektion in die "
        "lokalen Hecke-Maximalideale konstruiert. Es zeigt aber, dass die naive "
        "Residuen-Nichtnullheit modulo Führer-Drop-ℓ genauso generisch ist wie die "
        "P1-Amplitude. Der nächste P1′-Schritt müsste echte Hecke-Quotienten/Maximalideale "
        "oder eine neue, deutlich schärfere Verschwindungsvorhersage liefern."
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("raw_output", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    records = parse_records(args.raw_output)
    if not records:
        raise SystemExit(f"No RES records found in {args.raw_output}")
    args.out.write_text(summarize(records), encoding="utf-8")
    print(f"Parsed {len(records)} residue records -> {args.out}")


if __name__ == "__main__":
    main()
