FROM continuumio/miniconda3:4.3.14

# Dumb init
RUN wget -O /usr/local/bin/dumb-init https://github.com/Yelp/dumb-init/releases/download/v1.2.0/dumb-init_1.2.0_amd64
RUN chmod +x /usr/local/bin/dumb-init

RUN conda install --yes -c conda-forge \
    dask \
    distributed \
    numpy \
    pandas \
    numba \
    nomkl \
    fastparquet \
    zict \
    python-blosc \
    numcodecs \
    cytoolz \
    git \
    xarray \
    netcdf4 \
    scipy \
    && conda clean -tipsy

RUN apt-get update \
  && apt-get install -yq --no-install-recommends libfuse-dev nano fuse \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

RUN pip install pyasn1 click urllib3 --upgrade

RUN pip install git+https://github.com/zarr-developers/zarr \
                git+https://github.com/jhamman/xarray@fix/zarr_set_attrs \
                git+https://github.com/martindurant/gcsfs.git@fuse \
                fusepy

USER root
COPY prepare.sh /usr/bin/prepare.sh
RUN chmod +x /usr/bin/prepare.sh
RUN mkdir /opt/app
RUN mkdir /gcs

ENTRYPOINT ["/usr/local/bin/dumb-init", "/usr/bin/prepare.sh"]
