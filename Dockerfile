ARG ubver=20.04
FROM ubuntu:$ubver

# setup jlab env & app
RUN mkdir /apps
ADD build-jlab.sh /apps/tvb-hip-build-jlab.sh
RUN bash /apps/tvb-hip-build-jlab.sh

ADD build-jlab2.sh /apps/tvb-hip-build-jlab2.sh
RUN bash /apps/tvb-hip-build-jlab2.sh

ENV PATH=/apps/tvb-hip/jlab_server/bin:$PATH
ADD start.sh /apps/tvb-hip/start.sh
RUN chmod +x /apps/tvb-hip/start.sh

#Mrtrix
RUN apt-get update && apt-get install -y wget git g++ python python-numpy libeigen3-dev zlib1g-dev libqt4-opengl-dev libgl1-mesa-dev libfftw3-dev libtiff5-dev dc
RUN cd /apps/tvb-hip && git clone https://github.com/MRtrix3/mrtrix3.git
RUN cd /apps/tvb-hip/mrtrix3 && export EIGEN_CFLAGS="-isystem /usr/include/eigen3" && ./configure
RUN cd /apps/tvb-hip/mrtrix3 && NUMBER_OF_PROCESSORS=1 ./build

#FSL
RUN wget https://fsl.fmrib.ox.ac.uk/fsldownloads/fslinstaller.py
RUN echo "" | python fslinstaller.py
RUN mv /usr/local/fsl /apps/tvb-hip/
ENV FSLDIR /apps/tvb-hip/fsl
RUN . ${FSLDIR}/etc/fslconf/fsl.sh
ENV PATH ${FSLDIR}/bin:${PATH}

#Freesurfer
RUN apt-get install -y tcsh bc libgomp1 perl-modules
RUN curl -LO https://surfer.nmr.mgh.harvard.edu/pub/dist/freesurfer/7.2.0/freesurfer_7.2.0_amd64.deb
RUN dpkg -i freesurfer_7.2.0_amd64.deb && apt-get install -f
RUN find / -name 'recon-all'
# COPY license.txt /apps/tvb-hip/freesurfer-stable/freesurfer/license.txt
ENV FREESURFER_HOME /apps/tvb-hip/freesurfer-stable/freesurfer
