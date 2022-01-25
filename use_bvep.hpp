//#include <Eigen/Eigen>
/*
#include "bvep.h"

static bool bvep_fut_setup = false;
static struct futhark_context_config *bvep_ctx_cfg;
static struct futhark_context *bvep_ctx;

static bool bvep_data_setup_done = false;
static struct futhark_opaque_bvep_data *bvep_data;

int
bvep_setup(std::ostream* pstream__)
{
	if (bvep_fut_setup) return 0;
	bvep_ctx_cfg = futhark_context_config_new();
	bvep_ctx = futhark_context_new(bvep_ctx_cfg);
	bvep_fut_setup = true;
	return 0;
}

int
bvep_data_setup(const Eigen::MatrixXd& sEEG, const Eigen::MatrixXd& SC,
                const Eigen::MatrixXd& gain, const double& dt, const double& tau0,
                const double& I1, std::ostream* pstream__)
{
	if (bvep_data_setup_done) return 0;
	struct futhark_f32_2d *f_sEEG, *f_SC, *f_gain;
	int ret = futhark_entry_mk_bvep_data(
		bvep_ctx, &bvep_data, f_sEEG, f_SC, f_gain, dt, tau0, I1);
	printf("mk_bvep_data returned %d\n", ret);
	return 1;
}
*/
