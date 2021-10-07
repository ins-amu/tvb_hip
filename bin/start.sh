#!/bin/bash

export PATH=/apps/tvb-hip/jlab_server/bin:$PATH

export FSLDIR=/apps/tvb-hip/fsl
RUN . ${FSLDIR}/etc/fslconf/fsl.sh
export PATH=${FSLDIR}/bin:${PATH}

cd /apps/tvb-hip/jupyterlab_app
yarn start --no-sandbox