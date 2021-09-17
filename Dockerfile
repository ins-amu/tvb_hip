FROM continuumio/miniconda3

RUN apt-get update

# TODO rest of build

# TODO checkout at commit-ish or curl a release
WORKDIR /opt
RUN git clone https://github.com/jupyterlab/jupyterlab_app

# single RUN once it works
WORKDIR /opt/jupyterlab_app
RUN conda install nodejs
RUN npm install --global yarn
RUN conda install constructor
RUN yarn install
RUN yarn create_env_installer:linux
RUN ls -lh dist
# RUN yarn dist:linux
RUN dpkg -i dist/JupyterLab.deb

# TODO tini + run command
