
bvep_: bvep_.stan bvep.o
	 STANCFLAGS=--allow-undefined USER_HEADER=$$PWD/use_bvep.hpp\ $$PWD/bvep.o make -C ~/.cmdstan/cmdstan-2.28.2/ $$PWD/bvep_

bvep_.stan: bvep.stan
	cpp < $< > $@

bvep.o: bvep.c
	 gcc -O3 -std=c99 -c bvep.c -lm

bvep.c: bvep.fut
	futhark c --library bvep.fut
