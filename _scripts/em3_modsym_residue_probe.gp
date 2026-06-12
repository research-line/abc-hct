\\ EM-3 / P1': modular-symbol residue probe.
\\
\\ Goal:
\\   Repeat the P1 matched-control setup, but measure residue nonvanishing
\\   modulo odd primes ell that actually occur as residual conductor drops:
\\       D_ell = prod_{p | N(E), ell | v_p(Delta_min)} p.
\\
\\ Scope:
\\   This is a computable surrogate for the Hecke-maximal-ideal question.
\\   It does NOT construct maximal ideals m_ell in the Hecke algebra. It only
\\   tests whether the period-normalized modular-symbol values along the
\\   Frey star become systematically zero modulo the relevant ell, compared
\\   with random centers from the P1 control design.
\\
\\ Run on Mac Studio:
\\   gp -s 8G -q em3_modsym_residue_probe.gp

\\p 50

absreal(x) = abs(x + 0.0);

frey_curve(a, b) = ellinit([0, b-a, 0, -a*b, 0]);

farey_star(r, s, H) =
{
  my(edges = List());
  for(q = 1, H,
    for(k = 0, 1,
      my(num = r*q + (-1)^k);
      if(num % s == 0,
        my(p = num \ s);
        if(p >= 0 && p <= q && !(p == r && q == s),
          listput(edges, [r/s, p/q]);
        );
      );
    );
  );
  Vec(edges);
};

random_coprime(slo, shi) =
{
  my(s, r);
  while(1,
    s = slo + random(shi - slo + 1);
    if(s < 2, s = 2);
    r = 1 + random(s - 1);
    if(gcd(r, s) == 1, return([r, s]));
  );
};

rat_vell(x, ell) =
{
  if(x == 0, return(999));
  valuation(numerator(x), ell) - valuation(denominator(x), ell);
};

edge_profile(M, xp, xm, edges, ell) =
{
  my(nonzero_edges = 0, zero_edges = 0, pole_values = 0);
  my(min_v = 999, max_frame = 0.0);
  for(i = 1, #edges,
    my(vp = mseval(M, xp, edges[i]));
    my(vm = mseval(M, xm, edges[i]));
    my(vvp = rat_vell(vp, ell));
    my(vvm = rat_vell(vm, ell));
    if(vvp < 0, pole_values++);
    if(vvm < 0, pole_values++);
    min_v = min(min_v, vvp);
    min_v = min(min_v, vvm);
    if(vvp <= 0 || vvm <= 0,
      nonzero_edges++,
      zero_edges++
    );
    max_frame = max(max_frame, max(absreal(vp), absreal(vm)));
  );
  [nonzero_edges, zero_edges, min_v, pole_values, max_frame];
};

drop_data(E, ell) =
{
  my(N = ellglobalred(E)[1]);
  my(Emin = ellminimalmodel(E));
  my(Delta = abs(Emin.disc));
  my(fN = factor(N));
  my(drop_primes = List());
  for(i = 1, matsize(fN)[1],
    my(p = fN[i, 1]);
    my(v = valuation(Delta, p));
    if(v > 0 && v % ell == 0,
      listput(drop_primes, p);
    );
  );
  my(dp = Vec(drop_primes));
  [if(#dp, vecprod(dp), 1), dp];
};

drop_string(dp) =
{
  if(#dp == 0, return("-"));
  my(s = Str(dp[1]));
  for(i = 2, #dp,
    s = Strprintf("%s,%d", s, dp[i]);
  );
  s;
};

report_residue(label, kind, center_num, center_den, ell, D_ell, dp, edges, prof) =
{
  my(nonzero_edges = prof[1]);
  my(zero_edges = prof[2]);
  my(min_v = prof[3]);
  my(pole_values = prof[4]);
  my(max_frame = prof[5]);
  printf("RES | %s | kind=%s | center=%d/%d | ell=%d | D_ell=%d | drop_primes=%s | edges=%d | max_frame=%.12g | nonzero_edges=%d | zero_edges=%d | support=%.6f | min_v=%d | pole_values=%d | all_zero=%d\n",
    label, kind, center_num, center_den, ell, D_ell, drop_string(dp), #edges,
    max_frame, nonzero_edges, zero_edges, nonzero_edges / #edges, min_v,
    pole_values, nonzero_edges == 0);
};

matched_residue_case(label, qabc, a, b, ncontrols) =
{
  my(c = a + b);
  printf("START | %s | a=%d | b=%d | c=%d\n", label, a, b, c);
  my(E = frey_curve(a, b));
  my(N = ellglobalred(E)[1]);
  my(w = ellrootno(E));
  my(ms = msfromell(E, 0));
  my(M = ms[1]);
  my(x = ms[2]);
  my(xp = x[1]);
  my(xm = x[2]);
  my(d = msdim(M));
  printf("INIT | %s | q=%.3f | Ncond=%d | rootno=%d | dim=%d\n", label, qabc, N, w, d);

  my(test_ells = [3, 5, 7, 11, 13, 17, 19]);
  my(active_ells = List());
  my(active_D = List());
  my(active_dp = List());
  for(i = 1, #test_ells,
    my(ell = test_ells[i]);
    my(dd = drop_data(E, ell));
    if(dd[1] > 1,
      listput(active_ells, ell);
      listput(active_D, dd[1]);
      listput(active_dp, dd[2]);
    );
  );
  my(ells = Vec(active_ells));
  my(Ds = Vec(active_D));
  my(dps = Vec(active_dp));
  printf("ACTIVE | %s | active_ells=%s\n", label, Str(ells));
  if(#ells == 0,
    printf("SKIP | %s | no nontrivial odd residual conductor drops\n", label);
    return();
  );

  my(H_frey = 2*c + 1);
  my(edges_frey = farey_star(a, c, H_frey));
  for(j = 1, #ells,
    my(prof = edge_profile(M, xp, xm, edges_frey, ells[j]));
    report_residue(label, "FREY", a, c, ells[j], Ds[j], dps[j], edges_frey, prof);
  );

  my(slo = max(2, c\2));
  my(shi = 2*c);
  for(k = 1, ncontrols,
    my(rs = random_coprime(slo, shi));
    my(r = rs[1], s = rs[2]);
    my(edges_rand = farey_star(r, s, 2*s + 1));
    for(j = 1, #ells,
      my(prof = edge_profile(M, xp, xm, edges_rand, ells[j]));
      report_residue(label, Strprintf("RAND_%02d", k), r, s, ells[j], Ds[j], dps[j], edges_rand, prof);
    );
  );
  printf("DONE | %s\n", label);
};

setrand(20260506);

print("=== EM-3 MODULAR-SYMBOL RESIDUE PROBE ===");
print("Design: P1 matched-control centers; odd ell only; active ell require D_ell > 1.");

matched_residue_case("1+8=9", 1.226, 1, 8, 20);
matched_residue_case("3+125=128", 1.427, 3, 125, 20);
matched_residue_case("13+243=256", 1.273, 13, 243, 20);
matched_residue_case("1+2400=2401", 1.456, 1, 2400, 20);
matched_residue_case("1+4374=4375", 1.568, 1, 4374, 20);
matched_residue_case("1+6560=6561", 1.235, 1, 6560, 20);

quit;
