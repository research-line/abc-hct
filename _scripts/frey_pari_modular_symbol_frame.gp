\\ Frey modular-symbol frame probe via PARI/GP.
\\
\\ This executes the P1 test without Sage. PARI's msfromell(E) returns
\\ period-normalized modular symbols x^+ and x^- attached to the elliptic
\\ curve E/Q. For Frey curves y^2 = x(x-a)(x+b), we evaluate x^\pm along
\\ the canonical Farey path from 0 to lambda=a/c.

\\p 50

absreal(x) = abs(x + 0.0);

pathstr(p) = Strprintf("[%Ps,%Ps]", p[1], p[2]);

frey_curve(a, b) = ellinit([0, b-a, 0, -a*b, 0]);

report_symbol_frame(label, a, b, paths) =
{
  my(c = a + b);
  my(E = frey_curve(a, b));
  my(N = ellglobalred(E)[1]);
  my(w = ellrootno(E));
  my(ms = msfromell(E, 0));
  my(M = ms[1]);
  my(x = ms[2]);
  my(xp = x[1]);
  my(xm = x[2]);
  my(windp = mseval(M, xp, [0, oo]));
  my(windm = mseval(M, xm, [0, oo]));
  my(maxp = 0.0, maxm = 0.0, maxboth = 0.0);
  my(top = 0);
  my(top_p = 0, top_m = 0);

  print("------------------------------------------------------------");
  printf("%s | a=%d b=%d c=%d Ncond=%d rootno=%d dim=%d\n",
         label, a, b, c, N, w, msdim(M));
  printf("winding xplus[0,oo]=%Ps  xminus[0,oo]=%Ps\n", windp, windm);
  printf("edge_count=%d\n", #paths);
  print("edge | path | xplus | xminus | max_abs");

  for(i = 1, #paths,
    my(vp = mseval(M, xp, paths[i]));
    my(vm = mseval(M, xm, paths[i]));
    my(ap = absreal(vp));
    my(am = absreal(vm));
    my(ab = max(ap, am));
    printf("%d | %s | %Ps | %Ps | %.12g\n", i, pathstr(paths[i]), vp, vm, ab);
    if(ap > maxp, maxp = ap);
    if(am > maxm, maxm = am);
    if(ab > maxboth,
      maxboth = ab;
      top = i;
      top_p = vp;
      top_m = vm;
    );
  );

  printf("SUMMARY | %s | max_xplus=%.12g | max_xminus=%.12g | max_frame=%.12g | top_edge=%d | top_xplus=%Ps | top_xminus=%Ps\n",
         label, maxp, maxm, maxboth, top, top_p, top_m);
};

\\ Core Frey triples from the abc project.
\\ Paths are consecutive convergent edges from the continued fraction of a/c.

report_symbol_frame("1+8=9", 1, 8, [[0, 1/9]]);

report_symbol_frame("3+125=128", 3, 125, [[0, 1/42], [1/42, 1/43], [1/43, 3/128]]);

report_symbol_frame("13+243=256", 13, 243, [[0, 1/19], [1/19, 1/20], [1/20, 2/39], [2/39, 13/256]]);

report_symbol_frame("1+2400=2401", 1, 2400, [[0, 1/2401]]);

report_symbol_frame("1+4374=4375", 1, 4374, [[0, 1/4375]]);

\\ Reyssat is intentionally not run by default: conductor 240672 overflows
\\ a 512 MB PARI stack in this environment. Use the dedicated Reyssat script
\\ with a multi-GB stack if needed.

quit;
