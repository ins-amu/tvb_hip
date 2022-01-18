type bvep_data [nt] [ns] [nn] = {
  sEEG: [nt][ns]f32,
  SC: [nn][nn]f32,
  gain: [ns][nn]f32,
  dt: f32,
  tau0: f32,
  I1: f32
}

entry mk_bvep_data [nt][ns][nn]
  (sEEG: [nt][ns]f32)
  (SC: [nn][nn]f32)
  (gain: [ns][nn]f32)
  (dt: f32)
  (tau0: f32)
  (I1: f32)
  : bvep_data[nt][ns][nn] =
    {sEEG=sEEG, SC=SC, gain=gain, dt=dt, tau0=tau0, I1}

type bvep_parm [ns] [nn] = { eta:[nn]f32, eps:f32, x_init:[nn]f32, z_init:[nn]f32, amp: f32, off:[ns]f32, K:f32 }

entry mk_bvep_parm [ns] [nn] (eta:[nn]f32) (eps:f32) (x_init:[nn]f32) (z_init:[nn]f32) (amp: f32) (off:[ns]f32) (K:f32)
  : bvep_parm [ns][nn] = 
  {eta=eta, eps=eps, x_init=x_init, z_init=z_init, amp=amp, off=off, K=K}

entry dfun [nn] (I1:f32) (tau0:f32) (K:f32) (SC:[nn][nn]f32) (x:[nn]f32) (z:[nn]f32) (eta:[nn]f32): ([nn]f32,[nn]f32) =
  let gx = map (\sc -> map2 (*) sc x |> reduce (+) 0f32) SC
  let dx = map2 (\x z -> 1f32 - x*x*x - 2*x*x - z + I1) x z
  let dz = map4 (\x z g e -> (1f32/tau0)*(4f32*(x - e) - z - K*g)) x z gx eta
  in (dx, dz)

entry bvep_step [nt][ns][nn] (d:bvep_data[nt][ns][nn]) (p:bvep_parm[ns][nn]) x z: ([nn]f32,[nn]f32) =
  -- k1 = f(y)
  let (dx1, dz1) = dfun d.I1 d.tau0 p.K d.SC x z p.eta

  -- k2 = f(y + dt*k1/2)
  let f1 x dx = map2 (\x dx -> x + d.dt * dx / 2) x dx
  let x1 = f1 x dx1
  let z1 = f1 z dz1
  let (dx2, dz2) = dfun d.I1 d.tau0 p.K d.SC x1 z1 p.eta

  -- k3 = f(y + dt*k2/2)
  let x2 = f1 x dx2
  let z2 = f1 z dz2
  let (dx3, dz3) = dfun d.I1 d.tau0 p.K d.SC x2 z2 p.eta

  -- k4 = f(y + dt*k3)
  let f2 x dx = map2 (\x dx -> x + d.dt * dx) x dx
  let x3 = f1 x dx3
  let z3 = f1 z dz3
  let (dx4, dz4) = dfun d.I1 d.tau0 p.K d.SC x3 z3 p.eta

  -- yn = y + dt/6*(k1 + 2*k2 + 2*k3 + k4)
  let f2 x k1 k2 k3 k4 = map5 (\x k1 k2 k3 k4 -> x + d.dt/6*(k1+2*k2+2*k3+k4)) x k1 k2 k3 k4
  let x4 = f2 x dx1 dx2 dx3 dx4
  let z4 = f2 z dz1 dz2 dz3 dz4
  in (x4, z4)

entry bvep_fwd [ns][nn] (gain:[ns][nn]f32) (amp:f32) (x:[nn]f32) (off:[ns]f32): [ns]f32 =
  let one g o = map2 (*) g x |> reduce (+) 0f32 |> (*amp) |> (+o)
  in map2 one gain off

entry norm_lpdf (x:f32) (mu:f32) (sd:f32): f32 =
  let a = f32.log sd
  let b = (f32.log (2 * f32.pi)) / 2
  let c = (x - mu) / sd
  let d = c * c / 2
  in -a - b - d

entry bvep_seeg_err [ns] (seeg_mu:[ns]f32) (seeg_obs:[ns]f32) (eps:f32): f32 =
  map2 (\x y -> norm_lpdf y x eps) seeg_mu seeg_obs |> reduce (+) 0f32

entry bvep_loss [nt][ns][nn] (data:bvep_data[nt][ns][nn]) (parm:bvep_parm[ns][nn]): f32 =
  let s0 = bvep_fwd data.gain parm.amp parm.x_init parm.off
  let l0 = bvep_seeg_err s0 data.sEEG[0] parm.eps
  let (l,_,_) = loop (l,x,z) = (l0, parm.x_init, parm.z_init)
    for i < (nt - 1) do
      let (x,z) = bvep_step data parm x z
      let seeg_mu = bvep_fwd data.gain parm.amp x parm.off
      let serr = bvep_seeg_err seeg_mu data.sEEG[i+1] parm.eps
      in (l + serr,x,z)
  in l

entry bvep_grad_loss [nt][ns][nn] (data:bvep_data[nt][ns][nn]) (parm:bvep_parm[ns][nn]): bvep_parm[ns][nn] =
  vjp (bvep_loss data) parm 1f32

-- then a bunch of packing / unpacking stuff
