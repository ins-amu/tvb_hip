#!/bin/bash

condaver=latest
jlabappver=3.1.12-1

set -eux

mkdir -p /apps/tvb-hip
pushd /apps/tvb-hip

# bootstrap a conda env for building the final env
curl -LO https://repo.anaconda.com/miniconda/Miniconda3-${condaver}-Linux-x86_64.sh
bash Miniconda3-${condaver}-Linux-x86_64.sh -b -p /apps/tvb-hip/conda
rm Miniconda3-${condaver}-Linux-x86_64.sh
export PATH=$PWD/conda/bin:$PATH

conda install nodejs constructor && npm install -g yarn

# build app and env installer & do installation
curl -L https://github.com/jupyterlab/jupyterlab_app/archive/refs/tags/v${jlabappver}.tar.gz | tar xzf - 
ln -s jupyterlab_app-${jlabappver} jupyterlab_app 
pushd jupyterlab_app 
yarn install 
yarn build 
yarn create_env_installer:linux
env_installer/JupyterLabAppServer-${jlabappver}-Linux-x86_64.sh -b -p /apps/tvb-hip/jlab_server
rm -rf env_installer
export PATH=/apps/tvb-hip/jlab_server/bin:$PATH

# now we can free up some space
rm -rf /apps/tvb-hip/conda /root/.conda

# and install some packages
conda install -y numba scipy matplotlib nodejs
npm install -g yarn

# install mrtrix
conda install -c mrtrix3 mrtrix3

# then fsl
pushd /apps/tvb-hip
wget https://fsl.fmrib.ox.ac.uk/fsldownloads/fslinstaller.py
# 2to3 -w fslinstaller.py
echo "" | python2 fslinstaller.py > fslinstall.log
mv /usr/local/fsl ./

# finally freesurfer
wget https://surfer.nmr.mgh.harvard.edu/pub/dist/freesurfer/7.2.0/freesurfer-linux-ubuntu18_amd64-7.2.0.tar.gz
tar xzf freesurfer-linux-ubuntu18_amd64-7.2.0.tar.gz


popd