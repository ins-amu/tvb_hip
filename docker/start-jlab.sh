#!/bin/bash

if [[ -z "$FREESURFER_HOME" ]]
then
	source /apps/tvb-hip/setup-env.sh
fi

jupyter lab --allow-root --ip=0.0.0.0 --port=8888
