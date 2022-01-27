
bvep_: bvep_.stan use_bvep.hpp bvep.o
	CXXFLAGS=-g STANCFLAGS='--allow-undefined' USER_HEADER=$$PWD/use_bvep.hpp LDLIBS_OS=$$PWD/bvep.o make -C ~/.cmdstan/cmdstan-2.28.2/ $$PWD/bvep_

bvep_.stan: bvep.stan
	cpp < $< > $@

bvep.o: bvep.c
	# clang-12 -std=c99 -O3 -fomit-frame-pointer -ffast-math -march=native -mtune=native -c bvep.c
	gcc -g -std=c99 -O3 -fomit-frame-pointer -ffast-math -march=cascadelake -mtune=cascadelake -c bvep.c

bvep.c: bvep.fut
	futhark c --library bvep.fut

clean:
	rm bvep_ bvep.o
