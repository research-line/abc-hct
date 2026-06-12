triples = [[1,8,9], [1,80,81], [3,125,128], [13,243,256], [1,4374,4375], [1,2400,2401], [625,2048,2673], [1,5831,5832], [49,576,625], [121,2187,2308], [1,9800,9801], [2,6436341,6436343]];

print("idx,a,b,c,orient,N,m,rank,tama,tors,Sha_an");
for(i=1, #triples, t = triples[i]; a = t[1]; b = t[2]; c = t[3]; if(a>b, [a,b]=[b,a]); if(a+b!=c||gcd(a,b)!=1, next); for(orient=1, 2, if(orient==1, E = ellinit([0, b-a, 0, -a*b, 0]); ostr="STD", E = ellinit([0, a-b, 0, -a*b, 0]); ostr="ANC"); Em = ellminimalmodel(E); glob = ellglobalred(Em); N = glob[1]; tama = glob[3]; m = ellmoddegree(Em); rk = ellrank(Em)[1]; tors = elltors(Em)[1]; if(rk == 0, L1 = ellL1(Em); periods = Em.omega; om = abs(real(periods[1])); sha_an = L1 * tors^2 / (om * tama); sha_int = round(sha_an), sha_int = -1); print(i, ",", a, ",", b, ",", c, ",", ostr, ",", N, ",", m, ",", rk, ",", tama, ",", tors, ",", sha_int)));
print("DONE");
quit();
