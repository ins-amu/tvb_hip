import timeit
import numpy as onp
import numba as nb
from functools import partial
from autograd import grad, numpy as np
from autograd.extend import primitive, defvjp
from autograd.scipy.stats.norm import logpdf as normal_lpdf
from autograd.test_util import check_grads

npz = np.load('bvep.npz')
globals().update(npz)

custom_grads = True

def ode_rhs(xz, eta, K):#, SC, I1, tau0):
    nn = xz.size // 2
    x, z = xz[:nn], xz[nn:]
    gx = np.dot(SC, x)
    dx = 1 - x**3 - 2*x**2 - z + I1
    dz = (1/tau0)*(4*(x - eta) - z - K*gx)
    return np.concatenate([dx, dz])

@nb.njit(inline='always', fastmath=True)
def ode_rhs_jit(xz, eta, K, SC, I1, rtau0):
    nn = xz.size // 2
    dxz = onp.zeros_like(xz)
    for i in range(nn):
        gx = 0.0
        for j in range(nn):
            gx += SC[i,j]*xz[j]
        x = xz[i]
        z = xz[i+nn]
        dxz[i] = 1.0 - x*x*x - 2*x*x - z + I1
        dxz[i+nn] = rtau0*(4.0*(x - eta[i]) - z - K*gx)
    return dxz

def ode_rhs(xz, eta, K):
    return ode_rhs_jit(xz, eta, K, SC, I1, 1/tau0)
ode_rhs.jit = ode_rhs_jit

if custom_grads:
    ode_rhs = primitive(ode_rhs)

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

    # set up jit version
    @nb.njit(inline='always', fastmath=True)
    def ode_rhs_eta_jit(g_eta, g, xz, eta, K, rtau0):
        nn = xz.shape[0] // 2
        # g_eta = onp.ones(nn)
        for i in range(nn):
            g_eta[i] = -g[i+nn] * rtau0 * 4 

    # TODO boilerplate
    ode_rhs_eta_np = ode_rhs_eta
    @vjp
    def ode_rhs_eta(g, xz, eta, K):
        val = lambda x : x._value if hasattr(x, '_value') else x
        if hasattr(g, '_value'):
            ret = ode_rhs_eta_np.f(g, xz, eta, K)
            ode_rhs_eta_jit(ret._value, g._value, val(xz), val(eta), val(K), 1/tau0)
            return ret
        else:
            ret = g[:xz.size//2]*0
            ode_rhs_eta_jit(ret, g, xz, eta, K, 1/tau0)
            return ret
    ode_rhs_eta.jit = ode_rhs_eta_jit

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

    # set up jit version
    @nb.njit(inline='always', fastmath=True)
    def ode_rhs_xz_jit(g_xz, g, xz, eta, K, rtau0, SC):
        # unpack
        nn = xz.size // 2
        x, _ = xz[:nn], xz[nn:]
        g_dx, g_dz = g[:nn], g[nn:]
        for i in range(nn):
            # grad wrt x & z via dx
            g_dx_x = g_dx[i] * (-3*x[i]*x[i] - 4*x[i])
            g_dx_z = g_dx[i] * (-1)
            # grad wrt x, z, eta, K via dz
            acc = 0
            for j in range(nn):
                acc += g_dz[j]*SC[j,i]
            g_dz_x = g_dz[i]*4*rtau0 - K*rtau0*acc # np.dot(g_dz, g_gx_x)
            g_dz_z = g_dz[i] * (-1/tau0)
            # cumulative grads for states & params
            g_xz[i] = g_dx_x + g_dz_x
            g_xz[i+nn] = g_dx_z + g_dz_z

    # TODO boilerplate
    ode_rhs_xz_np = ode_rhs_xz
    @vjp
    def ode_rhs_xz(g, xz, eta, K):
        val = lambda x : x._value if hasattr(x, '_value') else x
        if hasattr(g, '_value'):
            ret = ode_rhs_xz_np.f(g, xz, eta, K)
            ode_rhs_xz_jit(ret._value, g._value, val(xz), val(eta), val(K), 1/tau0, SC)
            return ret
        else:
            ret = g*0
            ode_rhs_xz_jit(ret, g, xz, eta, K, 1/tau0, SC)
            return ret
    ode_rhs_xz.jit = ode_rhs_xz_jit

    @vjp
    def ode_rhs_K(g, xz, eta, K):
        nn = xz.size // 2
        x, _ = xz[:nn], xz[nn:]
        _, g_dz = g[:nn], g[nn:]
        gx = np.dot(SC, x)
        return -np.sum(g_dz * gx / tau0)

    # set up jit version
    @nb.njit(inline='always', fastmath=True)
    def ode_rhs_K_jit(g, xz, eta, K, rtau0, SC):
        nn = xz.size // 2
        x, _ = xz[:nn], xz[nn:]
        _, g_dz = g[:nn], g[nn:]
        acc = 0
        for i in range(nn):
            gx = 0
            for j in range(nn):
                gx += SC[i,j]*x[j]
            acc += g_dz[i]*gx
        return -acc*rtau0
    # TODO boilerplate
    ode_rhs_K_np = ode_rhs_K
    @vjp
    def ode_rhs_K(g, xz, eta, K):
        val = lambda x : x._value if hasattr(x, '_value') else x
        if hasattr(g, '_value'):
            ret = ode_rhs_K_np.f(g, xz, eta, K)
            ret._value = ode_rhs_K_jit(g._value, val(xz), val(eta), val(K), 1/tau0, SC)
            return ret
        else:
            ret = ode_rhs_K_jit(g, xz, eta, K, 1/tau0, SC)
            return ret
    ode_rhs_K.jit = ode_rhs_K_jit

    defvjp(ode_rhs, ode_rhs_xz, ode_rhs_eta, ode_rhs_K)

nn = SC.shape[0]
xz = np.ones(2*nn)*0.2
eta = np.ones(nn)*0.2
K = 0.2

if custom_grads:
    check_grads(lambda xz: ode_rhs(xz, eta, K), modes=['rev'])(xz)
    print('rhs xz ok')
    check_grads(lambda eta: ode_rhs(xz, eta, K), modes=['rev'])(eta)
    print('rhs eta ok')
    check_grads(lambda K: ode_rhs(xz, eta, K), modes=['rev'])(K)
    print('rhs K ok')
    print('rhs ok w/ jits as well')

def ode_euler_step(xz, eta, K):
    return xz + dt * ode_rhs(xz, eta, K)

if custom_grads:
    ode_euler_step = primitive(ode_euler_step)

    @vjp
    def ode_euler_step_x(g, x, e, k): return g + ode_rhs_xz.f(g*dt,x,e,k)

    # set up jit version
    @nb.njit(inline='always', fastmath=True)
    def ode_euler_step_x_jit(g_x, g, x, e, k, rtau0, SC):
        ode_rhs_xz_jit(g_x, g*dt, x, e, k, rtau0, SC)
        g_x += g
    ode_euler_step_x_np = ode_euler_step_x
    @vjp
    def ode_euler_step_x(g, x, e, k):
        val = lambda x : x._value if hasattr(x, '_value') else x
        if hasattr(g, '_value'):
            ret = ode_euler_step_x_np.f(g, xz, eta, K)
            ode_euler_step_x_jit(ret._value, g._value, val(xz), val(eta), val(K), 1/tau0, SC)
            return ret
        else:
            ret = g*0
            ode_euler_step_x_jit(ret, g, xz, eta, K, 1/tau0, SC)
            return ret
    ode_euler_step_x.jit = ode_euler_step_x_jit

    @vjp
    def ode_euler_step_e(g, x, e, k): return ode_rhs_eta.f(g*dt, x, e, k)

    # set up jit version
    @nb.njit(inline='always', fastmath=True)
    def ode_euler_step_e_jit(g_e, g, x, e, k, rtau0):
        ode_rhs_eta_jit(g_e, g*dt, x, e, k, rtau0)
    ode_euler_step_e_np = ode_euler_step_e
    @vjp
    def ode_euler_step_e(g, x, e, k):
        val = lambda x : x._value if hasattr(x, '_value') else x
        if hasattr(g, '_value'):
            ret = ode_euler_step_e_np.f(g, xz, eta, K)
            ode_euler_step_e_jit(ret._value, g._value, val(xz), val(eta), val(K), 1/tau0)
            return ret
        else:
            ret = g[g.size//2:]*0
            ode_euler_step_e_jit(ret, g, xz, eta, K, 1/tau0)
            return ret
    ode_euler_step_e.jit = ode_euler_step_e_jit

    @vjp
    def ode_euler_step_k(g, x, e, k): return ode_rhs_K.f(g*dt, x, e, k)

    # set up jit version
    @nb.njit(inline='always', fastmath=True)
    def ode_euler_step_k_jit(g, x, e, k, rtau0, SC):
        return ode_rhs_K_jit(g*dt, x, e, k, rtau0, SC)
    ode_euler_step_k_np = ode_euler_step_k
    @vjp
    def ode_euler_step_k(g, x, e, k):
        rtau0 = 1/tau0
        val = lambda x : x._value if hasattr(x, '_value') else x
        if hasattr(g, '_value'):
            ret = ode_euler_step_k_np.f(g, xz, eta, K)
            ret._value = ode_euler_step_k_jit(g._value, val(xz), val(eta), val(K), rtau0, SC)
            return ret
        else:
            return ode_euler_step_k_jit(g, xz, eta, K, rtau0, SC)
    ode_euler_step_k.jit = ode_euler_step_k_jit

    defvjp(ode_euler_step, ode_euler_step_x, ode_euler_step_e, ode_euler_step_k)

def check_grads_step(step):
    print('check', 'x')
    check_grads(lambda x: step(x, eta, K), modes=['rev'])(xz)
    print('check', 'e')
    check_grads(lambda e: step(xz, e, K), modes=['rev'])(eta)
    print('check', 'k')
    check_grads(lambda k: step(xz, eta, k), modes=['rev'])(K)

if custom_grads:
    check_grads_step(ode_euler_step)
    print('euler ok')

def ode_heun_step(x, e, k):
    d1 = ode_rhs(x, e, k)
    d2 = ode_rhs(x + dt*d1, e, k)
    nx = x + dt/2*(d1 + d2)
    # nx = x + dt*d2
    return nx

if custom_grads:
    ode_heun_step = primitive(ode_heun_step)

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

    # set up jit version
    @nb.njit(inline='always', fastmath=True)
    def ode_heun_step_x_jit(g_x, g_nx, x, e, k, rtau0, SC, I1):
        d1 = ode_rhs_jit(x, e, k, SC, I1, rtau0)
        # nx = x + dt/2*(d1 + d2)
        g_d1 = g_nx*dt/2
        g_d2 = g_nx*dt/2
        g_x[:] = g_nx
        # d2 = ode_rhs(x + dt*d1, e, k)
        g_d2_f = onp.zeros_like(g_d2)
        ode_rhs_xz_jit(g_d2_f, g_d2, x + dt*d1, e, k, rtau0, SC)
        g_x += g_d2_f
        g_d1 += g_d2_f*dt
        # d1 = ode_rhs(x, e, k)
        g_d1_f = onp.zeros_like(g_d2)
        ode_rhs_xz_jit(g_d1_f, g_d1, x, e, k, rtau0, SC)
        g_x += g_d1_f
    ode_heun_step_x_np = ode_heun_step_x
    @vjp
    def ode_heun_step_x(g, x, e, k):
        val = lambda x : x._value if hasattr(x, '_value') else x
        if hasattr(g, '_value'):
            ret = ode_heun_step_x_np.f(g, xz, eta, K)
            ode_heun_step_x_jit(ret._value, g._value, val(xz), val(eta), val(K), 1/tau0, SC, I1)
            return ret
        else:
            ret = g*0
            ode_heun_step_x_jit(ret, g, xz, eta, K, 1/tau0, SC, I1)
            return ret
    ode_heun_step_x.jit = ode_heun_step_x_jit

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

def ode_rk4_step(xz, eta, K): #dt, t, xz, SC, I1, tau0, K, eta):
    def f(x):
        return ode_rhs(x, eta, K)
    d1 = f(xz)
    d2 = f(xz + dt*d1/2)
    d3 = f(xz + dt*d2/2)
    d4 = f(xz + dt*d3)
    return xz + dt/6*(d1 + (d2 + d3)*2 + d4)

if custom_grads:
    ode_rk4_step = primitive(ode_rk4_step)

    @vjp
    def ode_rk4_step_x(g, x, e, k):
        def f(x): return ode_rhs(x, eta, K)
        # store from fwd pass or recalculate
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

def ode_heun_solve(dt, nt, xz_init, SC, I1, tau0, K, eta):
    sol = [xz_init]
    for t in range(nt-1):
        xz = sol[-1]
        # xz_next = ode_heun_step(dt, t*dt, xz, SC, I1, tau0, K, eta)
        xz_next = ode_heun_step(xz,eta,K)
        sol.append(xz_next)
    return np.array(sol)


def fwd_model(sol, gain, amp, off):
    nn = sol.shape[1] // 2
    return amp*np.dot(sol[:,:nn], gain.T) + off


def target(seeg_hat, seeg, eps):
    ll = normal_lpdf(seeg, seeg_hat, eps)
    return np.sum(ll)


def loss(params, data):
    sol = ode_heun_solve(
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

bench=True
if bench:
    nr = 10
    et = timeit.timeit('loss(params, data)', globals=globals(), number=nr)
    print(f'loss\t{et/nr*1e3:0.3f} ms')
    et = timeit.timeit('grad_loss(params, data)', globals=globals(), number=nr)
    print(f'gloss\t{et/nr*1e3:0.3f} ms')
