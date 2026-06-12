\\ EM-1b: Conductor, Kodaira type, root number for Frey curves
\\ Uses ellglobalred, elllocalred, ellminimalmodel, ellrootno
\\ Run: gp -s 1G -q em1b_pari_p2.gp

frey_curve(a, b) = ellinit([0, b-a, 0, -a*b, 0]);

kodaira_name(kod) =
{
  if(kod == 1, return("I_0"));
  if(kod >= 5, return(Strprintf("I_%d", kod - 4)));
  if(kod <= -5, return(Strprintf("I*_%d", -kod - 4)));
  if(kod == 2, return("II"));
  if(kod == 3, return("III"));
  if(kod == 4, return("IV"));
  if(kod == -1, return("I*_0"));
  if(kod == -2, return("IV*"));
  if(kod == -3, return("III*"));
  if(kod == -4, return("II*"));
  return(Strprintf("unknown_%d", kod));
};

analyze_triple(label, a, b) =
{
  my(c = a + b);
  my(E = frey_curve(a, b));
  my(gr = ellglobalred(E));
  my(N_cond = gr[1]);
  my(lr2 = elllocalred(E, 2));
  my(f2 = lr2[1]);
  my(kod2 = lr2[2]);
  my(c2_tam = lr2[4]);
  my(w = ellrootno(E));
  my(Emin = ellminimalmodel(E));
  my(v2_Delta_min = valuation(Emin.disc, 2));
  my(semistable = (f2 <= 1));

  printf("{\"label\": \"%s\", ", label);
  printf("\"a\": %d, \"b\": %d, \"c\": %d, ", a, b, c);
  printf("\"N_cond\": %d, ", N_cond);
  printf("\"f2\": %d, ", f2);
  printf("\"kodaira_p2\": \"%s\", ", kodaira_name(kod2));
  printf("\"c2_tam\": %d, ", c2_tam);
  printf("\"root_number\": %d, ", w);
  printf("\"semistable_at_2\": %d, ", semistable);
  printf("\"v2_abc\": %d, ", valuation(a*b*c, 2));
  printf("\"v2_Delta_min\": %d", v2_Delta_min);
  printf("}\n");
};

analyze_triple("Reyssat", 2, 3^10*109);
analyze_triple("ABCHome_2", 11^2, 3^2*5^6*7^3);
analyze_triple("classic_4374", 1, 2*3^7);
analyze_triple("classic_2401", 1, 2400);
analyze_triple("1+8=9", 1, 8);
analyze_triple("1+63=64", 1, 63);
analyze_triple("1+80=81", 1, 80);
analyze_triple("5+27=32", 5, 27);
analyze_triple("3+125=128", 3, 125);
analyze_triple("13+243=256", 13, 243);
analyze_triple("32+49=81", 32, 49);
analyze_triple("1+4374=4375_dup", 1, 4374);
analyze_triple("1+4095=4096", 1, 2^12-1);
analyze_triple("625+2048=2673", 625, 2048);
analyze_triple("1+1023=1024", 1, 1023);

quit;
