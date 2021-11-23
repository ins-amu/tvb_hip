#!/usr/bin/env bash

mkdir -p /apps/tvb-hip
pushd /apps/tvb-hip
wget https://surfer.nmr.mgh.harvard.edu/pub/dist/freesurfer/7.2.0/freesurfer-linux-ubuntu18_amd64-7.2.0.tar.gz
tar xzf freesurfer-linux-ubuntu18_amd64-7.2.0.tar.gz
rm freesurfer-linux-ubuntu18_amd64-7.2.0.tar.gz
