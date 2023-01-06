ARG CI_REGISTRY_IMAGE
ARG TAG
ARG DOCKERFS_TYPE
ARG DOCKERFS_VERSION
ARG FREESURFER_VERSION
ARG FSL_VERSION

# use prebuild freesurfer & fsl
FROM ${CI_REGISTRY_IMAGE}/freesurfer:${FREESURFER_VERSION}${TAG} as freesurfer
FROM ${CI_REGISTRY_IMAGE}/fsl:${FSL_VERSION}${TAG} as fsl

# and building this
FROM ${CI_REGISTRY_IMAGE}/${DOCKERFS_TYPE}:${DOCKERFS_VERSION}${TAG}
LABEL maintainer="marmaduke.woodman@univ-amu.fr"

ARG DEBIAN_FRONTEND=noninteractive
ARG CARD
ARG CI_REGISTRY
ARG APP_NAME
ARG APP_VERSION

LABEL app_version=$APP_VERSION
LABEL app_tag=$TAG

WORKDIR /apps/${APP_NAME}

# a lot of stuff depends on this path, so symlink it in place
RUN mkdir -p /apps/tvb-hip && ln -s /apps/${APP_NAME} /apps/tvb-hip

RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y libnss3-dev libx11-xcb1 libxcb-dri3-0 libxcomposite1 \
	libxcursor1 libxdamage1 libxfixes3 libxi6 libxtst6 libatk1.0-0 libatk-bridge2.0-0 \
	libgdk-pixbuf2.0-0 libgtk-3-0 libgtk-3-0 libpangocairo-1.0-0 libpango-1.0-0 libcairo2 \
	libdrm2 libgbm1 libasound2 libatspi2.0-0 curl git build-essential tcsh perl nodejs \
	python2 wget datalad bc libglu1-mesa-dev unzip vim

#RUN wget -q https://surfer.nmr.mgh.harvard.edu/pub/dist/freesurfer/7.2.0/freesurfer-linux-ubuntu18_amd64-7.2.0.tar.gz \
# && tar xzf freesurfer-linux-ubuntu18_amd64-7.2.0.tar.gz \
# && rm freesurfer-linux-ubuntu18_amd64-7.2.0.tar.gz
COPY --from=freesurfer /usr/local/freesurfer /usr/local/freesurfer

#RUN wget https://fsl.fmrib.ox.ac.uk/fsldownloads/fslinstaller.py \
# && sed -i -E -e 's,(^\s*prog.update|^\s*progress)\(,\1\,\(,' fslinstaller.py \
# && echo "" | python2 fslinstaller.py -d /usr/local/fsl
COPY --from=fsl /usr/local/fsl /usr/local/fsl

RUN curl -LO https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
 && bash Miniconda3-latest-Linux-x86_64.sh -b -p $PWD/conda \
 && rm Miniconda3-latest-Linux-x86_64.sh \
 && export PATH=$PWD/conda/bin:$PATH \
 && conda install -y jupyter numba scipy matplotlib \
 && pip install tvb-data tvb-library tqdm pybids siibra requests \
    		pyunicore mne nilearn pyvista ipywidgets cmdstanpy pytest \
 && install_cmdstan \
 && mv /root/.cmdstan $PWD/cmdstan

ENV PATH=/apps/${APP_NAME}/conda/bin:$PATH
# && conda install -y -c mrtrix3 mrtrix3 \

ENV PATH=/apps/${APP_NAME}/conda/bin:$PATH
ENV FREESURFER_HOME=/apps/${APP_NAME}/freesurfer
ADD ./apps/${APP_NAME}/license.txt /apps/${APP_NAME}/freesurfer/license.txt

# from the freesurfer dockerfile + mrtrix3
RUN apt install -y libx11-dev gettext xterm x11-apps perl make csh tcsh file bc xorg \
    xorg-dev xserver-xorg-video-intel libncurses5     libgomp1  libice6 libjpeg62 \
    libsm6     libxft2 libxmu6 libxt6 mrtrix3

# more reqs for jlab
RUN apt-get install -y libnotify4 xdg-utils libsecret-1-0 libsecret-common

RUN curl -LO https://github.com/jupyterlab/jupyterlab-desktop/releases/download/v3.5.0-1/JupyterLab-Setup-Debian.deb \
 && dpkg -i JupyterLab-Setup-Debian.deb \
 && bash $(find /opt/JupyterLab/ -name '*AppServer*sh') -b -p /apps/${APP_NAME}/jlabserver \
 && rm JupyterLab-Setup-Debian.deb

RUN pip install snakemake datalad

# run by hand once to select python environment 
# /apps/tvb/jlabserver/bin/python
# then grab config with
# docker cp hip-test:/home/hip/.config/jupyterlab-desktop/jupyterlab-desktop-data ./
# ADD jupyterlab-desktop-data /home/hip/.config/jupyterlab-desktop/jupyterlab-desktop-data
# TODO use entrypoint script to handle this step

# we could clean up but image is already enormous
    # apt-get remove -y --purge curl && \
    # apt-get autoremove -y --purge && \
    # apt-get clean && \
    # rm -rf /var/lib/apt/lists/*

# needed because we have a different context
ADD ./apps/${APP_NAME}/better-start.sh /apps/tvb-hip/start2.sh
# ADD better-start.sh /apps/tvb-hip/start2.sh

# ensure bash is used, and our our kernelspec with $HOME env vars set
#RUN mkdir /etc/jupyter \
# && echo "c.ServerApp.terminado_settings = { 'shell_command': ['/usr/bin/bash'] }" > /etc/jupyter/jupyter_lab_config.py \
# && echo "c.KernelSpecManager.whitelist = { 'tvb' }" >> /etc/jupyter/jupyter_lab_config.py \
# && echo "c.KernelSpecManager.ensure_native_kernel = False" >> /etc/jupyter/jupyter_lab_config.py

ENV APP_SPECIAL="terminal"
ENV APP_CMD=""
ENV PROCESS_NAME=""
ENV DIR_ARRAY=""
ENV CONFIG_ARRAY=".bash_profile"

HEALTHCHECK --interval=10s --timeout=10s --retries=5 --start-period=30s \
  CMD sh -c "/apps/${APP_NAME}/scripts/process-healthcheck.sh \
  && /apps/${APP_NAME}/scripts/ls-healthcheck.sh /home/${HIP_USER}/nextcloud/"

COPY ./scripts/ scripts/

# uncomment for deployment, I can't test this locally myself
ENTRYPOINT ["./scripts/docker-entrypoint.sh"]
