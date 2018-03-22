FROM continuumio/miniconda3:4.3.14

# Dumb init
RUN wget -O /usr/local/bin/dumb-init https://github.com/Yelp/dumb-init/releases/download/v1.2.0/dumb-init_1.2.0_amd64
RUN chmod +x /usr/local/bin/dumb-init

RUN conda install --yes -c conda-forge \
    cytoolz \
    dask=0.17.2 \
    distributed=1.21.4 \
    fastparquet \
    git \
    lz4 \
    netcdf4 \
    nomkl \
    numba \
    numcodecs \
    numpy \
    pandas \
    python-blosc \
    scikit-image \
    scipy \
    xarray \
    zict \
    && conda clean -tipsy

RUN apt-get update \
  && apt-get install -yq --no-install-recommends libfuse-dev nano fuse \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

RUN pip install pyasn1 click urllib3 --upgrade

RUN pip install git+https://github.com/zarr-developers/zarr \
                git+https://github.com/pydata/xarray \
                git+https://github.com/dask/gcsfs@2fbdc27e838a531ada080886ae778cb370ae48b8\
                fusepy \
                --no-cache-dir \
                --upgrade

ENV OMP_NUM_THREADS=1
ENV DASK_TICK_MAXIMUM_DELAY=5s

USER root
COPY prepare.sh /usr/bin/prepare.sh
RUN chmod +x /usr/bin/prepare.sh
RUN mkdir /opt/app
RUN mkdir /gcs

ENTRYPOINT ["/usr/local/bin/dumb-init", "/usr/bin/prepare.sh"]
