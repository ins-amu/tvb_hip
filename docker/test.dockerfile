FROM ubuntu
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /apps/${APP_NAME}

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y libnss3-dev libx11-xcb1 libxcb-dri3-0 libxcomposite1 \
libxcursor1 libxdamage1 libxfixes3 libxi6 libxtst6 libatk1.0-0 libatk-bridge2.0-0 \
libgdk-pixbuf2.0-0 libgtk-3-0 libgtk-3-0 libpangocairo-1.0-0 libpango-1.0-0 libcairo2 \
libdrm2 libgbm1 libasound2 libatspi2.0-0  curl pigz git build-essential tcsh perl nodejs \
python2

ENV APP_VERSION=v0.1

ADD pull_app.sh /tmp

RUN bash /tmp/pull_app.sh
