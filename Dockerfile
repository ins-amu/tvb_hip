ARG ubver=20.04
FROM ubuntu:$ubver

# setup jlab env & app
RUN mkdir -p /apps/tvb-hip
# ADD build-jlab.sh /apps/tvb-hip-build-jlab.sh
# RUN bash /apps/tvb-hip-build-jlab.sh

# ADD build-jlab2.sh /apps/tvb-hip-build-jlab2.sh
# RUN bash /apps/tvb-hip-build-jlab2.sh

# ENV PATH=/apps/tvb-hip/jlab_server/bin:$PATH
# ADD start.sh /apps/tvb-hip/start.sh
# RUN chmod +x /apps/tvb-hip/start.sh

# #Mrtrix
# RUN conda install -c mrtrix3 mrtrix3

#FSL
# RUN apt-get update && apt-get install -y python curl
# RUN curl -LO https://fsl.fmrib.ox.ac.uk/fsldownloads/fslinstaller.py
# RUN echo "" | python fslinstaller.py
# RUN mv /usr/local/fsl /apps/tvb-hip/
# ENV FSLDIR /apps/tvb-hip/fsl
# RUN . ${FSLDIR}/etc/fslconf/fsl.sh
# ENV PATH ${FSLDIR}/bin:${PATH}

#Freesurfer
RUN apt-get install -y curl
RUN curl -qLO https://surfer.nmr.mgh.harvard.edu/pub/dist/freesurfer/7.2.0/freesurfer_7.2.0_amd64.deb
RUN dpkg -i freesurfer_7.2.0_amd64.deb; apt-get install -f
RUN find / -name 'recon-all'
# COPY license.txt /apps/tvb-hip/freesurfer-stable/freesurfer/license.txt
ENV FREESURFER_HOME /apps/tvb-hip/freesurfer-stable/freesurfer
