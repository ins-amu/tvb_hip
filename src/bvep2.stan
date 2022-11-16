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

  vector ode_step(real time, real dt, vector xz, matrix SC, real I1, real tau0, real K, vector eta) {
    vector[rows(xz)] d1 = ode_rhs(time,xz,SC,I1,tau0,K,eta);
    vector[rows(xz)] d2 = ode_rhs(time+dt, xz+dt*d1,SC,I1,tau0,K,eta);
    return xz + dt / 2 * (d1 + d2);
  }

  vector ode_step_c(real time, real dt, vector xz, matrix SC, real I1, real tau0, real K, vector eta);

  matrix ode_sol_c(real dt, int nt, vector xz, matrix SC, real I1, real tau0, real K, vector eta);

  matrix ode_sol(real dt, int nt, vector xz, matrix SC, real I1, real tau0, real K, vector eta) {
    matrix[rows(xz),nt] sol;
    sol[,1] = xz;
    for (t in 1:(nt - 1)) {
      sol[,t+1] = ode_step(t*dt, dt, sol[,t], SC, I1, tau0, K, eta);
    }
    return sol;
  }

}

transformed data {
  real dt = 0.1;
  int nt = 3;
  matrix[2,2] SC = rep_matrix(0.1, 2, 2);
  real I1 = 3.1;
  real tau0 = 10.0;
  vector[4] xz = rep_vector(0.1, 4);
  real K = 0.1;
  vector[2] eta = rep_vector(-1.0,2);
  vector[4] dx = ode_rhs(0.0,xz,SC,I1,tau0,K,eta);
  vector[4] dx_c = ode_rhs_c(0.0,xz,SC,I1,tau0,K,eta);
  print("rhs sse = ", sum(square(dx - dx_c)));
  vector[4] nx = ode_step(0.0,dt,xz,SC,I1,tau0,K,eta);
  vector[4] nx_c = ode_step_c(0.0,dt,xz,SC,I1,tau0,K,eta);
  print("step sse = ", sum(square(nx - nx_c)));
  matrix[4,3] sol = ode_sol(dt, nt, xz, SC, I1, tau0, K, eta);
  matrix[4,3] sol_c = ode_sol_c(dt, nt, xz, SC, I1, tau0, K, eta);
  print("sol sse = ", sum(square(to_vector(sol) - to_vector(sol_c))));
}

parameters {
  // distinct parameter sets for different c++ functions allows
  // checking them in parallel.
  // for ode_rhs_c
  vector[4] xzh_rhs;
  real Kh_rhs;
  vector[2] etah_rhs;
  // for ode_step_c
  vector[4] xzh_step;
  real Kh_step;
  vector[2] etah_step;
  // for ode_sol_c
  vector[4] xzh_sol;
  real Kh_sol;
  vector[2] etah_sol;
}

model {
  target += sum(ode_rhs_c(0.0,xzh_rhs,SC,I1,tau0,Kh_rhs,etah_rhs));
  target += sum(ode_step_c(0.0,dt,xzh_step,SC,I1,tau0,Kh_step,etah_step));
  target += sum(ode_sol_c(dt,nt,xzh_sol,SC,I1,tau0,Kh_sol,etah_sol));
}
