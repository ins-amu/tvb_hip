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

data {
  int nn;  //number of brain regions
  int nt;  //number of data points per sensor
  int ns;  //number of sensors

  real dt;    //time step in Euler integration
  real tau0;  //time scale in Eipleptor model
  real I1;    //input current in in Eipleptor model
  real Ks;    //global connectivity parameter

  matrix[nt, ns] Obs_seeg;      // observation at sensor-level
  matrix[nn, nn] SC;           // brain structural connectivity
  matrix[ns, nn] Gr;           // gain (projection matrix)
  matrix[nn, nn] eigen_vec;   // eigen vectors of dot(Gr.T, Gr)

  real amplitude_fixed;
  real offset_offset;
  real offset_tol;
  real eps_tol;
  real eta_spread;
  real eta_offset; 
 
  // ode solving, 2==Stan Heun, 20==C++ Heun
  int ode_solve_order;

  // not used
  real ode_rtol;
  real ode_atol;
  int ode_maxstep;
}

transformed data {
  vector[nt*ns] Obs_seeg_vect;
  Obs_seeg_vect=to_vector(Obs_seeg);
  vector[2*nn] ode_atol_fwd = rep_vector(ode_atol, 2*nn);
}

parameters {
  vector[nn] x_init_star;
  vector[nn] z_init_star;
  vector[nn] eta_star;
  real <lower=-1.0> K_star;
  real <lower=-1.0> amplitude_star;
  vector [ns] offset_star;
  real eps_star;
}

transformed parameters {
  vector[nn] eta;
  vector[nn] x_init;
  vector[nn] z_init;
  real K;
  real amplitude;
  vector[ns] offset;
  real eps;
  
  eta =  eta_offset+eta_spread*eigen_vec*eta_star; // -3.5
  x_init= -2.0 +0.1*eigen_vec*x_init_star;
  z_init= 5.0+0.1*eigen_vec*z_init_star;
  K =  Ks + 0.1*K_star;
  amplitude = amplitude_fixed; // 1.0 + amplitude_star;
  offset=offset_tol * offset_star + offset_offset;
  eps=exp(eps_tol*eps_star); // 0.33
}

model {
  matrix[nn, nt] x;
  matrix[nn, nt] z;
  matrix[nt, ns] Seeg;
  vector[nt*ns] Seeg_vect;
  
  vector[nn] dx;
  vector[nn] dz;
  vector[nn] gx;
  
  /* priors*/
  
  eta_star ~ normal(0.,1.0);  
  x_init_star ~ normal(0.,1.0);
  z_init_star ~ normal(0, 1.0);
  K_star ~ normal(0., 1.);  
  amplitude_star ~ normal(0. ,1.);
  offset_star ~ normal(0.,1.);
  eps_star ~ normal(0.,1.);

  if (ode_solve_order == 2) {
    matrix[2*nn,nt] sol = ode_sol(dt, nt, append_row(x_init, z_init), SC, I1, tau0, K, eta);
    x = sol[1:nn,];
  } else if (ode_solve_order == 20) {
    matrix[2*nn,nt] sol = ode_sol_c(dt, nt, append_row(x_init, z_init), SC, I1, tau0, K, eta);
    x = sol[1:nn,];
  }  

    for(i in 1:nt){
      Seeg[i,]=to_row_vector(amplitude*(Gr*x[,i])+offset);
    }
    Seeg_vect=to_vector(Seeg);
    target += normal_lpdf(Obs_seeg_vect | Seeg_vect, eps);
 
}  

generated quantities {
  
  matrix[nn, nt] x;
  matrix[nn, nt] z;
  
  matrix[nt,ns] Seeg_qqc;
  vector[nt*ns] Seeg_qqc_vect;
  vector[nt*ns] Seeg_ppc;
  vector[nt*ns] log_lik;
  vector[nt] log_lik_sum = rep_vector(0,nt);  

    matrix[2*nn,nt] sol = ode_sol(dt, nt, append_row(x_init, z_init), SC, I1, tau0, K, eta);
    x = sol[1:nn,];
    z = sol[nn+1:,];

  for(i in 1:nt){
    Seeg_qqc[i,]=to_row_vector(amplitude*(Gr*x[,i])+offset);
  }
  
  Seeg_qqc_vect=to_vector(Seeg_qqc);

  for (i in 1:(nt*ns)){
        Seeg_ppc[i] = normal_rng(Seeg_qqc_vect[i], eps);
      }


  for (i in 1:(nt*ns)){
        log_lik[i] = normal_lpdf(Obs_seeg_vect[i]| Seeg_qqc_vect[i], eps);
      }  
  

  for (i in 1:nt){
        for (j in 1:ns)
            log_lik_sum[i] += normal_lpdf(Obs_seeg[i,j]| Seeg_qqc[i,j], eps);
      }   

}
