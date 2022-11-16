#!/bin/bash

# requires tar, curl & pigz

set -eu

base_url=https://github.com/ins-amu/hip-tvb-app/releases/download
app_ver=${APP_VERSION}
archive=tvb-hip-app.tar.gz2

tmpdir=/tmp/hip-tvb-pull
mkdir -p $tmpdir
pushd $tmpdir

for a in a b c d e f g h i j k l m; do
    curl -LO ${base_url}/${app_ver}/${archive}.part.a{$a} &
done
wait

ls -lh
cat $(ls ${archive}.part.*) > ${archive}
pigz -dc ${archive} | tar xf -
mv apps/tvb-hip /apps/

popd
rm -rf $tmpdir
