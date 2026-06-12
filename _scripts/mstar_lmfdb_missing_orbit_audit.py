"""Loop 108 audit for LMFDB coverage of the remaining oldlevels.

The Loop 107 trace filter closed all oldlevels for which LMFDB provides
trivial-character newform orbit traces.  This script checks whether the three
remaining levels have usable data in adjacent LMFDB tables.
"""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path
from typing import Any

import psycopg


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-05-09"
JSON_OUT = ROOT / "_results" / f"mstar_lmfdb_missing_orbit_audit_{DATE}.json"
MD_OUT = ROOT / "_results" / f"mstar_lmfdb_missing_orbit_audit_{DATE}.md"

LMFDB_SQL = {
    "host": "devmirror.lmfdb.xyz",
    "port": 5432,
    "dbname": "lmfdb",
    "user": "lmfdb",
    "password": "lmfdb",
}
LEVELS = [60168, 80224, 120336]
TEST_PRIMES = [5, 7, 11, 13, 17, 19, 29, 31]


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


def scalar(cur: psycopg.Cursor, sql: str, params: tuple[Any, ...]) -> int:
    cur.execute(sql, params)
    return int(cur.fetchone()[0])


def audit_level(cur: psycopg.Cursor, level: int) -> dict[str, Any]:
    cur.execute(
        """
        select label, dim, mf_new_dim, num_forms, hecke_orbit_dims,
               hecke_orbit_code, trace_bound, trace_display, traces
        from mf_newspaces
        where level=%s and weight=2 and char_order=1 and char_conductor=1
        order by label
        """,
        (level,),
    )
    newspaces = []
    for row in cur.fetchall():
        traces = jsonable(row[8])
        good_prime_traces = {}
        for p in TEST_PRIMES:
            if p <= len(traces):
                good_prime_traces[p] = traces[p - 1]
        newspaces.append(
            {
                "label": row[0],
                "dim": int(row[1]),
                "mf_new_dim": int(row[2]),
                "num_forms": jsonable(row[3]),
                "hecke_orbit_dims": jsonable(row[4]),
                "hecke_orbit_code": jsonable(row[5]),
                "trace_bound": jsonable(row[6]),
                "trace_display": jsonable(row[7]),
                "good_prime_total_traces": good_prime_traces,
            }
        )

    counts = {
        "mf_newforms": scalar(cur, "select count(*) from mf_newforms where level=%s and weight=2", (level,)),
        "mf_newforms_trivial": scalar(
            cur,
            "select count(*) from mf_newforms where level=%s and weight=2 and char_order=1 and char_conductor=1",
            (level,),
        ),
        "mf_hecke_nf": scalar(cur, "select count(*) from mf_hecke_nf where level=%s and weight=2", (level,)),
        "mf_hecke_cc": scalar(cur, "select count(*) from mf_hecke_cc where level=%s and weight=2", (level,)),
    }

    charpoly_counts = []
    for ns in newspaces:
        code = ns["hecke_orbit_code"]
        cur.execute(
            "select p, count(*) from mf_hecke_charpolys where hecke_orbit_code=%s group by p order by p",
            (code,),
        )
        charpoly_counts.append({"label": ns["label"], "hecke_orbit_code": code, "rows_by_p": cur.fetchall()})

    return {
        "level": level,
        "level_factor": factor_string(level),
        "newspaces": newspaces,
        "counts": counts,
        "charpoly_counts": jsonable(charpoly_counts),
        "usable_orbit_data": counts["mf_newforms_trivial"] > 0 or counts["mf_hecke_nf"] > 0,
        "usable_charpoly_data": any(item["rows_by_p"] for item in jsonable(charpoly_counts)),
    }


def main() -> None:
    conn = psycopg.connect(**LMFDB_SQL, connect_timeout=30)
    try:
        with conn.cursor() as cur:
            rows = [audit_level(cur, level) for level in LEVELS]
    finally:
        conn.close()

    payload = {
        "date": DATE,
        "source": "LMFDB public read-only PostgreSQL mirror",
        "purpose": "Audit whether the remaining Loop 107 oldlevels have usable orbit/eigenvalue/charpoly data.",
        "levels": LEVELS,
        "summary": {
            "levels_with_newspace_rows": [row["level"] for row in rows if row["newspaces"]],
            "levels_with_usable_orbit_data": [row["level"] for row in rows if row["usable_orbit_data"]],
            "levels_with_usable_charpoly_data": [row["level"] for row in rows if row["usable_charpoly_data"]],
        },
        "rows": rows,
    }
    JSON_OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# LMFDB Missing-Orbit Audit",
        "",
        f"Datum: {DATE}",
        "",
        "| Level | Faktor | Newdim | num_forms | mf_newforms(triv) | hecke_nf | hecke_cc | Charpoly |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        ns = row["newspaces"][0] if row["newspaces"] else {}
        lines.append(
            f"| {row['level']} | `{row['level_factor']}` | {ns.get('dim', 0)} | "
            f"{ns.get('num_forms')} | {row['counts']['mf_newforms_trivial']} | "
            f"{row['counts']['mf_hecke_nf']} | {row['counts']['mf_hecke_cc']} | "
            f"{'yes' if row['usable_charpoly_data'] else 'no'} |"
        )
    lines.extend(
        [
            "",
            "## Ergebnis",
            "",
            "Alle drei Levels besitzen `mf_newspaces`-Zeilen, aber keine nutzbare",
            "Orbit-/Eigenwert-/Charpoly-Abdeckung in den abgefragten öffentlichen",
            "LMFDB-Tabellen. Gesamt-Newspace-Traces sind vorhanden, reichen aber",
            "nicht, um einen einzelnen kongruenten Orbit auszuschließen.",
        ]
    )
    MD_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(JSON_OUT)
    print(MD_OUT)
    print(json.dumps(payload["summary"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
