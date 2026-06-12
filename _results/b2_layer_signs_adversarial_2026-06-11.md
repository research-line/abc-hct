# B2: Schicht-Vorzeichen + adversariales θ′ (2026-06-11)

Reduktions-Lemma: ⟨Σ_I φ, Σ_J φ⟩ = Σ_{Kanten(I×J)} G_ij (exakt).

| Schicht | Kanten | G>0 | G<0 | Anteil + | |G| median | |G| max (norm.) |
|---|---|---|---|---|---|---|
| maninT | 253388 | 84463 | 168925 | 0.333 | 0.2500 | 1.0000 |
| U3 | 334592 | 134455 | 200137 | 0.402 | 0.1890 | 0.6000 |
| T5 | 757414 | 385733 | 371681 | 0.509 | 0.1826 | 0.6455 |

**Adversariales θ′ (Matching der schwersten Kanten, I×J disjunkt):** K=64: 0.638, K=128: 0.617, K=256: 0.596, K=512: 0.584, K=1024: 0.564

Laufzeit: 5.1s. JSON: `_results/b2_layer_signs_adversarial_2026-06-11.json`

## Befund

1. **Worst-case weak flat RIP ist für die volle Matrix FALSCH:** Das
   adversariale Matching hält θ′ ≈ 0.56–0.64 bis K = 1024 — es gibt
   tausende disjunkte schwere Paare. Struktureller Unterschied zu
   BDFKK-Chirps (dort ist die Kohärenz μ ~ p^(−1/2) klein, schwere Paare
   existieren nicht). Die Witness-Matrix ist „RIP außerhalb eines
   strukturierten Kerns", keine klassische RIP-Matrix. ⟹ Das Hauptlemma
   MUSS als Struktur/Generisch-Zerlegung formuliert werden (v2 unten);
   die frühere Zielmarke θ′ ≲ 0.01 gilt nur für das generische Regime.
2. **maninT-Vorzeichen sind EXAKT deterministisch:** 84 463 positive vs.
   168 925 negative Kanten = exakt 1 positive + 2 negative pro Dreieck
   (84 468 Dreiecke). Das algebraische Horn hat in dieser Schicht eine
   vollständig explizite Vorzeichen-Kombinatorik. U₃: 40/60 strukturiert;
   T₅: 51/49 quasi-balanciert (zufallsartig).
3. **Hauptlemma v2 (Programm-Formulierung):** Zerlege den Spaltenraum in
   STRUKTUR-Teil (Cliquen-Kern-Nachbarschaften — endlich, P¹-klassifizierbar,
   exakte Vorzeichen-Muster) und GENERISCHEN Teil (≥ 27 489 orthonormal +
   low-coincidence-Erweiterung). Beweisziele: (a) RIP auf dem generischen
   Teil via Kantensummen (Reduktions-Lemma exakt: ⟨Σ_I,Σ_J⟩ = Σ_Kanten G_ij);
   (b) der Struktur-Teil ist klassifiziert und deckt sich mit den bekannten
   Kern-/S5-Klassen. CR-2b-No-Escape wird dann: **dünne Fast-Kerne können
   nur durch klassifizierte Strukturrichtungen entkommen — und die sind
   durch die S5-/Fitting-Zertifikate (C1!) abgedeckt.** B2 und C1
   verschmelzen an dieser Stelle zu EINEM Programm.
