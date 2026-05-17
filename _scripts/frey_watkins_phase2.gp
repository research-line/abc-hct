triples = [[1,8,9], [1,80,81], [3,125,128], [32,49,81], [13,243,256], [5,27,32], [1,48,49], [1,99,100], [1,288,289], [1,728,729], [625,2048,2673], [1,2400,2401], [1,5831,5832], [3,1024,1027], [2,6436341,6436343]];

for(i=1, #triples, t = triples[i]; a = t[1]; b = t[2]; c = t[3]; if(a+b != c || gcd(a,b) != 1, print("SKIP: ", t); next()); E = ellinit([0, b-a, 0, -a*b, 0]); Em = ellminimalmodel(E); N = ellglobalred(Em)[1]; m = ellmoddegree(Em); rv = ellrank(Em); rk = rv[1]; ratio = log(1.0*m)/log(1.0*N); print(a, "+", b, "=", c, " | N=", N, " | m=", m, " | rank=", rk, " | log_m/log_N=", precision(ratio, 5)); );
print("DONE");
quit();
