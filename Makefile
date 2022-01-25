
bvep_: bvep_.stan
	 STANCFLAGS=--allow-undefined USER_HEADER=$$PWD/use_bvep.hpp make -C ~/.cmdstan/cmdstan-2.28.2/ $$PWD/bvep_

bvep_.stan: bvep.stan
	cpp < $< > $@
