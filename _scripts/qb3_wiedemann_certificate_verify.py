#!/usr/bin/env python3
"""Verify a scalar-Wiedemann rank certificate for the Q_B-3 source Gram block.

The verifier is intentionally pure Python.  It checks the portable certificate
part of a run:

    s_k = u^T A^k v
    s_k + c_1 s_{k-1} + ... + c_L s_{k-L} = 0

over F_q.  If Berlekamp-Massey recomputes degree L=n and c_L is nonzero, the
sequence has a full-degree scalar generator.  Together with an authenticated
matvec transcript for A, this is the production certificate pattern for
rank(A)=n.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-05-23"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def mod_list(values: list[Any], q: int) -> list[int]:
    return [int(x) % q for x in values]


def signed_lift(value: int, q: int) -> int:
    v = int(value) % q
    if v > q // 2:
        v -= q
    return v


def berlekamp_massey(sequence: list[int], q: int) -> tuple[int, list[int]]:
    c = [1]
    b_poly = [1]
    degree = 0
    shift = 1
    last_discrepancy = 1

    for n, s_n in enumerate(sequence):
        discrepancy = s_n % q
        for i in range(1, degree + 1):
            discrepancy = (discrepancy + c[i] * sequence[n - i]) % q
        if discrepancy == 0:
            shift += 1
            continue

        old = list(c)
        factor = (-discrepancy * pow(last_discrepancy, -1, q)) % q
        needed = len(b_poly) + shift
        if len(c) < needed:
            c.extend([0] * (needed - len(c)))
        for j, coeff in enumerate(b_poly):
            c[j + shift] = (c[j + shift] + factor * coeff) % q

        if 2 * degree <= n:
            degree = n + 1 - degree
            b_poly = old
            last_discrepancy = discrepancy
            shift = 1
        else:
            shift += 1

    return degree, [x % q for x in c[: degree + 1]]


def recurrence_failures(sequence: list[int], coeffs: list[int], q: int, max_failures: int) -> list[dict[str, int]]:
    degree = len(coeffs) - 1
    failures: list[dict[str, int]] = []
    for k in range(degree, len(sequence)):
        total = sequence[k] % q
        for i in range(1, degree + 1):
            total = (total + coeffs[i] * sequence[k - i]) % q
        if total != 0:
            failures.append({"k": k, "residue": total, "signed": signed_lift(total, q)})
            if len(failures) >= max_failures:
                break
    return failures


def extract_certificate(payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    if "sequence_mod_q" in payload and "connection_coefficients_mod_q" in payload:
        return payload, payload
    cert = payload.get("accepted_certificate")
    if isinstance(cert, dict) and "sequence_mod_q" in cert:
        return cert, payload
    for attempt in payload.get("attempts", []):
        if isinstance(attempt, dict) and "sequence_mod_q" in attempt:
            return attempt, payload
    raise ValueError("no Wiedemann sequence certificate found")


def verify(path: Path, expected_rank: int | None, expected_q: int | None, min_suffix: int) -> dict[str, Any]:
    payload = load_json(path)
    cert, root = extract_certificate(payload)
    q = int(expected_q or root.get("q") or cert.get("q"))
    target_rank = int(expected_rank or root.get("rank_A_target") or cert.get("target_rank"))
    degree_claim = int(cert["degree"])
    coeffs = mod_list(cert["connection_coefficients_mod_q"], q)
    sequence = mod_list(cert["sequence_mod_q"], q)
    bm_degree, bm_coeffs = berlekamp_massey(sequence, q)
    recurrence_bad = recurrence_failures(sequence, coeffs, q, max_failures=12)

    constant = coeffs[-1] if coeffs else 0
    length_required = 2 * target_rank + min_suffix
    coeffs_match_bm = degree_claim == bm_degree and coeffs == bm_coeffs
    full_degree = degree_claim == target_rank == bm_degree
    accepted = (
        q > 2
        and len(coeffs) == degree_claim + 1
        and coeffs[0] == 1
        and len(sequence) >= length_required
        and not recurrence_bad
        and coeffs_match_bm
        and full_degree
        and constant % q != 0
    )

    return {
        "tool": "qb3_wiedemann_certificate_verify",
        "date": DATE,
        "input_json": str(path),
        "level": root.get("level"),
        "mode": root.get("mode"),
        "q": q,
        "target_rank": target_rank,
        "degree_claim": degree_claim,
        "bm_degree": bm_degree,
        "sequence_length": len(sequence),
        "min_sequence_length": length_required,
        "constant_mod_q": int(constant % q),
        "constant_signed": signed_lift(constant, q),
        "coefficients_match_bm": coeffs_match_bm,
        "full_degree": full_degree,
        "constant_nonzero": bool(constant % q != 0),
        "recurrence_verified": not recurrence_bad,
        "recurrence_failures": recurrence_bad,
        "accepted_rank_certificate_pattern": accepted,
        "certificate_scope": (
            "This verifies the portable scalar sequence certificate.  A full "
            "large-level proof certificate also needs the run transcript or "
            "recomputation showing that the sequence was generated by the "
            "declared A = C_source B_AL C_source^T matvec."
        ),
    }


def write_md(result: dict[str, Any], out_md: Path) -> None:
    lines = [
        "# Q_B-3 Wiedemann Certificate Verification",
        "",
        f"Datum: `{result['date']}`",
        f"Input: `{result['input_json']}`",
        "",
        "## Ergebnis",
        "",
        "```text",
        f"q:                         {result['q']}",
        f"target rank:               {result['target_rank']}",
        f"degree claim:              {result['degree_claim']}",
        f"Berlekamp-Massey degree:   {result['bm_degree']}",
        f"sequence length:           {result['sequence_length']}",
        f"min sequence length:       {result['min_sequence_length']}",
        f"constant signed:           {result['constant_signed']}",
        f"coefficients match BM:     {result['coefficients_match_bm']}",
        f"recurrence verified:       {result['recurrence_verified']}",
        f"accepted pattern:          {result['accepted_rank_certificate_pattern']}",
        "```",
        "",
        "## Scope",
        "",
        result["certificate_scope"],
        "",
    ]
    if result["recurrence_failures"]:
        lines.extend([
            "## Rekurrenzfehler",
            "",
            "```json",
            json.dumps(result["recurrence_failures"], indent=2, ensure_ascii=False),
            "```",
            "",
        ])
    out_md.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--certificate", type=Path, required=True)
    parser.add_argument("--expected-rank", type=int)
    parser.add_argument("--expected-q", type=int)
    parser.add_argument("--min-suffix", type=int, default=4)
    parser.add_argument(
        "--out-json",
        type=Path,
        default=ROOT / "_results" / f"qb3_wiedemann_certificate_verify_{DATE}.json",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=ROOT / "_results" / f"qb3_wiedemann_certificate_verify_{DATE}.md",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = verify(args.certificate, args.expected_rank, args.expected_q, args.min_suffix)
    args.out_json.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_md(result, args.out_md)
    print(json.dumps({
        "accepted": result["accepted_rank_certificate_pattern"],
        "target_rank": result["target_rank"],
        "bm_degree": result["bm_degree"],
        "constant_signed": result["constant_signed"],
    }, ensure_ascii=False))
    return 0 if result["accepted_rank_certificate_pattern"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
