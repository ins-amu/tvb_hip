FROM tvb/hip:latest

USER root
RUN conda install -c mrtrix3 mrtrix3