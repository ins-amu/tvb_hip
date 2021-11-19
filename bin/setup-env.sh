
export PATH=/apps/tvb-hip/jlab_server/bin:$PATH

export FSLDIR=/apps/tvb-hip/fsl
source ${FSLDIR}/etc/fslconf/fsl.sh
export PATH=$FSLDIR/bin:$PATH

export SUBJECTS_DIR=$HOME/subjects
mkdir -p $SUBJECTS_DIR
export FREESURFER_HOME=/apps/tvb-hip/freesurfer
source $FREESURFER_HOME/SetUpFreeSurfer.sh
