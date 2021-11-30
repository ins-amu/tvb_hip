FROM hip

ENV PATH=/apps/tvb-hip/jlab_server/bin:$PATH

RUN apt-get install -y bc

# TODO add bigwarp https://bigbrainwarp.readthedocs.io/en/latest/pages/scripts.html
