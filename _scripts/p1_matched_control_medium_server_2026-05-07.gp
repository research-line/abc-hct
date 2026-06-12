\\ P1 Matched-Control: medium/large cases (top max_frame triples)
\\ Extension of pilot. Run: gp -s 2G -q < p1_matched_control_medium.gp
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

max_frame(M, xp, xm, edges) =
{
  my(mf = 0.0);
  for(i = 1, #edges,
    my(vp = mseval(M, xp, edges[i]));
    my(vm = mseval(M, xm, edges[i]));
    mf = max(mf, max(absreal(vp), absreal(vm)));
  );
  mf;
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

matched_control(label, qabc, a, b, ncontrols) =
{
  my(c = a + b);
  printf("START | %s | computing msfromell...\n", label);
  my(E = frey_curve(a, b));
  my(N = ellglobalred(E)[1]);
  my(ms = msfromell(E, 0));
  my(M = ms[1]);
  my(x = ms[2]);
  my(xp = x[1]);
  my(xm = x[2]);
  my(d = msdim(M));
  printf("INIT | %s | Ncond=%d | dim=%d | msfromell done\n", label, N, d);

  my(H_frey = 2*c + 1);
  my(edges_frey = farey_star(a, c, H_frey));
  my(mf_frey = max_frame(M, xp, xm, edges_frey));
  printf("FREY | %s | q=%.3f | Ncond=%d | dim=%d | H=%d | edges=%d | max_frame=%.6f\n",
         label, qabc, N, d, H_frey, #edges_frey, mf_frey);

  my(slo = max(2, c\2));
  my(shi = 2*c);
  my(frames = vector(ncontrols));

  for(k = 1, ncontrols,
    my(rs = random_coprime(slo, shi));
    my(r = rs[1], s = rs[2]);
    my(H_rand = 2*s + 1);
    my(edges_rand = farey_star(r, s, H_rand));
    my(mf_rand = max_frame(M, xp, xm, edges_rand));
    frames[k] = mf_rand;
    printf("RAND_%02d | %s | center=%d/%d | H=%d | edges=%d | max_frame=%.6f\n",
           k, label, r, s, H_rand, #edges_rand, mf_rand);
  );

  my(sorted_f = vecsort(frames));
  my(n = #frames);
  my(mean_f = vecsum(frames) / n);
  my(median_f = sorted_f[(n+1)\2]);
  my(var_f = sum(i=1, n, (frames[i] - mean_f)^2) / max(1, n-1));
  my(std_f = sqrt(var_f + 0.0));
  my(p95_idx = max(1, ceil(0.95 * n)));
  my(p95_f = sorted_f[p95_idx]);
  my(z = if(std_f > 0.001, (mf_frey - mean_f) / std_f, 999.0));

  printf("STATS | %s | frey_frame=%.6f | mean_rand=%.6f | median_rand=%.6f | std_rand=%.6f | p95_rand=%.6f | z_score=%.3f | above_p95=%d\n\n",
         label, mf_frey, mean_f, median_f, std_f, p95_f, z, mf_frey > p95_f);
};

setrand(20260506);

print("=== P1 MATCHED-CONTROL MEDIUM (20 random centers each) ===");
print("");

\\ 1+2400=2401: dim=769, frame=28 (medium)
matched_control("1+2400=2401", 1.456, 1, 2400, 20);

\\ 1+4374=4375: dim=1537, frame=63 (highest quality)
matched_control("1+4374=4375", 1.568, 1, 4374, 20);

\\ 1+6560=6561: dim=4033, frame=48 (former null case, H=2c+1 star)
matched_control("1+6560=6561", 1.235, 1, 6560, 20);

quit;
