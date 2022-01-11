#!/bin/bash

export PATH=/apps/tvb-hip/jlab_server/bin:$PATH

source /apps/tvb-hip/setup-env.sh

cd /apps/tvb-hip/jupyterlab_app
yarn start --no-sandbox
