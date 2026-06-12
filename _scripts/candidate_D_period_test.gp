\\ Kandidat D — Periodenquotienten-Test für Frey-Kurven
\\ Berechnet Ω_E und Ω_{E'} für E' = E/⟨(0,0)⟩
\\ Design: _proof-notes/candidate_D_period_ratio_design.md

candidate_D_test(a, b) = {
  my(c, E, Emin, omega_E, disc_E, N_E);
  my(iso, Eprime, Epmin, omega_Ep, disc_Ep, N_Ep);
  my(ratio, tors_E, tors_Ep, tam_E, tam_Ep);

  c = a + b;

  \\ Frey-Kurve: y^2 = x(x-a)(x+b) = x^3 + (b-a)x^2 - ab*x
  E = ellinit([0, b-a, 0, -a*b, 0]);
  Emin = ellminimalmodel(E);
  N_E = ellconductor(Emin);
  disc_E = Emin.disc;

  \\ Perioden der Frey-Kurve
  omega_E = Emin.omega;
  \\ Reelle Periode: wenn disc > 0 (zwei Komponenten), Ω = 2·ω₁
  if(disc_E > 0,
    real_omega_E = 2 * real(omega_E[1]),
    real_omega_E = real(omega_E[1])
  );

  \\ Torsion und Tamagawa
  tors_E = elltors(Emin)[1];
  tam_E = ellglobalred(Emin)[3][,2];
  tam_prod_E = prod(i=1, #tam_E, tam_E[i]);

  \\ 2-Isogenie: Kern = (0,0), Kernpolynom = x
  iso = ellisogeny(E, x);
  \\ iso[1] = Isogenie-Abbildung, iso[2] = (nicht standard — PARI gibt [map, Eprime] zurück)
  \\ In PARI ≥ 2.15: ellisogeny(E, G) gibt [rational map] zurück
  \\ Bildkurve: ellisogenyapply brauchen wir nicht — wir brauchen die Kurve

  \\ Alternative: Vélu direkt. Für Kern (0,0) auf y^2 = x^3 + Ax^2 + Bx:
  \\ A = b-a, B = -ab
  \\ Bildkurve: y^2 = x^3 - 2A*x^2 + (A^2 - 4B)*x
  my(A_coeff = b - a, B_coeff = -a*b);
  my(A2 = -2*A_coeff, A4 = A_coeff^2 - 4*B_coeff);
  Eprime = ellinit([0, A2, 0, A4, 0]);
  Epmin = ellminimalmodel(Eprime);
  N_Ep = ellconductor(Epmin);
  disc_Ep = Epmin.disc;

  omega_Ep = Epmin.omega;
  if(disc_Ep > 0,
    real_omega_Ep = 2 * real(omega_Ep[1]),
    real_omega_Ep = real(omega_Ep[1])
  );

  tors_Ep = elltors(Epmin)[1];
  tam_Ep = ellglobalred(Epmin)[3][,2];
  tam_prod_Ep = prod(i=1, #tam_Ep, tam_Ep[i]);

  \\ Verhältnis und normalisiertes Minimum
  ratio = real_omega_E / real_omega_Ep;
  min_omega = min(real_omega_E, real_omega_Ep);
  threshold = N_E^(-0.5);

  printf("=== Tripel (%d, %d, %d) ===\n", a, b, c);
  printf("  N(E)  = %d,  N(E') = %d\n", N_E, N_Ep);
  printf("  disc(E) sign: %s,  disc(E') sign: %s\n",
    if(disc_E>0, "+", "-"), if(disc_Ep>0, "+", "-"));
  printf("  Ω_E   = %.8f\n", real_omega_E);
  printf("  Ω_E'  = %.8f\n", real_omega_Ep);
  printf("  Ω_E / Ω_E' = %.6f\n", ratio);
  printf("  min(Ω) = %.8f\n", min_omega);
  printf("  N^{-1/2} = %.8f\n", threshold);
  printf("  Ω_E / N^{-1/2}    = %.4f\n", real_omega_E / threshold);
  printf("  min(Ω) / N^{-1/2} = %.4f\n", min_omega / threshold);
  printf("  |Tors(E)| = %d,  |Tors(E')| = %d\n", tors_E, tors_Ep);
  printf("  ∏c_p(E) = %d,  ∏c_p(E') = %d\n", tam_prod_E, tam_prod_Ep);
  printf("  Tam-Ratio = %.4f\n", tam_prod_Ep * 1.0 / tam_prod_E);
  printf("\n");

  [a, b, c, N_E, real_omega_E, real_omega_Ep, ratio, min_omega,
   tors_E, tors_Ep, tam_prod_E, tam_prod_Ep];
};

\\ Standard-Tripel aus tab:mining
print("KANDIDAT D — PERIODENQUOTIENTEN-TEST");
print("=====================================\n");

results = [];

results = concat(results, [candidate_D_test(1, 8)]);
results = concat(results, [candidate_D_test(3, 125)]);
results = concat(results, [candidate_D_test(13, 243)]);
results = concat(results, [candidate_D_test(1, 4374)]);
results = concat(results, [candidate_D_test(2, 6436341)]);

\\ Zusammenfassung
print("\n=== ZUSAMMENFASSUNG ===");
print("Tripel | Ω_E/Ω_E' | min(Ω)/N^{-1/2} | Ω_E/N^{-1/2} | Tors E/E' | Tam E/E'");
print("-------|-----------|------------------|--------------|-----------|----------");
for(i=1, #results,
  my(r = results[i]);
  my(threshold = r[4]^(-0.5));
  printf("(%d,%d,%d) | %.4f | %.4f | %.4f | %d/%d | %d/%d\n",
    r[1], r[2], r[3], r[7],
    r[8]/threshold, r[5]/threshold,
    r[9], r[10], r[11], r[12]);
);

print("\n=== VERDIKT ===");
print("Prüfe: Ist Ω_E/Ω_E' ∈ {2, 1, 1/2} konsistent?");
print("Prüfe: Gibt min(Ω)/N^{-1/2} systematisch mehr als Ω_E/N^{-1/2}?");
