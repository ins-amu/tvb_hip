#!/bin/bash

workdir=/apps/tvb-hip

mkdir -p $workdir

for script in ./install-packages.sh ./install-freesurfer.sh ./install-fsl.sh ./build-jlab.sh
do
	bash $script
done
