#!/bin/bash

condaver=latest
jlabappver=3.1.12-1

set -eux

apt-get update

DEBIAN_FRONTEND=noninteractive apt-get install -y libnss3-dev libx11-xcb1 libxcb-dri3-0 libxcomposite1 \
libxcursor1 libxdamage1 libxfixes3 libxi6 libxtst6 libatk1.0-0 libatk-bridge2.0-0 \
libgdk-pixbuf2.0-0 libgtk-3-0 libgtk-3-0 libpangocairo-1.0-0 libpango-1.0-0 libcairo2 \
libdrm2 libgbm1 libasound2 libatspi2.0-0 curl git build-essential tcsh perl nodejs

# npm install -g yarn

# mkdir -p /apps/tvb-hip
# pushd /apps/tvb-hip

# # bootstrap a conda env for building the final env
# curl -LO https://repo.anaconda.com/miniconda/Miniconda3-${condaver}-Linux-x86_64.sh
# bash Miniconda3-${condaver}-Linux-x86_64.sh -b -p /apps/tvb-hip/conda
# rm Miniconda3-${condaver}-Linux-x86_64.sh
# export PATH=$PWD/conda/bin:$PATH

# conda install constructor

# # build app and env installer & do installation
# curl -L https://github.com/jupyterlab/jupyterlab_app/archive/refs/tags/v${jlabappver}.tar.gz | tar xzf - 
# ln -s jupyterlab_app-${jlabappver} jupyterlab_app 
# pushd jupyterlab_app 
# yarn install 
# yarn build 
# yarn create_env_installer:linux
# env_installer/JupyterLabAppServer-${jlabappver}-Linux-x86_64.sh -b -p /apps/tvb-hip/jlab_server
# rm -rf env_installer
# export PATH=/apps/tvb-hip/jlab_server:$PATH

# # now we can free up some space
# rm -rf /apps/tvb-hip/conda /root/.conda

# # and install some packages
# conda install -y numba scipy matplotlib

# # clean up
# apt-get clean
# rm -rf /var/lib/apt/lists/*