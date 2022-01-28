import timeit
from functools import partial
from autograd import grad, numpy as np
from autograd.extend import primitive, defvjp
from autograd.scipy.stats.norm import logpdf as normal_lpdf
from autograd.test_util import check_grads

npz = np.load('bvep.npz')
globals().update(npz)

@primitive
def ode_rhs(xz, eta, K):#, SC, I1, tau0):
    nn = xz.size // 2
    x, z = xz[:nn], xz[nn:]
    gx = np.dot(SC, x)
    dx = 1 - x**3 - 2*x**2 - z + I1
    dz = (1/tau0)*(4*(x - eta) - z - K*gx)
    return np.concatenate([dx, dz])

def vjp(f):
    def _(ans, *args):
        return lambda g: f(g, *args)
    _.f = f
    return _

@vjp
def ode_rhs_eta(g, xz, eta, K):
    nn = xz.size // 2
    x, _ = xz[:nn], xz[nn:]
    _, g_dz = g[:nn], g[nn:]
    return g_dz * (-4/tau0)

@vjp
def ode_rhs_xz(g, xz, eta, K):
    "this is just g @ J_{xz,eta,K}, automate w/ sympy"
    # unpack
    nn = xz.size // 2
    x, _ = xz[:nn], xz[nn:]
    g_dx, g_dz = g[:nn], g[nn:]
    # jac of gx wrt x
    g_gx_x = SC
    # grad wrt x & z via dx
    g_dx_x = g_dx * (-3*x**2 - 4*x)
    g_dx_z = g_dx * (-1)
    # grad wrt x, z, eta, K via dz
    g_dz_x = g_dz*4/tau0 - K/tau0*np.dot(g_dz, g_gx_x)
    g_dz_z = g_dz * (-1/tau0)
    # cumulative grads for states & params
    g_x = g_dx_x + g_dz_x
    g_z = g_dx_z + g_dz_z
    return np.concatenate([g_x, g_z])

@vjp
def ode_rhs_K(g, xz, eta, K):
    nn = xz.size // 2
    x, _ = xz[:nn], xz[nn:]
    _, g_dz = g[:nn], g[nn:]
    gx = np.dot(SC, x)
    return -np.sum(g_dz * gx / tau0)
    
defvjp(ode_rhs, ode_rhs_xz, ode_rhs_eta, ode_rhs_K)

nn = SC.shape[0]
xz = np.ones(2*nn)*0.2
eta = np.ones(nn)*0.2
K = 0.2

check_grads(lambda xz: ode_rhs(xz, eta, K), modes=['rev'])(xz)
check_grads(lambda eta: ode_rhs(xz, eta, K), modes=['rev'])(eta)
check_grads(lambda K: ode_rhs(xz, eta, K), modes=['rev'])(K)
print('rhs ok')

@primitive
def ode_euler_step(xz, eta, K):
    return xz + dt * ode_rhs(xz, eta, K)

@vjp
def ode_euler_step_x(g, x, e, k): return g + ode_rhs_xz.f(g*dt,x,e,k)

@vjp
def ode_euler_step_e(g, x, e, k): return ode_rhs_eta.f(g*dt, x, e, k)

@vjp
def ode_euler_step_k(g, x, e, k): return ode_rhs_K.f(g*dt, x, e, k)

defvjp(ode_euler_step, ode_euler_step_x, ode_euler_step_e, ode_euler_step_k)

def check_grads_step(step):
    print('check', 'x')
    check_grads(lambda x: step(x, eta, K), modes=['rev'])(xz)
    print('check', 'e')
    check_grads(lambda e: step(xz, e, K), modes=['rev'])(eta)
    print('check', 'k')
    check_grads(lambda k: step(xz, eta, k), modes=['rev'])(K)

check_grads_step(ode_euler_step)
print('euler ok')

@primitive
def ode_heun_step(x, e, k):
    d1 = ode_rhs(x, e, k)
    d2 = ode_rhs(x + dt*d1, e, k)
    nx = x + dt/2*(d1 + d2)
    # nx = x + dt*d2
    return nx

@vjp
def ode_heun_step_x(g_nx, x, e, k):
    d1 = ode_rhs(x, e, k)
    # nx = x + dt/2*(d1 + d2)
    g_d1 = g_nx*dt/2
    g_d2 = g_nx*dt/2
    g_x = g_nx*1
    # d2 = ode_rhs(x + dt*d1, e, k)
    g_d2_f = ode_rhs_xz.f(g_d2, x + dt*d1, e, k)
    g_x += g_d2_f
    g_d1 += g_d2_f*dt
    # d1 = ode_rhs(x, e, k)
    g_d1_f = ode_rhs_xz.f(g_d1, x, e, k)
    g_x += g_d1_f
    return g_x

@vjp
def ode_heun_step_e(g, x, e, k):
    d1 = ode_rhs(x, e, k)
    # nx = x + dt/2*(d1 + d2)
    g_d1 = g*dt/2
    g_d2 = g*dt/2
    # d2 = ode_rhs(x + dt*d1, e, k)
    g_d2_f = ode_rhs_eta.f(g_d2, x + dt*d1, e, k)
    g_d1 += ode_rhs_xz.f(g_d2, x + dt*d1, e, k)*dt
    # d1 = ode_rhs(x, e, k)
    g_d1_f = ode_rhs_eta.f(g_d1, x, e, k)
    return g_d2_f + g_d1_f

@vjp
def ode_heun_step_k(g, x, e, k):
    # TODO this is identical to _e 
    d1 = ode_rhs(x, e, k)
    # nx = x + dt/2*(d1 + d2)
    g_d1 = g*dt/2
    g_d2 = g*dt/2
    # d2 = ode_rhs(x + dt*d1, e, k)
    g_d2_f = ode_rhs_K.f(g_d2, x + dt*d1, e, k)
    g_d1 += ode_rhs_xz.f(g_d2, x + dt*d1, e, k)*dt
    # d1 = ode_rhs(x, e, k)
    g_d1_f = ode_rhs_K.f(g_d1, x, e, k)
    return g_d2_f + g_d1_f

defvjp(ode_heun_step, ode_heun_step_x, ode_heun_step_e, ode_heun_step_k)

check_grads_step(ode_heun_step)
print('heun ok')

@primitive
def ode_rk4_step(xz, eta, K): #dt, t, xz, SC, I1, tau0, K, eta):
    def f(x):
        return ode_rhs(x, eta, K)
    d1 = f(xz)
    d2 = f(xz + dt*d1/2)
    d3 = f(xz + dt*d2/2)
    d4 = f(xz + dt*d3)
    return xz + dt/6*(d1 + (d2 + d3)*2 + d4)

@vjp
def ode_rk4_step_x(g, x, e, k):
    def f(x): return ode_rhs(x, eta, K)
    d1 = f(x)
    d2 = f(x + dt*d1/2)
    d3 = f(x + dt*d2/2)
    # nx = xz + dt/6*(d1 + (d2 + d3)*2 + d4)
    g_x = g*1
    g_d1 = g*dt/6
    g_d2 = g*dt/3
    g_d3 = g*dt/3
    g_d4 = g*dt/6

    # d4 = f(x + dt*d3)
    g_d4_f = ode_rhs_xz.f(g_d4, x + dt*d3, e, k)
    g_x += g_d4_f
    g_d3 += g_d4_f*dt

    # d3 = f(x + dt*d2/2)
    g_d3_f = ode_rhs_xz.f(g_d3, x + dt*d2/2, e, k)
    g_x += g_d3_f
    g_d2 += g_d3_f*dt/2

    # d2 = f(x + dt*d1/2)
    g_d2_f = ode_rhs_xz.f(g_d2, x + dt*d1/2, e, k)
    g_x += g_d2_f
    g_d1 += g_d2_f*dt/2

    # d1 = f(x)
    g_d1_f = ode_rhs_xz.f(g_d1, x, e, k)
    g_x += g_d1_f

    return g_x

@vjp
def ode_rk4_step_e(g, x, e, k): return e*0
@vjp
def ode_rk4_step_k(g, x, e, k): return k*0

defvjp(ode_rk4_step, ode_rk4_step_x, ode_rk4_step_e, ode_rk4_step_k)

def f_rk4_xz(xz):
    return ode_rk4_step(xz, eta, K)
check_grads(f_rk4_xz,modes=['rev'])(xz)

print('ok')

def ode_rk4_solve(dt, nt, xz_init, SC, I1, tau0, K, eta):
    sol = [xz_init]
    for t in range(nt-1):
        xz = sol[-1]
        xz_next = ode_rk4_step(dt, t*dt, xz, SC, I1, tau0, K, eta)
        sol.append(xz_next)
    return np.array(sol)


def fwd_model(sol, gain, amp, off):
    seeg = []
    nn = sol.shape[1] // 2
    for xz_t in sol:
        seeg_t = amp*np.dot(gain, xz_t[:nn]) + off
        seeg.append(seeg_t)
    return np.array(seeg)


def target(seeg_hat, seeg, eps):
    ll = normal_lpdf(seeg, seeg_hat, eps)
    return np.sum(ll)


def loss(params, data):
    sol = ode_rk4_solve(
        data['dt'], data['nt'], params['xz_init'],
        data['SC'], data['I1'], data['tau0'], params['K'], params['eta'])
    seeg_hat = fwd_model(sol, data['gain'], params['amp'], params['off'])
    loss = -1 * target(seeg_hat, data['seeg'], params['eps'])
    return loss


grad_loss = grad(loss)
npz = np.load('bvep.npz')

data = {
    'dt': npz['dt'],
    'nt': npz['nt'],
    'SC': npz['SC'],
    'I1': npz['I1'],
    'tau0': npz['tau0'],
    'gain': npz['Gr'],
    'seeg': npz['Obs_seeg']
}
globals().update(data)
ns, nn = data['gain'].shape

init = 0.2
params = {
    'xz_init': np.ones(2*nn) * init,
    'K': init,
    'eta': np.ones(nn) * init,
    'amp': init,
    'off': np.ones(ns) * ns,
    'eps': init
}

bench=False
if bench:
    nr = 10
    et = timeit.timeit('loss(params, data)', globals=globals(), number=nr)
    print(f'loss\t{et/nr*1e3:0.3f} ms')
    et = timeit.timeit('grad_loss(params, data)', globals=globals(), number=nr)
    print(f'gloss\t{et/nr*1e3:0.3f} ms')
