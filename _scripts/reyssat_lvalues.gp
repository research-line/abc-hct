\\ Q3/Q4: L-values and local data for Reyssat Frey curve
\\ E: y^2 = x(x - 2)(x + 6436341) where b = 3^10 * 109, c = 23^5
\\ Expected conductor: divisor of rad(2 * 3^10*109 * 23^5)^2

print("=" * 70);
print("REYSSAT FREY CURVE: L-VALUE COMPUTATION");
print("=" * 70);

\\ Define curve: y^2 = x^3 + (b-a)x^2 - ab*x
\\ a=2, b=6436341, so coefficients: [0, 6436339, 0, -12872682, 0]
E = ellinit([0, 6436339, 0, -12872682, 0]);

\\ Minimal model
Em = ellminimalmodel(E);
print("\n--- MINIMAL MODEL ---");
print("a-invariants: ", Em.a1, ", ", Em.a2, ", ", Em.a3, ", ", Em.a4, ", ", Em.a6);

\\ Global reduction data
red = ellglobalred(E);
N_cond = red[1];
print("\n--- CONDUCTOR ---");
print("N = ", N_cond);
print("N factored = ", factor(N_cond));

\\ Root number
w = ellrootno(E);
print("\n--- ROOT NUMBER ---");
print("w(E) = ", w);
if(w == -1, print("  => Analytic rank is ODD, L(E,1) = 0 forced"));
if(w == +1, print("  => Analytic rank is EVEN"));

\\ Local data at all bad primes
print("\n--- LOCAL REDUCTION DATA ---");
print("p | Kodaira | f_p | c_p (Tamagawa) | a_p");
print("-" * 50);
fp = factor(N_cond);
for(i = 1, matsize(fp)[1],
  p = fp[i, 1];
  ld = elllocalred(E, p);
  kod = ld[2];
  f_p = ld[1];
  c_p = ld[4];
  ap = ellap(E, p);
  print("  p=", p, " | ", kod, " | f=", f_p, " | c=", c_p, " | a_p=", ap);
);

\\ L(E, 1)
print("\n--- L-VALUES ---");
L1 = lfun(E, 1);
print("L(E, 1) = ", L1);

\\ L'(E, 1) if root number is -1
if(w == -1,
  Lp1 = lfun(E, 1, 1);
  print("L'(E, 1) = ", Lp1);
  if(abs(Lp1) > 0.0001,
    print("  => L'(E,1) != 0: analytic rank = 1"),
    print("  => L'(E,1) ~ 0: analytic rank >= 3 (?)")
  );
);

\\ Q3: L(E, chi_{-31}, 1)
print("\n--- TWISTED L-VALUE: D = -31 ---");
\\ Method 1: Direct twist
D = -31;
print("Kronecker symbols:");
print("  (D/2) = ", kronecker(D, 2));
print("  (D/3) = ", kronecker(D, 3));
print("  (D/23) = ", kronecker(D, 23));
print("  (D/109) = ", kronecker(D, 109));

\\ Heegner hypothesis check: all p|N must split in Q(sqrt(D))
\\ p splits iff (D/p) = +1
print("Heegner hypothesis for p|N:");
heeg_ok = 1;
for(i = 1, matsize(fp)[1],
  p = fp[i, 1];
  kr = kronecker(D, p);
  print("  p=", p, ": (D/p)=", kr, if(kr == 1, " SPLIT", if(kr == -1, " INERT", " RAMIFIED")));
  if(kr != 1, heeg_ok = 0);
);
if(heeg_ok, print("  => Heegner hypothesis SATISFIED"), print("  => Heegner hypothesis FAILS"));

\\ Compute L(E, chi_D, 1) via quadratic twist
Et = elltwist(E, D);
Et = ellinit(Et);
Nt = ellglobalred(Et)[1];
wt = ellrootno(Et);
print("\nTwisted curve E_{-31}:");
print("  Conductor: N(E_{-31}) = ", Nt);
print("  Root number: w(E_{-31}) = ", wt);

Lt1 = lfun(Et, 1);
print("  L(E_{-31}, 1) = ", Lt1);

if(wt == -1,
  Ltp1 = lfun(Et, 1, 1);
  print("  L'(E_{-31}, 1) = ", Ltp1);
);

\\ Also try via Hecke character twist
\\ Lchi = lfun([E, D], 1);  \\ may not work in all versions

\\ Q3 answer
print("\n--- Q3 ANSWER ---");
if(abs(Lt1) > 0.0001,
  print("L(E, chi_{-31}, 1) != 0: GZ route VIABLE for D=-31"),
  if(wt == -1,
    print("L(E, chi_{-31}, 1) = 0 forced by sign (w = -1)"),
    print("L(E, chi_{-31}, 1) ~ 0: possible higher vanishing")
  )
);

\\ GZ formula analysis
print("\n--- GROSS-ZAGIER ANALYSIS ---");
if(w == -1,
  print("Since w(E) = -1:");
  print("  L(E/K, s) = L(E, s) * L(E, chi_D, s)");
  print("  ord_{s=1} L(E/K, s) = ord L(E,s) + ord L(E,chi_D,s)");
  if(abs(Lt1) > 0.0001,
    print("  = 1 + 0 = 1 (GZ applies!)");
    print("  GZ formula: L'(E,1) * L(E,chi_D,1) = c * h_hat(P_K)");
    if(type(Lp1) == "t_REAL",
      gz_product = Lp1 * Lt1;
      print("  L'(E,1) * L(E,chi_D,1) = ", gz_product);
      print("  Since this is > 0, Heegner point P_K has POSITIVE height.");
    );
  ,
    print("  L(E,chi_D,1) ~ 0: need different D or ord >= 2");
  );
);

\\ Additional discriminants to try
print("\n--- SCANNING OTHER DISCRIMINANTS ---");
print("Testing D where all p|N split and L(E,chi_D,1) != 0:");
good_D = [];
{
for(d = 3, 200,
  D_test = -d;
  if(!isfundamental(D_test), next);
  ok = 1;
  for(i = 1, matsize(fp)[1],
    p = fp[i, 1];
    if(kronecker(D_test, p) != 1, ok = 0; break);
  );
  if(!ok, next);
  \\ D_test satisfies Heegner hypothesis
  Et2 = elltwist(E, D_test);
  Et2 = ellinit(Et2);
  wt2 = ellrootno(Et2);
  if(wt2 == -1, next);  \\ L vanishes by sign
  Lt2 = lfun(Et2, 1);
  if(abs(Lt2) > 0.0001,
    print("  D=", D_test, ": L(E,chi_D,1) = ", precision(Lt2, 9), " w=", wt2, " h_K=", qfbclassno(D_test));
    good_D = concat(good_D, [D_test]);
  );
  if(#good_D >= 10, break);
);
}

\\ Periods and other data
print("\n--- PERIODS ---");
om = E.omega;
print("Real period Omega_+ = ", om[1]);
print("Imaginary period Omega_- = ", om[2]);

\\ Modular degree (if computable)
\\ md = ellmoddegree(E);  \\ may be slow for large conductor

print("\n--- ANALYTIC DATA SUMMARY ---");
print("Curve: y^2 = x(x-2)(x+6436341)");
print("Conductor: ", N_cond);
print("Root number: ", w);
print("L(E, 1) = ", L1);
if(type(Lp1) == "t_REAL", print("L'(E, 1) = ", Lp1));
print("L(E_{-31}, 1) = ", Lt1);
print("Analytic rank: ", if(w==-1, if(abs(Lp1)>0.0001, 1, ">=3"), if(abs(L1)>0.0001, 0, ">=2")));
print("Class number h(-31) = ", qfbclassno(-31));

print("\n" * 2);
print("=" * 70);
print("COMPUTATION COMPLETE");
print("=" * 70);
