import os.path

def Settings(*args, **kwargs):
    stan_cmd = '-std=c++1y -Wno-unknown-warning-option -Wno-tautological-compare -Wno-sign-compare -D_REENTRANT -Wno-ignored-attributes      -I stan/lib/stan_math/lib/tbb_2020.3/include    -O3 -I src -I stan/src -I lib/rapidjson_1.1.0/ -I lib/CLI11-1.9.1/ -I stan/lib/stan_math/ -I stan/lib/stan_math/lib/eigen_3.3.9 -I stan/lib/stan_math/lib/boost_1.75.0 -I stan/lib/stan_math/lib/sundials_5.7.0/include    -DBOOST_DISABLE_ASSERTS          -c -include-pch stan/src/stan/model/model_header.hpp.gch -x c++ -o examples/bernoulli/bernoulli.o examples/bernoulli/bernoulli.hpp'
    home = os.environ['HOME']
    stan_cmd = stan_cmd.replace('-I stan/', f'-I {home}/.cmdstan/cmdstan-2.28.2/stan/')
    flags = [_ for _ in stan_cmd.split(' ') if _.strip()]
    return {'flags': flags}

