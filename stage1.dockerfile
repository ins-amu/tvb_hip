FROM ubuntu

RUN mkdir -p /apps/tvb-hip
WORKDIR /apps/tvb-hip

ADD bin/install-packages.sh ./
RUN bash install-packages.sh

ADD bin/install-freesurfer.sh ./
RUN bash install-freesurfer.sh

ADD bin/install-fsl.sh ./
RUN bash install-fsl.sh

ADD bin/build-jlab.sh ./
RUN bash build-jlab.sh

ENV PATH=/apps/tvb-hip/jlab_server/bin:$PATH

RUN pip install Cython && pip install tvb-gdist

# speculative
RUN pip install pybids siibra requests pyunicore

# RUN pip install mne frites nilearn etc etc
