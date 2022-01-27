#include <stan/math.hpp>
#include <stan/math/rev/core/reverse_pass_callback.hpp>
#include "bvep.h"

static bool bvep_fut_setup = false;
static struct futhark_context_config *bvep_ctx_cfg;
static struct futhark_context *bvep_ctx;

static bool bvep_data_setup_done = false;
static struct futhark_opaque_bvep_data *bvep_data;


namespace bvep__model_namespace {

using namespace stan;
using namespace std;

int
bvep_setup(std::ostream* pstream__)
{
	if (bvep_fut_setup) return 0;
	bvep_ctx_cfg = futhark_context_config_new();
	bvep_ctx = futhark_context_new(bvep_ctx_cfg);
	bvep_fut_setup = true;
	return 0;
}

typedef Eigen::Map<Eigen::MatrixXd, 0, Eigen::Stride<0,0> > Data;

futhark_f32_2d *to_f(const Eigen::MatrixXd &m) {
	const Eigen::Matrix<float,Eigen::Dynamic,Eigen::Dynamic,Eigen::RowMajor> mf = m.cast<float>();
	return futhark_new_f32_2d(bvep_ctx, mf.data(), mf.rows(), mf.cols());
}

int
bvep_data_setup(const Data& sEEG, const Data& SC,
                const Data& gain, const double& dt, const double& tau0,
                const double& I1, std::ostream* pstream__)
{
	bvep_setup(pstream__);
	if (bvep_data_setup_done) return 0;
	struct futhark_f32_2d *f_sEEG=to_f(sEEG), *f_SC=to_f(SC), *f_gain=to_f(gain);
	int ret = futhark_entry_mk_bvep_data(
		bvep_ctx, &bvep_data, f_sEEG, f_SC, f_gain, dt, tau0, I1);
	printf("mk_bvep_data returned %d\n", ret);
	if (ret != 0) {
		auto err = futhark_context_get_error(bvep_ctx);
		std::cout << "FUTHARK ERROR: " << err << std::endl;
	}
	return 1;
}

futhark_f32_1d *Vf_to_fut(Eigen::VectorXf v) { 
	return futhark_new_f32_1d(bvep_ctx, v.data(), v.size());
}

futhark_f32_1d *Vd_to_fut(Eigen::VectorXd v) {
	return Vf_to_fut(v.cast<float>());
}

double
bvep_loss(
	const Eigen::VectorXd& eta,
	const double& eps,
	const Eigen::VectorXd& x_init,
        const Eigen::VectorXd& z_init,
	const double& amp,
	const Eigen::VectorXd& off,
	const double& K, std::ostream* pstream__) 
{
	futhark_f32_1d *f_eta = Vd_to_fut(eta),
		       *f_x_init = Vd_to_fut(x_init),
		       *f_z_init = Vd_to_fut(z_init),
		       *f_off = Vd_to_fut(off);
	futhark_context_sync(bvep_ctx);
	float f_eps = eps, f_amp = amp, f_K = K;
	futhark_opaque_bvep_parm *parm;
	futhark_entry_mk_bvep_parm(bvep_ctx, &parm, f_eta, f_eps,
			f_x_init, f_z_init, f_amp, f_off, f_K);
	float f_loss = 0.0;
	futhark_entry_bvep_loss(bvep_ctx, &f_loss, bvep_data, parm);
	futhark_context_sync(bvep_ctx);
	double loss = f_loss;
	return loss;
}

#define FUTCHECK(e) if (!(e)) std::cout << #e ": " << futhark_context_get_error(bvep_ctx) << std::endl

template <typename f, typename V, typename P>
void inc_adj(P& p, V& v) {
	futhark_f32_1d *g;
	futhark_entry_bvep_parm_get_eta(bvep_ctx, &g, p);
	Eigen::VectorXf G(v.size());
	futhark_values_f32_1d(bvep_ctx, g, G.data());
	v.adj() += G.cast<double>();
}

template <typename V, typename S>
promote_args_t<value_type_t<V>, S>
bvep_loss(const V& eta, const S& eps, const V& x_init,
          const V& z_init, const S& amp, const V& off,
          const S& K, std::ostream* pstream__) 
{
	// forward pass
	futhark_f32_1d *f_eta = Vd_to_fut(value_of(eta)),
		       *f_x_init = Vd_to_fut(value_of(x_init)),
		       *f_z_init = Vd_to_fut(value_of(z_init)),
		       *f_off = Vd_to_fut(value_of(off));
	futhark_context_sync(bvep_ctx);
	float f_eps = value_of(eps), f_amp = value_of(amp), f_K = value_of(K);
	futhark_opaque_bvep_parm *parm;
	futhark_entry_mk_bvep_parm(bvep_ctx, &parm, f_eta, f_eps,
			f_x_init, f_z_init, f_amp, f_off, f_K);
	float f_loss = 0.0;
	futhark_entry_bvep_loss(bvep_ctx, &f_loss, bvep_data, parm);
	futhark_context_sync(bvep_ctx);
	S ret(f_loss);
	// arena vars
	arena_t<V> a_eta(eta);
	arena_t<V> a_x_init(x_init);
	arena_t<V> a_z_init(z_init);
	arena_t<V> a_off(off);
	arena_t<S> a_eps(eps);
	arena_t<S> a_amp(amp);
	arena_t<S> a_K(K);
	arena_t<S> a_ret(ret);
	// backward pass
	math::reverse_pass_callback([a_eta, a_x_init, a_z_init, a_off, a_eps, a_amp, a_K, a_ret, parm]() mutable {
		futhark_opaque_bvep_parm *gparm;
		// run bwd in futhark
		futhark_entry_bvep_grad_loss(bvep_ctx, &gparm, bvep_data, parm);
		// extract parameter gradients
		futhark_f32_1d *g_eta;
		futhark_entry_bvep_parm_get_eta(bvep_ctx, &g_eta, gparm);
		Eigen::VectorXf G_eta(a_eta.size());
		futhark_values_f32_1d(bvep_ctx, g_eta, G_eta.data());
		a_eta.adj() += G_eta.cast<double>();

		futhark_f32_1d *g_x_init;
		futhark_entry_bvep_parm_get_x_init(bvep_ctx, &g_x_init, gparm);
		Eigen::VectorXf G_x_init(a_x_init.size());
		futhark_values_f32_1d(bvep_ctx, g_x_init, G_x_init.data());
		a_x_init.adj() += G_x_init.cast<double>();

		futhark_f32_1d *g_z_init;
		futhark_entry_bvep_parm_get_z_init(bvep_ctx, &g_z_init, gparm);
		Eigen::VectorXf G_z_init(a_z_init.size());
		futhark_values_f32_1d(bvep_ctx, g_z_init, G_z_init.data());
		a_z_init.adj() += G_z_init.cast<double>();

		futhark_f32_1d *g_off;
		futhark_entry_bvep_parm_get_off(bvep_ctx, &g_off, gparm);
		Eigen::VectorXf G_off(a_off.size());
		futhark_values_f32_1d(bvep_ctx, g_off, G_off.data());
		a_off.adj() += G_off.cast<double>();

		float g_eps;
		futhark_entry_bvep_parm_get_eps(bvep_ctx, &g_eps, gparm);
		a_eps.adj() += g_eps;

		float g_amp;
		futhark_entry_bvep_parm_get_amp(bvep_ctx, &g_amp, gparm);
		a_amp.adj() += g_amp;

		float g_K;
		futhark_entry_bvep_parm_get_K(bvep_ctx, &g_K, gparm);
		a_K.adj() += g_K;
	});
	return ret;
}

} // namespace
