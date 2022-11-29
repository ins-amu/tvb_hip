#!/bin/bash

docker run --rm -i -v $PWD:/work hip bash <<EOF
apt-get install -y pigz 
tar cf - /apps/tvb-hip | pigz > /work/app.tar.gz
EOF
