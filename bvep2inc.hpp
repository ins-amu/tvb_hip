#include "stan/math/prim/meta/is_rev_matrix.hpp"
#include <stan/math.hpp>
#include <stan/math/rev/core/reverse_pass_callback.hpp>

namespace bvep2_model_namespace {

using namespace stan;
using namespace stan::math;
using namespace Eigen;
using namespace std;

// fwd pass
template <typename Mat, typename Mat2>
VectorXd ode_rhs_c(const double time, const Mat& xz, const Mat2& SC, 
		const double I1, const double tau0, const double K,
		const Mat& eta, ostream* pstream) {
	int nn = xz.size() / 2;
	double rtau0 = 1.0 / tau0;
	VectorXd dxz(xz.size());
	for (int i=0; i<nn; i++)
	{
		double acc = 0.0;
		for (int j=0; j<nn; j++)
			acc += SC(i,j)*xz(j);
		double x = xz(i), z = xz(i+nn);
		dxz(i) = 1.0 - x*x*x - 2*x*x - z + I1;
		dxz(i+nn) = rtau0*(4*(x - eta(i)) - z - K*acc);
	}
	return dxz;
}

// rev as separate function for reuse
template <typename VarMat, typename Var, typename Mat>
inline auto ode_rhs_rev(
		int nn, VarMat& dxz_a, VarMat& xz_a, VarMat& eta_a,
	       	Var& K_a, Mat& SC_a, double rtau0, double I1) {
	auto g = dxz_a.adj_op();
	auto g_dx = g.head(nn), g_dz = g.tail(nn);
	auto x = value_of(xz_a.head(nn));
	eta_a.adj() += -g_dz.tail(nn)*rtau0*4;
	K_a.adj() += -(g_dz.array()*(SC_a*x).array()).sum() * rtau0;
	VectorXd g_x(xz_a.size());
	g_x.fill(0.0);
	g_x.head(nn).array() += g_dx.array()*(-3*x.array().square() - 4*x.array());
	g_x.head(nn) += g_dz*4*rtau0 - value_of(K_a)*rtau0*(SC_a.transpose()*g_dz);
	g_x.tail(nn) += -g_dx;
	g_x.tail(nn) += -g_dz*rtau0;
	xz_a.adj() += g_x;
}

// fwd + reverse when args are var types
template <typename VarMat, typename Var, typename Mat,
	  require_rev_matrix_t<VarMat>* = nullptr >
VarMat ode_rhs_c(const double time, const VarMat& xz, const Mat& SC,
          const double I1, const double tau0, const Var& K,
          const VarMat& eta, ostream* pstream) { 
	int nn = xz.size() / 2;
	double rtau0 = 1.0 / tau0;
	// call fwd pass impl
	//typename decltype(value_of(xz))::foo bar;
	//typename decltype(SC)::foo bar2;
	VectorXd dxz_val = ode_rhs_c(
			time, value_of(xz), SC, I1, tau0, 
			value_of(K), value_of(eta), pstream);
	VarMat dxz_(dxz_val);
	// construct bwd pass
	arena_t<VarMat> dxz_a(dxz_);
	arena_t<VarMat> xz_a(xz);
	arena_t<VarMat> eta_a(eta);
	arena_t<Var> K_a(K);
	arena_t<Mat> SC_a(SC);
	reverse_pass_callback([nn, dxz_a, xz_a, eta_a, K_a, SC_a, rtau0, I1]() mutable {
		ode_rhs_rev(nn, dxz_a, xz_a, eta_a, K_a, SC_a, rtau0, I1);
	});
	// return results
	return dxz_;
}

} // bvep2_model_namespace
