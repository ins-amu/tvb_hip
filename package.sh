#!/bin/bash

#python -m zipapp -p '/usr/bin/env python' -c tvb_hip
#chmod +x tvb_hip.pyz
set -eux

build=build
buildtest=buildtest

rm -rf $build $buildtest
mkdir -p $build/tvb_hip
mkdir $buildtest

# create app in new folder
pushd $build
pip3 install --target tvb_hip scipy matplotlib nibabel mne webdav4  # dependencies that may not be available
cp -r ../tvb_hip tvb_hip/
echo '
import tvb_hip.cli as cli
cli.main()
' > tvb_hip/__main__.py
python -m zipapp -p '/usr/bin/env python' -c tvb_hip
chmod +x tvb_hip.pyz
popd

# test in separate directory
cp $build/tvb_hip.pyz $buildtest/tvb_hip.pyz
pushd $buildtest
# test we can invoke the cli directly
./tvb_hip.pyz -v
# test we can import libraries with a single file on the PYTHONPATH
PYTHONPATH=tvb_hip.pyz python -c 'import tvb_hip; print(tvb_hip)'
# check size of archive
ls -lh
popd
