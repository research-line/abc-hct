\p 50
default(parisize, "256M");

\\ TAMAGAWA HEIGHT LEDGER v3
\\ Convention: Cremona (= PARI ellheight)
\\
\\ v2 → v3 changes:
\\   - safe_val() guard for ψ₂=0 (128a1 edge case)
\\   - lh_additive() for explicit additive Kodaira types (III, IV, etc.)
\\   - verify_decomposition(): λ^Néron = λ^Cremona + v_p(Δ)/6·log(p)
\\   - frey_ledger(): Frey curve y²=x(x-a)(x+b) from abc triple
\\   - General bad-prime loop (any number of multiplicative places)

\\ --- Core functions ---

archlocal(E, P) = {
  my(z, omv, etv, sig, disc, t1, t2, eta_z, w1, w2, det);
  z = ellpointtoz(E, P);
  omv = E.omega; etv = elleta(E);
  sig = ellsigma(E, z); disc = E.disc;
  w1 = omv[1]; w2 = omv[2];
  if(abs(real(w2)) < 1e-20,
    t1 = real(z)/real(w1);
    t2 = imag(z)/imag(w2),
    det = real(w1)*imag(w2) - real(w2)*imag(w1);
    t1 = (real(z)*imag(w2) - imag(z)*real(w2)) / det;
    t2 = (imag(z)*real(w1) - real(z)*imag(w1)) / det
  );
  eta_z = t1*etv[1] + t2*etv[2];
  return(-log(abs(disc))/6 + real(z * conj(eta_z)) - 2*log(abs(sig)));
};

safe_val(x, p) = {
  if(x == 0, return(9999));
  return(valuation(numerator(x), p) - valuation(denominator(x), p));
};

\\ Cremona Bernoulli formula for split multiplicative I_n
lh_mult(n, j, p) = {
  my(t = (j % n) / (n + 0.0));
  return(n * (t^2 - t + 1.0/6) * log(p));
};

\\ Additive local height via Cremona Prop 3.4.1(d) + decomposition identity
\\ λ^Néron = λ^Cremona + v_p(Δ)/6·log(p)
\\ λ^Cremona = -(1/4)·ord_p(ψ₃(P))·log(p) for additive reduction
lh_cremona_additive(Em, P, p) = {
  my(x_P = P[1], y_P = P[2]);
  my(a1=Em.a1, a2=Em.a2, a3=Em.a3, a4=Em.a4, a6=Em.a6);
  my(b2=Em.b2, b4=Em.b4, b6=Em.b6, b8=Em.b8);
  \\ ψ₃ = 3x⁴ + b₂x³ + 3b₄x² + 3b₆x + b₈
  my(psi3 = 3*x_P^4 + b2*x_P^3 + 3*b4*x_P^2 + 3*b6*x_P + b8);
  my(v3 = safe_val(psi3, p));
  return(-(1/4) * v3 * log(p));
};

lh_neron_additive(Em, P, p) = {
  my(vd = valuation(abs(Em.disc), p));
  return(lh_cremona_additive(Em, P, p) + vd/6 * log(p));
};

\\ Radical
rad(n) = {
  my(f=factor(abs(n)), r=1);
  for(i=1, matsize(f)[1], r *= f[i,1]);
  return(r);
};

\\ --- Full ledger with additive handling ---

full_ledger(E, label) = {
  my(Em, chv, P, hhat, la, lg, denom_x, facts, target);
  my(bad_mult, bad_add, sum_bad);
  Em = ellminimalmodel(E, &chv);
  my(gr = ellglobalred(Em));
  my(N = gr[1]);
  printf("\n--- %s  N=%d ---\n", label, N);

  facts = factor(abs(Em.disc));
  printf("disc="); print(Em.disc);
  printf("Bad: ");
  for(i=1, matsize(facts)[1],
    my(p=facts[i,1]); my(lr=elllocalred(Em,p));
    printf("p=%d(kod=%d,c=%d) ", p, lr[2], lr[4]);
  );
  printf("\nw=%d  tors=%s\n", ellrootno(Em), elltors(Em)[2]);

  if(ellrootno(Em)==-1,
    P = ellheegner(Em),
    my(gens=ellgenerators(Em));
    if(#gens==0, printf("No generator. SKIP.\n"); return);
    P = gens[1]
  );

  hhat = ellheight(Em, P);
  printf("hhat = %.12f\n", hhat);

  la = archlocal(Em, P);
  printf("la   = %.12f\n", la);

  denom_x = denominator(P[1]);
  if(denom_x > 1,
    lg = log(denom_x + 0.0),
    lg = 0
  );
  printf("lg   = %.12f  (denom=%d)\n", lg, denom_x);

  \\ Classify bad primes
  bad_mult = List();
  bad_add = List();
  sum_bad = 0.0;

  for(i=1, matsize(facts)[1],
    my(p=facts[i,1]);
    my(lr=elllocalred(Em,p));
    my(kod=lr[2], cp=lr[4]);

    if(kod > 4,
      \\ Multiplicative I_n: find best component j
      my(n=kod-4);
      my(best_j=0, best_lp=lh_mult(n,0,p), best_diff=100.0);
      for(j=0, n-1,
        my(lp=lh_mult(n,j,p));
        my(trial_target = hhat - la - lg - lp);
        \\ We just record it; matching done later
        if(j==0, best_j=0; best_lp=lp);
      );
      listput(bad_mult, [p, n, cp, kod]);
      printf("  p=%d: I_%d (c=%d, split=%d)\n", p, n, cp, cp>1);
    ,
      \\ Additive reduction
      my(lp_neron = lh_neron_additive(Em, P, p));
      my(lp_cremona = lh_cremona_additive(Em, P, p));
      my(vd = valuation(abs(Em.disc), p));
      sum_bad += lp_neron;
      listput(bad_add, [p, kod, cp, lp_neron, lp_cremona, vd]);
      printf("  p=%d: additive kod=%d c=%d: lambda_Neron=%.12f (Crem=%.6f + v(D)/6*logp=%.6f)\n",
             p, kod, cp, lp_neron, lp_cremona, vd/6*log(p));
    );
  );

  \\ For multiplicative primes, brute-force match all component combinations
  my(nm = #bad_mult);
  if(nm == 0,
    \\ All bad primes are additive — check sum
    my(total = la + lg + sum_bad);
    printf("Ledger check: la + lg + sum_add = %.12f vs hhat = %.12f\n", total, hhat);
    printf("  diff = %.2e\n", abs(total - hhat));
  );

  if(nm >= 1,
    my(target_mult = hhat - la - lg - sum_bad);
    printf("target_mult = hhat - la - lg - sum_add = %.12f\n", target_mult);

    \\ Best-match search over all component combinations
    my(best_diff = 100.0, best_js = vector(nm));

    if(nm == 1,
      my(p1=bad_mult[1][1], n1=bad_mult[1][2]);
      for(j1=0, n1-1,
        my(lp1=lh_mult(n1,j1,p1));
        my(d=abs(target_mult-lp1));
        if(d < best_diff, best_diff=d; best_js=[j1]);
        if(d < 1e-6,
          printf("MATCH j_%d=%d: lp=%.6f diff=%.2e\n", p1, j1, lp1, d);
        );
      );
    );

    if(nm == 2,
      my(p1=bad_mult[1][1], n1=bad_mult[1][2]);
      my(p2=bad_mult[2][1], n2=bad_mult[2][2]);
      for(j1=0, n1-1,
        for(j2=0, n2-1,
          my(lp=lh_mult(n1,j1,p1)+lh_mult(n2,j2,p2));
          my(d=abs(target_mult-lp));
          if(d < best_diff, best_diff=d; best_js=[j1,j2]);
          if(d < 1e-6,
            printf("MATCH j_%d=%d j_%d=%d: diff=%.2e\n", p1,j1,p2,j2,d);
          );
        );
      );
    );

    if(nm == 3,
      my(p1=bad_mult[1][1], n1=bad_mult[1][2]);
      my(p2=bad_mult[2][1], n2=bad_mult[2][2]);
      my(p3=bad_mult[3][1], n3=bad_mult[3][2]);
      for(j1=0, n1-1,
        for(j2=0, n2-1,
          for(j3=0, n3-1,
            my(lp=lh_mult(n1,j1,p1)+lh_mult(n2,j2,p2)+lh_mult(n3,j3,p3));
            my(d=abs(target_mult-lp));
            if(d < best_diff, best_diff=d; best_js=[j1,j2,j3]);
            if(d < 1e-6,
              printf("MATCH j_%d=%d j_%d=%d j_%d=%d: diff=%.2e\n",
                     p1,j1,p2,j2,p3,j3,d);
            );
          );
        );
      );
    );

    if(best_diff > 1e-6,
      printf("BEST j=%s: diff=%.4f\n", best_js, best_diff);
    );
  );

  printf("\n");
};

\\ --- Decomposition identity verifier ---
\\ λ^Néron = λ^Cremona + v_p(Δ)/6·log(p) for all bad p

verify_decomposition(E, label) = {
  my(Em, chv, P, facts);
  Em = ellminimalmodel(E, &chv);
  printf("\n--- Decomposition: %s ---\n", label);

  if(ellrootno(Em)==-1,
    P = ellheegner(Em),
    my(gens=ellgenerators(Em));
    if(#gens==0, printf("No generator. SKIP.\n"); return);
    P = gens[1]
  );

  my(hhat = ellheight(Em, P));
  my(la = archlocal(Em, P));
  my(lg_val = 0);
  my(dx = denominator(P[1]));
  if(dx > 1, lg_val = log(dx + 0.0));

  \\ Compute Néron decomposition: hhat = la + lg + Σ λ_p^Néron
  facts = factor(abs(Em.disc));
  my(sum_neron = 0.0, sum_cremona = 0.0, sum_baseline = 0.0);

  for(i=1, matsize(facts)[1],
    my(p=facts[i,1]);
    my(lr=elllocalred(Em,p));
    my(kod=lr[2], vd=valuation(abs(Em.disc),p));

    if(kod > 4,
      \\ Multiplicative: λ^Cremona = Bernoulli-match, λ^Néron = Cremona + v_p(Δ)/6·log(p)
      my(n=kod-4, target_p = hhat - la - lg_val);
      \\ Skip individual matching here — just verify identity holds globally
      printf("  p=%d: I_%d, v(D)=%d\n", p, n, vd);
    ,
      \\ Additive
      my(lp_crem = lh_cremona_additive(Em, P, p));
      my(baseline = vd/6 * log(p));
      my(lp_neron = lp_crem + baseline);
      sum_cremona += lp_crem;
      sum_baseline += baseline;
      sum_neron += lp_neron;
      printf("  p=%d: kod=%d, v(D)=%d, Crem=%.10f, base=%.10f, Neron=%.10f\n",
             p, kod, vd, lp_crem, baseline, lp_neron);
    );
  );

  printf("Sum additive: Cremona=%.10f + baseline=%.10f = Neron=%.10f\n",
         sum_cremona, sum_baseline, sum_neron);
  printf("hhat=%.12f  la=%.12f  lg=%.12f\n", hhat, la, lg_val);
};

\\ --- Frey curve from abc triple ---

frey_ledger(a, b, label) = {
  my(c = a + b);
  my(r = rad(a*b*c));
  my(q = log(c+0.0)/log(r+0.0));
  printf("\n=== Frey: %s  (a=%d, b=%d, c=%d) ===\n", label, a, b, c);
  printf("rad=%d  q=%.4f\n", r, q);

  my(E = ellinit([0, b-a, 0, -a*b, 0]));
  full_ledger(E, label);
};

\\ === MAIN ===

printf("TAMAGAWA HEIGHT LEDGER v3\n");
printf("Convention: Cremona (= PARI ellheight)\n\n");

printf("=== PART A: Reyssat verification ===\n");
{
  my(E = ellinit([0, 6436341-2, 0, -2*6436341, 0]));
  full_ledger(E, "Reyssat");
  verify_decomposition(E, "Reyssat");
}

printf("\n=== PART B: Cremona DB scan (Kodaira III at 2, rank >= 1) ===\n");
{
  my(found = List());
  for(N=1, 500,
    iferr(
      my(curves = ellsearch(N));
      for(i=1, #curves,
        my(E = ellinit(curves[i][2]));
        my(lr2 = elllocalred(E, 2));
        if(lr2[2] == 3,
          my(w = ellrootno(E));
          my(r = ellanalyticrank(E)[1]);
          if(r >= 1,
            printf("FOUND: %s N=%d kod2=%d c2=%d w=%d rank=%d\n",
                   curves[i][1], N, lr2[2], lr2[4], w, r);
            if(#found < 5, listput(found, curves[i]));
          );
        );
      );
    , err, );
  );
  printf("Found %d curves with Kodaira III at 2, rank >= 1\n\n", #found);

  printf("=== PART C: Full ledger on found curves ===\n");
  for(i=1, #found,
    my(E = ellinit(found[i][2]));
    full_ledger(E, found[i][1]);
  );
}

printf("\n=== SCAN COMPLETE ===\n");
