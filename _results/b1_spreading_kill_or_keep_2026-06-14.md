# B1 Spreading Kill-or-Keep-Test (2026-06-14)

**Frage (Ajtai-Reverse):** Kann ein abc-Verletzer isoliert bleiben? Spreading lebt nur bei qualitaetserhaltender Operation MIT Expansion.
**Daten:** de Smit, 241 gute Tripel (q≥1.4). a+b=c verifiziert: 240/240 (Parsefehler 1); max |q_listed−q_comp| = 0.0.
**Notwendige Bedingung getestet:** Radikal-Cluster ÜBER Glattheits-Nullmodell (500 Permutationen, grad-/größen-erhaltend).

Mittleres |q_i−q_j| über alle Paare (Baseline „klein"): 0.0345.

| Overlap-Schwelle | Kanten (obs) | Kanten (Null μ±σ) | z | max Komp. (obs) | max Komp. (Null μ) | z | ⟨Δq⟩ Kante |
|---|---:|---|---:|---:|---:|---:|---:|
| 0.500 | 21003 | 8662.6±654.6 | 18.85 | 240 | 238.7 | 1.16 | 0.0364 |
| 0.667 | 5252 | 1001.5±171.0 | 24.85 | 237 | 189.7 | 5.77 | 0.0425 |
| 0.750 | 3861 | 671.3±131.1 | 24.33 | 236 | 174.4 | 5.51 | 0.0473 |
| 1.000 | 498 | 51.9±29.7 | 15.00 | 210 | 38.1 | 7.20 | 0.0438 |

## Operations-Enumeration (deterministische Tripel-Operationen)

| Operation | gültig? | Δq | Expansion |
|---|---|---|---|
| Skalierung+Primitivierung | ja | 0.0 | Orbit=1 (primitiv invariant) -> KEINE Expansion |
| additive Stoerung (a+e, b, c) | nein | — | verletzt a+b=c -> ungueltig (Rigiditaet) |
| Primexponent-Bump im Radikal | nein | — | veraendert c, a+b=c neu zu loesen -> keine lokale Operation |

## Verdikt: **KILL**

Kein Overlap-Exzess (z≥3) mit gleichzeitig kleinem Kanten-Δq über dem Glattheits-Nullmodell; die deterministischen Tripel-Operationen sind nicht-expandierend (a+b=c-Rigidität). ⟹ Die NOTWENDIGE Bedingung für Spreading ist nicht erfüllt: ein Verletzer kann im Radikal-Raum isoliert bleiben. Triple-Ebene-B1 verworfen; falls Spreading existiert, lebt es in der Kurven-/Twist-Familie (Zertifikatsraum), nicht in der Tripel-Familie.

Caveat: Dies ist die billige erste Stufe (notwendige Bedingung). KILL ist belastbar (kein Cluster ⟹ keine Operation); KEEP ist nur ein Weiterleben, kein Spreading-Beweis. de Weger-Set nicht im Projekt — de Smit als Referenz.

JSON: `/Users/lukas/compute/abc_b1/_results/b1_spreading_kill_or_keep_2026-06-14.json`. Script: `_scripts/b1_spreading_kill_or_keep.py`.
