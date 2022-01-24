export PATH=/apps/tvb-hip/jlab_server/bin:$PATH

# allows pipeline to find some relevant mrtrix3-shipped files
export MRT3=/apps/tvb-hip/jlab_server

export FSLDIR=/apps/tvb-hip/fsl
source ${FSLDIR}/etc/fslconf/fsl.sh
export PATH=$FSLDIR/bin:$PATH

# or fsl will not work
ln -s /apps/tvb-hip/fsl /usr/local/fsl &> /dev/null || true

export SUBJECTS_DIR=$HOME/subjects
mkdir -p $SUBJECTS_DIR
export FREESURFER_HOME=/apps/tvb-hip/freesurfer
source $FREESURFER_HOME/SetUpFreeSurfer.sh

# or minc may not work?
ln -s /apps/tvb-hip/minc /opt/minc/1.9.18 &> /dev/null || true

# or cmdstanpy will not work
ln -s /apps/tvb-hip/cmdstan $HOME/.cmdstan &> /dev/null || true
