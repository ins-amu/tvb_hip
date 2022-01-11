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


ADD setup-env.sh ./
ADD entrypoint.sh ./
ADD start-jlab.sh ./
ADD start.sh ./

ENTRYPOINT ["/apps/tvb-hip/entrypoint.sh"]
CMD ["/apps/tvb-hip/start-jlab.sh"]
