#!/bin/bash

if [[ -z "$FREESURFER_HOME" ]]
then
	source /apps/tvb-hip/setup-env.sh
fi

cd /apps/tvb-hip/jupyterlab_app
yarn start --no-sandbox
