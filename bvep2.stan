functions {
  vector ode_rhs(real time, vector xz, matrix SC, real I1, real tau0, real K, vector eta) {
    int nn = rows(xz)/2;
    vector[nn] x = xz[1:nn];
    vector[nn] z = xz[nn+1:2*nn];
    vector[nn] gx = SC * x;
    // print(nn, " ", rows(x), " ", rows(z), " ", rows(eta), " ", rows(gx));
    vector[nn] dx = 1.0 - x.*x.*x - 2.0*x.*x - z + I1;
    vector[nn] dz = (1/tau0)*(4*(x - eta) - z - K*gx);
    return append_row(dx, dz);
  }
  
  vector ode_rhs_c(real time, vector xz, matrix SC, real I1, real tau0, real K, vector eta);
}

transformed data {
  matrix[2,2] SC = rep_matrix(0.1, 2, 2);
  real I1 = 3.1;
  real tau0 = 10.0;
  vector[4] xz = rep_vector(0.1, 4);
  real K = 0.1;
  vector[2] eta = rep_vector(-1.0,2);
  vector[4] dx = ode_rhs(0.0,xz,SC,I1,tau0,K,eta);
  vector[4] dx_c = ode_rhs_c(0.0,xz,SC,I1,tau0,K,eta);
  print("fwd sse = ", sum(square(dx - dx_c)));
}

parameters {
  vector[4] xzh;
  real Kh;
  vector[2] etah;
}

model {
  target += sum(ode_rhs_c(0.0,xzh,SC,I1,tau0,Kh,etah));
}
