#!/bin/bash

# setup our environment, link stuff up etc
source /apps/tvb-hip/setup-env.sh

# exec ensures the exit code gets back to caller
# "@$" ensures quotes in arguments handled correctly
exec "$@"
