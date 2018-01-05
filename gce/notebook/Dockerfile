FROM daskdev/dask-notebook
    
RUN conda install --yes -c conda-forge \
    xarray \
    netcdf4 \
    scipy \
    && conda clean -tipsy

RUN pip install git+https://github.com/martindurant/gcsfs.git@fuse fusepy click 

USER root
RUN apt-get update \
  && apt-get install -yq --no-install-recommends libfuse-dev nano kmod fuse \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*
RUN curl https://raw.githubusercontent.com/kubernetes/helm/master/scripts/get | bash
USER $NB_USER
