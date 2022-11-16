#!/usr/bin/env bash

mkdir -p /apps/tvb-hip
pushd /apps/tvb-hip

apt-get install -y libglu1-mesa-dev
wget https://fsl.fmrib.ox.ac.uk/fsldownloads/fslinstaller.py
# 2to3 -w fslinstaller.py
echo "" | python2 fslinstaller.py &> fslinstall.log
tail fslinstall.log
mv /usr/local/fsl ./
