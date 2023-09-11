# HIP TVB app

This is a repo of software configuration and Jupyter notebooks for the TVB app on
the HIP platform, as part of HBP SGA3.  It is a work in progress, but the following
diagram shows the functional structure:

![](app.png)

## Setup

The app consists of a `tvb_hip` Python module and template Jupyter notebooks.

The Python code assumes that a variety of tools are already installed:

- Freesurfer
- FSL
- Mrtrix3
- Python + JupyterLab and all dependencies

Data is processed inside temporary FreeSurfer `$SUBJECTS_DIR/$SUBJECT` folders.

## Local setup

For local development, I install the above tools, use a virtualenv for the Python
environment, and use Jupyter via a normal browser. 

This environment requires synchronizing some data via nextcloud client somewhere
on disk, and then the `tvb_hip` module should pick up via env var `hip_nextcloud`.

## HIP

For HIP, a Docker image contains the above tools + JupyterLab Desktop,
with data is present under `~/nextcloud`, available directly on the HIP platform:

![](running-on-hip.md)

