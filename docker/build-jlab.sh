#!/bin/bash

condaver=latest
jlabappver=3.2.3-1

set -eux

mkdir -p /apps/tvb-hip
pushd /apps/tvb-hip

# bootstrap a conda env for building the final env
curl -LO https://repo.anaconda.com/miniconda/Miniconda3-${condaver}-Linux-x86_64.sh
bash Miniconda3-${condaver}-Linux-x86_64.sh -b -p /apps/tvb-hip/conda
rm Miniconda3-${condaver}-Linux-x86_64.sh
export PATH=$PWD/conda/bin:$PATH

conda install -c conda-forge -y nodejs constructor
npm install -g yarn

# build app and env installer & do installation
curl -L https://github.com/jupyterlab/jupyterlab_app/archive/refs/tags/v${jlabappver}.tar.gz | tar xzf - 
ln -s $PWD/jupyterlab-desktop-${jlabappver} jupyterlab_app 

pushd jupyterlab_app 
conda update -y nodejs
which node
node --version
yarn install 
yarn build 
yarn create_env_installer:linux
env_installer/JupyterLabDesktopAppServer-${jlabappver}-Linux-x86_64.sh -b -p /apps/tvb-hip/jlab_server
# rm -rf env_installer
export PATH=/apps/tvb-hip/jlab_server/bin:$PATH

# now we can free up some space
rm -rf /apps/tvb-hip/conda /root/.conda

# and install some packages
conda install -y numba scipy matplotlib nodejs
npm install -g yarn

# install mrtrix
conda install -c mrtrix3 mrtrix3

# install tvb etc
pip install tvb-data tvb-library tqdm
pip install Cython && pip install tvb-gdist
pip install pybids siibra requests pyunicore mne nilearn
pip install pyvista ipywidgets
pip install cmdstanpy && install_cmdstan && mv /root/.cmdstan /apps/tvb-hip/cmdstan

popd


# TODO
# tvb-data tvb-library
# bvep modules
# stan
# jupyter notebooks
# pyunicore
# ipcluster
