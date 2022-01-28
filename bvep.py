from autograd import grad, numpy as np
from scipy.stats import norm


def ode_rhs(time, xz, SC, I1, tau0, K, eta):
    nn = xz.size // 2
    x, z = xz[:nn], xz[nn:]
    gx = np.dot(SC, x)
    dx = 1 - x**3 - 2*x**2 - z + I1
    dz = (1/tau0)*(4*(x - eta) - z - K*gx)
    return np.r_[dx, dz]


def ode_rk4_step(dt, t, xz, SC, I1, tau0, K, eta):
    def f(t, x):
        return ode_rhs(t, x, SC, I1, tau0, K, eta)
    d1 = f(t, xz)
    d2 = f(t + dt/2, xz + dt*d1/2)
    d3 = f(t + dt/2, xz + dt*d2/2)
    d4 = f(t + dt/2, xz + dt*d3)
    return xz + dt/6*(d1 + (d2 + d3)*2 + d4)


def ode_rk4_solve(dt, nt, xz_init, SC, I1, tau0, K, eta):
    sol = [xz_init]
    for t in range(nt-1):
        xz = sol[-1]
        xz_next = ode_rk4_step(dt, t*dt, xz, SC, I1, tau0, K, eta)
        sol.append(xz_next)
    return np.array(sol)


def fwd_model(sol, gain, amp, off):
    seeg = []
    for xz_t in sol:
        seeg_t = amp*np.dot(gain, xz_t) + off
        seeg.append(seeg_t)
    return np.array(seeg)


def target(seeg_hat, seeg, eps):
    ll = norm.pdf(seeg, seeg_hat, eps)
    return np.sum(ll)


def loss(params, data):
    sol = ode_rk4_solve(
        data['dt'], data['nt'], params['xz_init'],
        data['SC'], data['I1'], data['tau0'], params['K'], params['eta'])
    seeg_hat = fwd_model(sol, data['gain'], params['amp'], params['off'])
    loss = -1 * target(seeg_hat, data['seeg'], params['eps'])
    return loss


grad_loss = grad(loss)

