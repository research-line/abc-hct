\\ Heegner height computation for Reyssat Frey curve
\\ modular degree m_E already confirmed = 4450176000

default(parisize, 1024000000);

E = ellinit([0,1,0,-13808832780322,19750744373708998160]);
Em = ellminimalmodel(E);
N = ellglobalred(Em)[1];
print("CONDUCTOR=", N);

\\ Periods
omega_plus = real(Em.omega[1]);
omega_minus = abs(imag(Em.omega[2]));
print("OMEGA_PLUS=", omega_plus);
print("OMEGA_MINUS=", omega_minus);

\\ Modular degree
m_E = 4450176000;
print("MODDEG=", m_E);
print("MODDEG_FACTOR=", factor(m_E));

\\ Petersson norm squared: ||f||^2 = m_E * Omega+ * |Omega-| (Manin const = 1)
pet = m_E * omega_plus * omega_minus;
print("PETERSSON_NORM_SQ=", pet);

\\ L-values
L_prime = lfun(Em, 1, 1);
print("L_PRIME=", L_prime);

\\ BSD generator height
hat_h_gen = L_prime * 16 / (omega_plus * 800);
print("HAT_H_GEN=", hat_h_gen);

\\ Twist by D=-191 using quadratic twist
Ed191 = elltwist(Em, -191);
Ed191 = ellinit(Ed191);
L_d191 = lfun(Ed191, 1);
print("L_TWIST_D191=", L_d191);

GZ_prod = L_prime * L_d191;
print("GZ_PRODUCT_D191=", GZ_prod);

\\ Gross-Zagier formula (Q-height of Heegner trace point):
\\ hat{h}_Q(y_K) = GZ_prod * sqrt(|D|) / (8 * Pi^2 * ||f||^2)
\\ (u_K = 1 for |D| > 4)
D = 191;
h_K = 13;
hat_h_yK = GZ_prod * sqrt(D) / (8 * Pi^2 * pet);
print("HAT_H_YK_D191_RAW=", hat_h_yK);

\\ Heegner index: y_K = I * P_gen (mod tors), so hat{h}(y_K) = I^2 * hat{h}(P_gen)
I_sq = hat_h_yK / hat_h_gen;
print("HEEGNER_INDEX_SQ=", I_sq);

\\ Alternative: with class number h_K^2 factor
\\ Some normalizations include h_K: y_K = sum over Cl(K), giving h_K * base point
\\ Then hat{h}(y_K) = h_K^2 * hat{h}(x_0)
\\ But y_K as defined IS the class group sum, so no extra factor

\\ Try D=-31 for comparison
Ed31 = elltwist(Em, -31);
Ed31 = ellinit(Ed31);
L_d31 = lfun(Ed31, 1);
GZ_31 = L_prime * L_d31;
hat_h_31 = GZ_31 * sqrt(31) / (8 * Pi^2 * pet);
print("HAT_H_YK_D31=", hat_h_31);

\\ Required height for abc bound
log_N = log(2*3*23*109);
q_eff = 1.3918875019567794732343982471818332444;
req = (q_eff - 1) * log_N / 2;
print("REQUIRED_LOG_HEIGHT=", req);
print("HAT_H_YK_D191_LOG=", log(hat_h_yK));
print("RATIO_D191=", hat_h_yK / exp(req));

\\ Try ellheegner (direct Heegner point computation)
print("COMPUTING_ELLHEEGNER...");
iferr(
  P = ellheegner(Em);
  print("HEEGNER_POINT=", P);
  print("HEEGNER_HEIGHT=", ellheight(Em, P));
, e,
  print("ELLHEEGNER_ERROR=", e)
);

print("DONE");
