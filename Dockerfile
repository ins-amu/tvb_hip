ARG ubver=20.04
FROM ubuntu:$ubver

# setup jlab env & app
RUN mkdir /apps
ADD build-jlab.sh /apps/tvb-hip-build-jlab.sh
RUN bash /apps/tvb-hip-build-jlab.sh

ADD build-jlab2.sh /apps/tvb-hip-build-jlab2.sh
RUN bash /apps/tvb-hip-build-jlab2.sh

# everything should run under hip user
RUN useradd -m hip -s /usr/bin/bash
USER hip
ENV PS1='hip@tvb:\w '
WORKDIR /home/hip

# customize jlab a bit
# RUN mkdir -p /home/hip/.jupyter/lab/user-settings/@jupyterlab/apputils-extension
# ADD theme.json /home/hip/.jupyter/lab/user-settings/@jupyterlab/apputils-extension/themes.jupyterlab-settings

# setup tini to avoid zombies
ENV tiniver v0.19.0
ADD https://github.com/krallin/tini/releases/download/${tiniver}/tini /tini
RUN chmod +x /tini

ENV PATH=/apps/tvb-hip/jlab_server/bin:$PATH

USER hip
ENTRYPOINT ["/tini", "--"]
WORKDIR /apps/tvb-hip/jupyterlab_app
CMD yarn start --no-sandbox