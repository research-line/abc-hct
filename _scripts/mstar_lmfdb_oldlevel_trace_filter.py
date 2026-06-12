"""Loop 107 LMFDB oldlevel trace filter modulo 3863.

This script uses the public LMFDB API for weight-2 newform orbits and applies
a necessary trace-level test for a Reyssat mod-3863 congruence.

For a degree-d Hecke orbit to have all conjugates congruent to the Frey
eigenvalue a_p(E) modulo a prime above q, its trace must satisfy

    Tr(T_p | orbit) == d * a_p(E) mod q

for every tested good prime p.  This is only a necessary condition, not a full
coefficient-field prime-ideal congruence test.
"""

from __future__ import annotations

import argparse
import json
import math
import time
import urllib.parse
import urllib.request
from decimal import Decimal
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-05-09"
JSON_OUT = ROOT / "_results" / f"mstar_lmfdb_oldlevel_trace_filter_{DATE}.json"
MD_OUT = ROOT / "_results" / f"mstar_lmfdb_oldlevel_trace_filter_{DATE}.md"

LMFDB_API = "https://www.lmfdb.org/api/mf_newforms/"
LMFDB_SQL = {
    "host": "devmirror.lmfdb.xyz",
    "port": 5432,
    "dbname": "lmfdb",
    "user": "lmfdb",
    "password": "lmfdb",
}
Q = 3863
FREY_N = 240672
RAW_A = 2
RAW_B = 3**10 * 109
DEFAULT_LEVELS = [109, 218, 327, 872, 1744, 2507, 3488, 15042, 20056, 40112, 60168, 80224, 120336]
DEFAULT_PRIMES = [5, 7, 11, 13, 17, 19, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]


def factorint(n: int) -> dict[int, int]:
    n = abs(int(n))
    out: dict[int, int] = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            out[d] = out.get(d, 0) + 1
            n //= d
        d += 1 if d == 2 else 2
    if n > 1:
        out[n] = out.get(n, 0) + 1
    return out


def factor_string(n: int) -> str:
    factors = factorint(n)
    if not factors:
        return "1"
    return " * ".join(str(p) if e == 1 else f"{p}^{e}" for p, e in sorted(factors.items()))


def legendre_symbol(n: int, p: int) -> int:
    n %= p
    if n == 0:
        return 0
    val = pow(n, (p - 1) // 2, p)
    return 1 if val == 1 else -1


def frey_ab(mode: str) -> tuple[int, int]:
    if mode == "raw":
        return RAW_A, RAW_B
    if mode == "anc":
        return RAW_B, RAW_A
    raise ValueError(f"unknown mode {mode}")


def frey_ap(mode: str, p: int) -> int:
    a, b = frey_ab(mode)
    total = 0
    for x in range(p):
        total += legendre_symbol(x * (x - a) * (x + b), p)
    return -total


def fetch_json(url: str, timeout_seconds: int) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={"User-Agent": "Codex HCT abc trace filter"})
    with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
        content_type = resp.headers.get("content-type", "")
        if "json" not in content_type:
            sample = resp.read(160).decode("utf-8", errors="replace")
            raise RuntimeError(f"non-json LMFDB response: content_type={content_type!r}, sample={sample!r}")
        return json.load(resp)


def fetch_level_api(level: int, timeout_seconds: int, sleep_seconds: float, max_pages: int) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    pages: list[dict[str, Any]] = []
    offset = 0
    seen_offsets: set[int] = set()
    for page_index in range(max_pages):
        params = {
            "level": level,
            "weight": 2,
            "_format": "json",
            "_offset": offset,
        }
        url = LMFDB_API + "?" + urllib.parse.urlencode(params)
        start = time.perf_counter()
        payload = fetch_json(url, timeout_seconds)
        elapsed = time.perf_counter() - start
        page_rows = payload.get("data", [])
        pages.append(
            {
                "page_index": page_index,
                "url": url,
                "start": payload.get("start"),
                "offset": payload.get("offset"),
                "row_count": len(page_rows),
                "elapsed_seconds": elapsed,
            }
        )
        if not page_rows:
            break
        rows.extend(page_rows)
        reported_start = int(payload.get("start", offset) or 0)
        if reported_start in seen_offsets:
            break
        seen_offsets.add(reported_start)
        offset = reported_start + len(page_rows)
        if sleep_seconds:
            time.sleep(sleep_seconds)
    return {"level": level, "rows": rows, "pages": pages, "source": "api"}


def jsonable(value: Any) -> Any:
    if isinstance(value, Decimal):
        if value == value.to_integral_value():
            return int(value)
        return float(value)
    if isinstance(value, list):
        return [jsonable(item) for item in value]
    if isinstance(value, tuple):
        return [jsonable(item) for item in value]
    return value


def fetch_level_sql(level: int, timeout_seconds: int) -> dict[str, Any]:
    import psycopg

    start = time.perf_counter()
    conn = psycopg.connect(**LMFDB_SQL, connect_timeout=timeout_seconds)
    try:
        with conn.cursor() as cur:
            cur.execute("select count(*) from mf_newforms where level=%s and weight=2", (level,))
            total_count = int(cur.fetchone()[0])
            cur.execute(
                """
                select
                    label, space_label, level, weight, char_order, char_conductor,
                    dim, hecke_orbit, field_poly, traces
                from mf_newforms
                where level=%s and weight=2 and char_order=1 and char_conductor=1
                order by label
                """,
                (level,),
            )
            rows = []
            for row in cur.fetchall():
                rows.append(
                    {
                        "label": row[0],
                        "space_label": row[1],
                        "level": int(row[2]),
                        "weight": int(row[3]),
                        "char_order": int(row[4]),
                        "char_conductor": int(row[5]),
                        "dim": int(row[6]),
                        "hecke_orbit": jsonable(row[7]),
                        "field_poly": jsonable(row[8]),
                        "traces": jsonable(row[9]),
                    }
                )
            cur.execute(
                """
                select label, dim, mf_new_dim, num_forms, hecke_orbit_dims
                from mf_newspaces
                where level=%s and weight=2 and char_order=1 and char_conductor=1
                order by label
                """,
                (level,),
            )
            newspaces = []
            for row in cur.fetchall():
                newspaces.append(
                    {
                        "label": row[0],
                        "dim": int(row[1]),
                        "mf_new_dim": int(row[2]),
                        "num_forms": jsonable(row[3]),
                        "hecke_orbit_dims": jsonable(row[4]),
                    }
                )
    finally:
        conn.close()
    elapsed = time.perf_counter() - start
    return {
        "level": level,
        "rows": rows,
        "pages": [
            {
                "source": "sql_mirror",
                "query": "mf_newforms where level=:level and weight=2 and char_order=1 and char_conductor=1",
                "total_weight2_orbits": total_count,
                "row_count": len(rows),
                "elapsed_seconds": elapsed,
            }
        ],
        "source": "sql",
        "total_weight2_orbits": total_count,
        "newspaces": newspaces,
    }


def fetch_level(args: argparse.Namespace, level: int) -> dict[str, Any]:
    if args.source == "api":
        return fetch_level_api(level, args.timeout_seconds, args.sleep_seconds, args.max_pages)
    if args.source == "sql":
        return fetch_level_sql(level, args.timeout_seconds)
    try:
        return fetch_level_api(level, args.timeout_seconds, args.sleep_seconds, args.max_pages)
    except Exception:
        return fetch_level_sql(level, args.timeout_seconds)


def is_trivial_character(row: dict[str, Any]) -> bool:
    return int(row.get("char_order", 0) or 0) == 1 and int(row.get("char_conductor", 0) or 0) == 1


def test_orbit(row: dict[str, Any], mode: str, primes: list[int]) -> dict[str, Any]:
    level = int(row["level"])
    dim = int(row.get("dim", 0) or 0)
    traces = row.get("traces") or []
    tested: list[dict[str, int]] = []
    skipped: list[int] = []
    missing: list[int] = []
    first_failure: dict[str, int] | None = None

    for p in primes:
        if p == Q or level % p == 0 or FREY_N % p == 0:
            skipped.append(p)
            continue
        if p > len(traces):
            missing.append(p)
            continue
        trace = int(traces[p - 1])
        ap = frey_ap(mode, p)
        expected = (dim * ap) % Q
        observed = trace % Q
        tested.append(
            {
                "p": p,
                "trace": trace,
                "trace_mod_q": observed,
                "frey_ap": ap,
                "dim_times_ap_mod_q": expected,
            }
        )
        if observed != expected:
            first_failure = tested[-1]
            break

    return {
        "label": row.get("label"),
        "space_label": row.get("space_label"),
        "level": level,
        "level_factor": factor_string(level),
        "mode": mode,
        "dim": dim,
        "hecke_orbit": row.get("hecke_orbit"),
        "field_poly": row.get("field_poly"),
        "trace_count_available": len(traces),
        "tested_prime_count": len(tested),
        "tested_primes": [item["p"] for item in tested],
        "skipped_primes": skipped,
        "missing_primes": missing,
        "first_failure": first_failure,
        "passes_trace_filter": first_failure is None and bool(tested),
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    levels = [int(x) for x in args.levels.split(",") if x.strip()]
    primes = [int(x) for x in args.primes.split(",") if x.strip()]

    source_levels: list[dict[str, Any]] = []
    tests: list[dict[str, Any]] = []
    fetch_errors: list[dict[str, Any]] = []

    for level in levels:
        try:
            level_payload = fetch_level(args, level)
        except Exception as exc:  # noqa: BLE001 - diagnostics should keep going
            fetch_errors.append({"level": level, "error": repr(exc)})
            continue

        rows = level_payload["rows"]
        trivial_rows = [row for row in rows if is_trivial_character(row)]
        source_levels.append(
            {
                "level": level,
                "level_factor": factor_string(level),
                "data_source": level_payload.get("source"),
                "total_newform_orbits_returned": level_payload.get("total_weight2_orbits", len(rows)),
                "trivial_newspaces": level_payload.get("newspaces", []),
                "trivial_newspace_dim_sum": sum(int(row.get("dim", 0) or 0) for row in level_payload.get("newspaces", [])),
                "trivial_newspace_num_forms": [
                    row.get("num_forms") for row in level_payload.get("newspaces", [])
                ],
                "trivial_character_orbits": len(trivial_rows),
                "trivial_character_dim_sum": sum(int(row.get("dim", 0) or 0) for row in trivial_rows),
                "pages": level_payload["pages"],
            }
        )
        for row in trivial_rows:
            for mode in ("raw", "anc"):
                tests.append(test_orbit(row, mode, primes))

    survivors = [row for row in tests if row["passes_trace_filter"]]
    by_level = []
    for level in levels:
        level_tests = [row for row in tests if row["level"] == level]
        level_survivors = [row for row in level_tests if row["passes_trace_filter"]]
        source_row = next((row for row in source_levels if row["level"] == level), {})
        newspace_dim = int(source_row.get("trivial_newspace_dim_sum", 0) or 0)
        orbit_dim = int(source_row.get("trivial_character_dim_sum", 0) or 0)
        if orbit_dim:
            coverage = "orbit-traces"
        elif newspace_dim:
            coverage = "newspace-only"
        else:
            coverage = "no-data"
        by_level.append(
            {
                "level": level,
                "level_factor": factor_string(level),
                "newspace_dim": newspace_dim,
                "orbit_dim_loaded": orbit_dim,
                "coverage": coverage,
                "test_count": len(level_tests),
                "survivor_count": len(level_survivors),
                "survivors": [
                    {
                        "label": row["label"],
                        "mode": row["mode"],
                        "dim": row["dim"],
                        "tested_prime_count": row["tested_prime_count"],
                        "tested_primes": row["tested_primes"],
                    }
                    for row in level_survivors
                ],
            }
        )

    return {
        "date": DATE,
        "source": "LMFDB mf_newforms",
        "source_note": "Default source is the public LMFDB read-only PostgreSQL mirror; HTTP API kept as optional fallback.",
        "source_urls": {
            "api": LMFDB_API,
            "access_options": "https://www.lmfdb.org/api/options",
            "sql_host": LMFDB_SQL["host"],
        },
        "purpose": "Loop 107 necessary trace filter for Reyssat mod-3863 congruence against oldlevel newform orbits.",
        "guardrail": "Trace congruence is necessary but not sufficient for coefficient-field prime-ideal congruence.",
        "q": Q,
        "frey_conductor": FREY_N,
        "levels": levels,
        "tested_primes_requested": primes,
        "fetch_errors": fetch_errors,
        "source_levels": source_levels,
        "summary": {
            "level_count_requested": len(levels),
            "level_count_fetched": len(source_levels),
            "fetch_error_count": len(fetch_errors),
            "orbit_mode_tests": len(tests),
            "survivor_count": len(survivors),
            "closed_by_trace_filter_levels": [
                row["level"]
                for row in by_level
                if row["coverage"] == "orbit-traces" and row["survivor_count"] == 0
            ],
            "open_due_to_missing_orbit_data_levels": [
                row["level"] for row in by_level if row["coverage"] == "newspace-only"
            ],
            "survivors": [
                {
                    "level": row["level"],
                    "label": row["label"],
                    "mode": row["mode"],
                    "dim": row["dim"],
                    "tested_prime_count": row["tested_prime_count"],
                    "tested_primes": row["tested_primes"],
                }
                for row in survivors
            ],
            "by_level": by_level,
        },
        "tests": tests,
    }


def write_markdown(payload: dict[str, Any]) -> None:
    lines = [
        "# M* LMFDB Oldlevel Trace Filter",
        "",
        f"Datum: {payload['date']}",
        f"Quelle: `{payload['source']}`",
        "",
        "## Ergebnis",
        "",
        f"- Angefragte Levels: {payload['summary']['level_count_requested']}",
        f"- Geladene Levels: {payload['summary']['level_count_fetched']}",
        f"- Trivial-Charakter-Orbit/Orientierungs-Tests: {payload['summary']['orbit_mode_tests']}",
        f"- Trace-Survivor: {payload['summary']['survivor_count']}",
        "",
        "## Level-Summary",
        "",
        "| Level | Faktor | Newdim | Orbitdim geladen | Abdeckung | Tests | Survivor |",
        "|---:|---:|---:|---:|---|---:|---:|",
    ]
    for row in payload["summary"]["by_level"]:
        lines.append(
            f"| {row['level']} | `{row['level_factor']}` | {row['newspace_dim']} | "
            f"{row['orbit_dim_loaded']} | {row['coverage']} | {row['test_count']} | {row['survivor_count']} |"
        )

    if payload["summary"]["survivors"]:
        lines.extend(["", "## Survivor", ""])
        for row in payload["summary"]["survivors"]:
            lines.append(
                f"- `{row['label']}` ({row['mode']}), dim={row['dim']}, "
                f"tested={row['tested_primes']}"
            )
    else:
        lines.extend(
            [
                "",
                "## Survivor",
                "",
                "Keine. Alle geladenen trivialen Gewicht-2-Newform-Orbits sterben bereits an einem Trace-Test.",
            ]
        )

    if payload["summary"]["open_due_to_missing_orbit_data_levels"]:
        lines.extend(
            [
                "",
                "## Nicht Geschlossen",
                "",
                "Für diese Levels enthält `mf_newspaces` zwar den trivialen Newspace, aber `mf_newforms`",
                "liefert keine Orbit-Dekomposition mit Traces. Sie sind daher durch diesen externen",
                "Trace-Filter nicht geschlossen:",
                "",
                "- "
                + ", ".join(str(level) for level in payload["summary"]["open_due_to_missing_orbit_data_levels"]),
            ]
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Der Test ist nur notwendig: Bei einem Orbit vom Grad `d` müsste für jedes getestete gute `p`",
            "`trace(T_p) ≡ d * a_p(E) (mod 3863)` gelten. Ein Fehlschlag schließt den Orbit als Träger",
            "der gesuchten Reyssat-Kongruenz aus. Ein Survivor wäre dagegen noch kein Beweis, sondern",
            "müsste mit Koeffizientenfeld, Primideal über 3863 und Hecke-Eigenwerten weiter geprüft werden.",
            "",
            "## Fetch-Fehler",
            "",
        ]
    )
    if payload["fetch_errors"]:
        for err in payload["fetch_errors"]:
            lines.append(f"- Level {err['level']}: `{err['error']}`")
    else:
        lines.append("- Keine.")

    MD_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", choices=["sql", "api", "auto"], default="sql")
    parser.add_argument("--levels", default=",".join(str(x) for x in DEFAULT_LEVELS))
    parser.add_argument("--primes", default=",".join(str(x) for x in DEFAULT_PRIMES))
    parser.add_argument("--timeout-seconds", type=int, default=60)
    parser.add_argument("--sleep-seconds", type=float, default=0.2)
    parser.add_argument("--max-pages", type=int, default=20)
    args = parser.parse_args()

    payload = analyze(args)
    JSON_OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(payload)
    print(JSON_OUT)
    print(MD_OUT)
    print(json.dumps(payload["summary"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
