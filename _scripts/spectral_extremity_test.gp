\\ Spectral Extremity Discriminating Check
\\ Test: Does L'(E,1)/N^{1/4} correlate monotonically with abc quality q?
\\ Frey curve: E_{a,b}: y^2 = x^3 + (b-a)*x^2 - a*b*x

default(parisize, 256000000);

rad(n) = {
  my(f = factor(n), r = 1);
  for(i = 1, matsize(f)[1], r *= f[i,1]);
  r;
};

quality(a, b) = {
  my(c = a + b);
  log(c) / log(rad(a * b * c));
};

test_triple(a, b, label) = {
  my(c = a + b);
  my(q = quality(a, b));
  my(E = ellinit([0, b - a, 0, -a * b, 0]));
  my(Em = ellminimalmodel(E));
  my(N_E = ellglobalred(Em)[1]);
  my(Le = lfuninit(Em, [0, 1], 1));
  my(w = ellrootno(Em));
  my(Lval, ratio);
  if(w == -1,
    Lval = lfun(Le, 1, 1);  \\ L'(E,1)
    ratio = Lval / N_E^(1/4);
    printf("TRIPLE=%s q=%.6f N=%d w=%d L'(E,1)=%.10f L'/N^{1/4}=%.10f\n",
           label, q, N_E, w, Lval, ratio);
  ,
    Lval = lfun(Le, 1);  \\ L(E,1)
    ratio = Lval / N_E^(1/4);
    printf("TRIPLE=%s q=%.6f N=%d w=%d L(E,1)=%.10f L/N^{1/4}=%.10f\n",
           label, q, N_E, w, Lval, ratio);
  );
};

print("SPECTRAL_EXTREMITY_TEST_START");

{
triples = [
  [1, 2, "1+2=3"],
  [1, 8, "1+8=9"],
  [1, 48, "1+48=49"],
  [1, 63, "1+63=64"],
  [1, 80, "1+80=81"],
  [1, 1023, "1+1023=1024"],
  [1, 2400, "1+2400=2401"],
  [1, 4374, "1+4374=4375"],
  [1, 6560, "1+6560=6561"],
  [2, 109, "2+109=111"],
  [3, 125, "3+125=128"],
  [5, 27, "5+27=32"],
  [7, 2187, "7+2187=2194"],
  [13, 243, "13+243=256"],
  [32, 49, "32+49=81"],
  [2, 6859, "2+6859=6861"],
  [1, 191, "1+191=192"],
  [2, 3^10*109, "Reyssat"],
  [1, 4095, "1+4095=4096"],
  [11, 32, "11+32=43"],
  [1, 3071, "1+3071=3072"],
  [343, 2048, "343+2048=2391"],
  [1, 32767, "1+32767=32768"],
  [1, 78124, "1+78124=78125"],
  [2187, 131072, "2187+131072=133259"],
  [1, 14348906, "1+14348906=14348907"],
  [16, 2171, "16+2171=2187"],
  [1, 531440, "1+531440=531441"]
];

for(i = 1, #triples,
  iferr(
    test_triple(triples[i][1], triples[i][2], triples[i][3]),
    E, printf("ERROR: %s failed: %s\n", triples[i][3], E)
  );
);
}

print("SPECTRAL_EXTREMITY_TEST_END");
