"""Frey-specific Farey frame probe for the modular-symbol route.

This is deliberately a pre-Sage filter. It does not compute modular-symbol
integrals. It tests the part of P1 that can be checked with exact elementary
arithmetic: the canonical Farey path attached to lambda = a/c and the geometry
that a future Sage modular-symbol computation would have to exploit.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class Triple:
    a: int
    b: int
    name: str
    n_rad: int
    n_cond: int | None = None

    @property
    def c(self) -> int:
        return self.a + self.b


TRIPLES = [
    Triple(1, 8, "1+8=9", 6, 48),
    Triple(3, 125, "3+125=128", 30, 240),
    Triple(13, 243, "13+243=256", 78, None),
    Triple(1, 2400, "1+2400=2401", 210, 1680),
    Triple(1, 4374, "1+4374=4375", 210, 3360),
    Triple(2, 6436341, "Reyssat", 15042, 240672),
]


def continued_fraction(frac: Fraction) -> list[int]:
    n, d = frac.numerator, frac.denominator
    out: list[int] = []
    while d:
        q, n = divmod(n, d)
        out.append(q)
        n, d = d, n
    return out


def convergents(cf: list[int]) -> list[Fraction]:
    convs: list[Fraction] = []
    for i in range(1, len(cf) + 1):
        value = Fraction(cf[i - 1], 1)
        for q in reversed(cf[1 : i - 1]):
            value = q + Fraction(1, value)
        if i > 1:
            value = cf[0] + Fraction(1, value)
        convs.append(value)
    return convs


def farey_edges(frac: Fraction) -> list[tuple[Fraction, Fraction]]:
    convs = [Fraction(0, 1)] + convergents(continued_fraction(frac))
    clean: list[Fraction] = []
    for x in convs:
        if not clean or clean[-1] != x:
            clean.append(x)
    return list(zip(clean, clean[1:]))


def agm(x: float, y: float) -> float:
    while abs(x - y) > 1e-15 * max(1.0, abs(x)):
        x, y = (x + y) / 2.0, math.sqrt(x * y)
    return x


def model_lambda1(a: int, b: int) -> float:
    c = a + b
    omega_re = 2.0 * math.pi / agm(math.sqrt(c), math.sqrt(a))
    omega_im = 2.0 * math.pi / agm(math.sqrt(c), math.sqrt(b))
    return min(omega_re, omega_im)


def main() -> None:
    print("Frey modular-symbol Farey-frame probe (P1 pre-Sage filter)")
    print("=" * 88)
    print(
        f"{'triple':<18} {'lambda':>12} {'cf':>18} {'edges':>5} "
        f"{'Hmax':>8} {'sqrtN*lam1':>12} {'sqrtNcond*lam1':>16} {'verdict':>16}"
    )
    print("-" * 88)

    for t in TRIPLES:
        lam = Fraction(t.a, t.c)
        cf = continued_fraction(lam)
        edges = farey_edges(lam)
        hmax = max(max(e[0].denominator, e[1].denominator) for e in edges)
        lam1 = model_lambda1(t.a, t.b)
        ncond = t.n_cond or t.n_rad
        scaled_rad = math.sqrt(t.n_rad) * lam1
        scaled_cond = math.sqrt(ncond) * lam1
        if len(edges) <= 3:
            verdict = "too sparse"
        elif scaled_cond < 1:
            verdict = "stress case"
        else:
            verdict = "geometry ok"
        print(
            f"{t.name:<18} {str(lam):>12} {str(cf):>18} {len(edges):>5} "
            f"{hmax:>8} {scaled_rad:>12.4f} {scaled_cond:>16.4f} {verdict:>16}"
        )

    print()
    print("Interpretation:")
    print("- The Farey path is canonical and Frey-specific, but often very short.")
    print("- The geometry-only quantity sqrt(N)*lambda1 is already the abc-equivalent scale.")
    print("- A genuine P1 win therefore needs modular-symbol coefficients or frame ratios")
    print("  that grow beyond the trivial period lattice normalization.")
    print("- Next executable step requires Sage's E.modular_symbol machinery.")


if __name__ == "__main__":
    main()
