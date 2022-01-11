FROM ubuntu:20.04

RUN mkdir -p /apps/tvb-hip
WORKDIR /apps/tvb-hip

ADD install-packages.sh ./
RUN bash install-packages.sh

ADD install-freesurfer.sh ./
RUN bash install-freesurfer.sh

ADD install-fsl.sh ./
RUN bash install-fsl.sh

ADD build-jlab.sh ./
RUN bash build-jlab.sh
