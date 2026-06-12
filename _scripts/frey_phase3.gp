triples = [[1,8,9], [1,80,81], [3,125,128], [32,49,81], [13,243,256], [5,27,32], [1,48,49], [1,99,100], [1,288,289], [1,728,729], [625,2048,2673], [1,2400,2401], [1,5831,5832], [3,1024,1027], [2,6436341,6436343], [1,624,625], [9,16,25], [1,15624,15625], [1,143,144], [1,575,576], [49,576,625], [1,168,169], [1,224,225], [4,121,125], [27,32,59], [1,4374,4375], [4,729,733], [1,4095,4096], [1,1023,1024], [1,2047,2048], [1,8191,8192], [1,323,324], [1,440,441], [1,675,676], [3,4096,4099], [1,3124,3125], [16,243,259], [1,9800,9801], [4,243,247], [121,2187,2308], [1,124,125]];

processed = List();
for(i=1, #triples, t = triples[i]; a = t[1]; b = t[2]; c = t[3]; if(a>b, [a,b] = [b,a]); if(a+b != c, next); if(gcd(a,b) != 1, next); key = [a,b,c]; found = 0; for(j=1, #processed, if(processed[j] == key, found=1; break)); if(!found, listput(processed, key)));

print("count=", #processed);
print("idx,a,b,c,N,m,rank,tama,q,rho,delta");
for(i=1, #processed, t = processed[i]; a = t[1]; b = t[2]; c = t[3]; E = ellinit([0, b-a, 0, -a*b, 0]); Em = ellminimalmodel(E); glob = ellglobalred(Em); N = glob[1]; tama = glob[3]; m = ellmoddegree(Em); rk = ellrank(Em)[1]; n = abs(a*b*c); rad = 1; d = 2; while(d*d <= n, if(n%d == 0, rad = rad*d; while(n%d == 0, n = n\d)); d = d+1); if(n > 1, rad = rad*n); q = log(1.0*c)/log(1.0*rad); rho = log(1.0*m)/log(1.0*N); delta = rho - (q - 1); print(i, ",", a, ",", b, ",", c, ",", N, ",", m, ",", rk, ",", tama, ",", precision(q,5), ",", precision(rho,5), ",", precision(delta,5)));
print("DONE");
quit();
