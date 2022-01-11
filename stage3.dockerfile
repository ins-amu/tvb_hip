FROM hip:stage2

RUN apt-get install -y bc

# prereq bbwarp is mnic & workbench
WORKDIR /apps/tvb-hip
RUN curl -L http://packages.bic.mni.mcgill.ca/minc-toolkit/Debian/minc-toolkit-1.9.18-20200813-Ubuntu_20.04-x86_64.deb > minc.deb
RUN dpkg -i minc.deb; apt-get install -f -y \
 && mv /opt/minc/1.9.18 /apps/tvb-hip/minc \
 && ln -s /apps/tvb-hip/minc /opt/minc/1.9.18

RUN curl -L https://www.humanconnectome.org/storage/app/media/workbench/workbench-linux64-v1.5.0.zip > wb.zip
RUN apt-get install -y unzip && unzip wb.zip

# bigwarp https://bigbrainwarp.readthedocs.io/en/latest/pages/scripts.html
ADD BigBrainWarp /apps/tvb-hip/bbwarp

ENV bbwDir=/apps/tvb-hip/bbwarp
ENV mnc2Path=/apps/tvb-hip/minc
ENV icbmTemplate=$bbwDir/spaces/tpl-icbm/tpl-icbm_desc-t1_tal_nlin_sym_09c_mask.mnc
ENV wbPath=/apps/tvb-hip/workbench
ENV PATH=$bbwDir:$bbwDir/scripts/:$mnc2Path/:$wbPath:$PATH
ENV MATLABPATH=$bbwDir/scripts/:$MATLABPATH

WORKDIR /apps/tvb-hip/bbwarp
RUN bash scripts/downloads.sh

WORKDIR /work
