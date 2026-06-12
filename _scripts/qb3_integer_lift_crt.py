#!/usr/bin/env python3
"""CRT combination of two Q_B Wiedemann certificates into an integer constraint.

Given two Q_B-3 Wiedemann certificates for the same level/mode but two
distinct residue primes q and q', combine them via CRT to derive an
integer-level constraint on Q_B and its key Wiedemann invariants.

Mathematically:
  Q_B(phi)  mod q   from certificate 1
  Q_B(phi)  mod q'  from certificate 2
  ⇒ Q_B(phi)  mod (q · q')  (by CRT, if matching invariants)

The script also checks consistency:
- target_rank agrees between the two certificates (it's a rank, so q-independent)
- degree agrees (same minimal polynomial degree over Q if matrix is nondegenerate)
- the CRT-lifted Q_B is "small" relative to q*q' (sanity check for integer value)

Usage:
    python qb3_integer_lift_crt.py \\
        --cert1 path_to_cert_q.json \\
        --cert2 path_to_cert_qprime.json \\
        [--out-json crt_report.json]
"""

from __future__ import annotations

import argparse
import json
from math import gcd
from pathlib import Path


def egcd(a: int, b: int) -> tuple[int, int, int]:
    if a == 0:
        return b, 0, 1
    g, x1, y1 = egcd(b % a, a)
    return g, y1 - (b // a) * x1, x1


def modinv(a: int, m: int) -> int:
    g, x, _ = egcd(a % m, m)
    if g != 1:
        raise ValueError(f"inverse of {a} mod {m} does not exist")
    return x % m


def crt(r1: int, m1: int, r2: int, m2: int) -> tuple[int, int]:
    g = gcd(m1, m2)
    if g != 1:
        raise ValueError(f"moduli not coprime: gcd({m1},{m2})={g}")
    m = m1 * m2
    # Find x with x = r1 mod m1, x = r2 mod m2
    diff = (r2 - r1) % m2
    inv = modinv(m1 % m2, m2)
    k = (diff * inv) % m2
    x = (r1 + k * m1) % m
    return x, m


def signed_lift(value: int, m: int) -> int:
    v = value % m
    if v > m // 2:
        v -= m
    return v


def extract_qb_from_certificate(cert: dict) -> dict:
    """Extract the Q_B-3 constant and metadata from a Wiedemann certificate.

    Supports both flat structure (older) and nested under 'accepted_certificate' (newer).
    """
    nested = cert.get("accepted_certificate") or {}
    out = {
        "level": cert.get("level"),
        "mode": cert.get("mode"),
        "q": cert.get("q"),
        "target_rank": cert.get("target_rank"),
        "accepted_seed": cert.get("accepted_seed") or nested.get("seed"),
        "degree": cert.get("degree") or nested.get("degree"),
        "constant_signed": cert.get("constant_signed") if cert.get("constant_signed") is not None else nested.get("constant_signed"),
        "sequence_length": cert.get("sequence_length") or nested.get("sequence_length"),
    }
    return out


def combine(cert1: dict, cert2: dict) -> dict:
    e1 = extract_qb_from_certificate(cert1)
    e2 = extract_qb_from_certificate(cert2)
    q1 = int(e1["q"])
    q2 = int(e2["q"])
    if q1 == q2:
        raise ValueError(f"both certificates use same q = {q1}")

    # Consistency: target_rank should match (rank is q-independent over a prime field)
    rank1 = e1.get("target_rank")
    rank2 = e2.get("target_rank")
    if rank1 != rank2:
        raise ValueError(f"target_rank mismatch: {rank1} vs {rank2}")

    level1 = e1.get("level")
    level2 = e2.get("level")
    mode1 = e1.get("mode")
    mode2 = e2.get("mode")
    if level1 != level2 or mode1 != mode2:
        raise ValueError(
            f"level/mode mismatch: ({level1},{mode1}) vs ({level2},{mode2})"
        )

    # Q_B-Konstante (signed) per Restprime
    c1 = int(e1.get("constant_signed") or 0)
    c2 = int(e2.get("constant_signed") or 0)
    # Unsigned form for CRT
    r1 = c1 % q1
    r2 = c2 % q2

    # CRT
    c_crt, m = crt(r1, q1, r2, q2)
    c_crt_signed = signed_lift(c_crt, m)

    # Sanity: degree match is expected if both nonsingular over Q
    deg1 = e1.get("degree")
    deg2 = e2.get("degree")
    degree_consistent = (deg1 == deg2)

    return {
        "tool": "qb3_integer_lift_crt",
        "level": level1,
        "mode": mode1,
        "rank": rank1,
        "q1": q1, "q2": q2, "modulus_crt": m,
        "constant_signed_q1": c1,
        "constant_signed_q2": c2,
        "constant_crt_unsigned": c_crt,
        "constant_crt_signed": c_crt_signed,
        "degree_q1": deg1,
        "degree_q2": deg2,
        "degree_consistent": degree_consistent,
        "nonzero": c_crt_signed != 0,
        "size_relative_to_modulus": (
            "tiny" if abs(c_crt_signed) < m / 1000 else
            "small" if abs(c_crt_signed) < m / 100 else
            "moderate" if abs(c_crt_signed) < m / 10 else
            "near boundary"
        ),
        "interpretation": (
            "INTEGER VALUE LIKELY: constant fits in [-modulus/2, modulus/2] "
            f"= [-{m//2}, {m//2}]; if true integer value of Q_B is bounded "
            "by max|coef|, this is an unconditional integer lift."
            if c_crt_signed != 0 else
            "ZERO: constant vanishes under CRT; either Q_B=0 (bad) or "
            "the two certificates encode trivial invariants."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cert1", type=Path, required=True,
                        help="First Wiedemann certificate JSON (q)")
    parser.add_argument("--cert2", type=Path, required=True,
                        help="Second Wiedemann certificate JSON (q')")
    parser.add_argument("--out-json", type=Path)
    args = parser.parse_args()

    cert1 = json.loads(args.cert1.read_text(encoding="utf-8"))
    cert2 = json.loads(args.cert2.read_text(encoding="utf-8"))

    report = combine(cert1, cert2)
    if args.out_json:
        args.out_json.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
