# M*: Charpoly-/Hecke-Feld-Datenpfad

Datum: 2026-05-10

## Kurzbefund

Der nächste rechnerische Schritt sollte kein voller ModularSymbols-Lauf auf
\(N=240672\) sein. Sinnvoller ist eine gestufte Mod-\(3863\)-
Determinant-/Kern-Kaskade auf den drei Rest-Oldlevels.

## Ziellevels

| Level | Faktor | Newdim | Gesamtdim | Sturm | Beitrag in N | Erste Probe |
|---:|---|---:|---:|---:|---:|---|
| 60168 | 2^3 * 3 * 23 * 109 | 1188 | 10545 | 21120 | 3564 | det(T_5-a_5(E)) mod 3863 on S2(Gamma0(M))^new |
| 80224 | 2^5 * 23 * 109 | 2376 | 10545 | 21120 | 4752 | det(T_5-a_5(E)) mod 3863 on S2(Gamma0(M))^new |
| 120336 | 2^4 * 3 * 23 * 109 | 2376 | 21097 | 42240 | 4752 | det(T_5-a_5(E)) mod 3863 on S2(Gamma0(M))^new |

## Echter New-Level

- Level: 240672 = 2^5 * 3 * 23 * 109.
- Newdim: 4752.
- Gesamtdimension: 42209.
- Sturm-Bound: 84480.
- Risiko: high; split by Atkin-Lehner signs before a full determinant if possible.

## Gestufter Plan

### R0 -- Do not use LMFDB total traces as orbit evidence

The missing levels have only mf_newspaces rows. Total traces do not exclude individual orbit factors unless a one-orbit decomposition is known.

Status: guardrail.

### R1 -- Restlevel determinant filter

Compute det(T_p-a_p(E)) mod 3863 on the newspace, starting with p=5.

Status: next executable data step.

### R2 -- Kernel cascade

Intersect kernels of T_p-a_p(E) modulo 3863 for p=5,7,11,13.

Status: conditional.

### R3 -- Orbit/field recovery only after a kernel survivor

Compute factor data, minimal polynomials, or q-adic field primes only on surviving subspace.

Status: conditional.

### N1 -- True newlevel after restlevels

Run the same determinant/kernelfilter on the 4752-dimensional new_subspace.

Status: high-risk later step.

### F1 -- FOG-FC evidence, not proof

If q=3863 is killed or localized, repeat for several external primes and small T to estimate index support.

Status: later evidence step.

## Entscheidung

Rechnerisch lohnt zuerst R1/R2 auf \(60168,80224,120336\).
Wenn diese drei Levels sterben, bleibt der echte New-Level als einziger
Datenkern. Wenn ein Restlevel überlebt, muss nur dieser Survivor
teuer in Orbit-/Hecke-Feld-Daten zerlegt werden.

Dieser Pfad ist Dateninfrastruktur für FOG-FC/NL-DualSmall; er ersetzt
keinen asymptotischen Beweis.
