FROM jupyter/base-notebook

USER root
RUN apt-get update \
  && apt-get install -yq --no-install-recommends libfuse-dev nano fuse \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*
USER $NB_USER

RUN conda install --yes -c conda-forge \
    cytoolz \
    dask \
    distributed \
    fastparquet \
    git \
    ipywidgets \
    jupyterlab \
    netcdf4 \
    nomkl \
    numba \
    numcodecs \
    numpy \
    pandas \
    python-blosc \
    scipy \
    xarray \
    zict \
    && conda clean -tipsy

RUN pip install git+https://github.com/jupyterhub/nbserverproxy
RUN jupyter serverextension enable --py nbserverproxy
RUN jupyter labextension install @jupyter-widgets/jupyterlab-manager@0.31

RUN pip install fusepy click jedi kubernetes --upgrade

RUN pip install git+https://github.com/mrocklin/daskernetes@deploy \
                git+https://github.com/zarr-developers/zarr \
                git+https://github.com/jhamman/xarray@fix/zarr_set_attrs \
                git+https://github.com/martindurant/gcsfs.git@fuse \
                git+https://github.com/dask/distributed \
                git+https://github.com/dask/dask

USER root
RUN mkdir /gcs && chown -R $NB_USER /gcs
COPY prepare.sh /usr/bin/prepare.sh
RUN chmod +x /usr/bin/prepare.sh
RUN mkdir /home/$NB_USER/examples && chown -R $NB_USER /home/$NB_USER/examples
RUN mkdir /pre-home && mkdir /pre-home/examples && chown -R $NB_USER /pre-home
COPY examples/ /pre-home/examples/
COPY .daskernetes.yaml /pre-home
RUN mkdir /opt/app

# Add NB_USER to sudo
RUN echo "$NB_USER ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/notebook
RUN sed -ri "s#Defaults\s+secure_path=\"([^\"]+)\"#Defaults secure_path=\"\1:$CONDA_DIR/bin\"#" /etc/sudoers
USER $NB_USER

ENTRYPOINT ["tini", "--", "/usr/bin/prepare.sh"]
CMD ["start.sh jupyter lab"]
