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

RUN echo "$NB_USER ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/notebook
RUN sed -ri "s#Defaults\s+secure_path=\"([^\"]+)\"#Defaults secure_path=\"\1:$CONDA_DIR/bin\"#" /etc/sudoers

USER $NB_USER

RUN pip install git+https://github.com/jupyterhub/nbserverproxy
RUN jupyter serverextension enable --py nbserverproxy

RUN pip install git+https://github.com/yuvipanda/daskernetes kubernetes \
                git+https://github.com/zarr-developers/zarr \
                git+https://github.com/jhamman/xarray@fix/zarr_set_attrs

 RUN pip install jedi --upgrade
