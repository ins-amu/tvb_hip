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

# then fsl
pushd /apps/tvb-hip
wget https://fsl.fmrib.ox.ac.uk/fsldownloads/fslinstaller.py
# 2to3 -w fslinstaller.py
echo "" | python2 fslinstaller.py &> fslinstall.log
tail fslinstall.log
mv /usr/local/fsl ./
export FSLDIR=/apps/tvb-hip/fsl
source ${FSLDIR}/etc/fslconf/fsl.sh
export PATH=$FSLDIR/bin:$PATH

# finally freesurfer
pushd /apps/tvb-hip
wget https://surfer.nmr.mgh.harvard.edu/pub/dist/freesurfer/7.2.0/freesurfer-linux-ubuntu18_amd64-7.2.0.tar.gz
tar xzf freesurfer-linux-ubuntu18_amd64-7.2.0.tar.gz

export FREESURFER_HOME=$PWD/freesurfer
source freesurfer/SetUpFreeSurfer.sh

popd


# TODO
# tvb-data tvb-library
# bvep modules
# stan
# jupyter notebooks
# pyunicore
# ipcluster
