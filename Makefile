bvep3: bvep3.stan bvep2inc.hpp
	rm bvep3 || true
	#CXXFLAGS='-g -Og'
	STANCFLAGS='--allow-undefined' USER_HEADER=$$PWD/bvep2inc.hpp make -C ~/.cmdstan/cmdstan-2.28.2/ $$PWD/bvep3

bvep2: bvep2.stan bvep2inc.hpp
	rm bvep2 || true
	#CXXFLAGS='-g -Og'
	STANCFLAGS='--allow-undefined' USER_HEADER=$$PWD/bvep2inc.hpp make -C ~/.cmdstan/cmdstan-2.28.2/ $$PWD/bvep2

bvep_: bvep_.stan use_bvep.hpp bvep.o
	rm bvep_ || true
	CXXFLAGS=-g STANCFLAGS='--allow-undefined' USER_HEADER=$$PWD/use_bvep.hpp LDLIBS_OS=$$PWD/bvep.o make -C ~/.cmdstan/cmdstan-2.28.2/ $$PWD/bvep_

bvep_.stan: bvep.stan
	cpp-11 < $< > $@

bvep.o: bvep.c
	clang -std=c99 -O3 -fomit-frame-pointer -ffast-math -mcpu=apple-a14 -c bvep.c
	# gcc -g -std=c99 -O3 -fomit-frame-pointer -ffast-math -march=cascadelake -mtune=cascadelake -c bvep.c

bvep.c: bvep.fut
	futhark c --library bvep.fut

clean:
	rm bvep_ bvep.o
