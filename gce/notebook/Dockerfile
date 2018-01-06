FROM jupyter/base-notebook

USER root
RUN apt-get update \
  && apt-get install -yq --no-install-recommends libfuse-dev nano fuse \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*
USER $NB_USER

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
    ipywidgets \
    git \
    jupyterlab \
    xarray \
    netcdf4 \
    scipy \
    && conda clean -tipsy

RUN pip install git+https://github.com/jupyterhub/nbserverproxy
RUN jupyter serverextension enable --py nbserverproxy
RUN jupyter labextension install @jupyter-widgets/jupyterlab-manager@0.31

RUN pip install click jedi kubernetes --upgrade

RUN pip install git+https://github.com/mrocklin/daskernetes@deploy \
                git+https://github.com/zarr-developers/zarr \
                git+https://github.com/jhamman/xarray@fix/zarr_set_attrs \
                git+https://github.com/martindurant/gcsfs.git@fuse \
                fusepy

USER root
RUN mkdir /gcs && chown -R $NB_USER /gcs
COPY prepare.sh /usr/bin/prepare.sh
RUN chmod +x /usr/bin/prepare.sh
RUN mkdir /home/$NB_USER/examples && chown -R $NB_USER /home/$NB_USER/examples
COPY examples/ /home/$NB_USER/examples
COPY .daskernetes.yaml /home/$NB_USER/
RUN mkdir /opt/app

# Add NB_USER to sudo
RUN echo "$NB_USER ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/notebook
RUN sed -ri "s#Defaults\s+secure_path=\"([^\"]+)\"#Defaults secure_path=\"\1:$CONDA_DIR/bin\"#" /etc/sudoers
USER $NB_USER

ENTRYPOINT ["tini", "--", "/usr/bin/prepare.sh"]
CMD ["start.sh jupyter lab"]
