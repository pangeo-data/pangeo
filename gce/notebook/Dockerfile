FROM jupyter/base-notebook

USER root
RUN apt-get update \
  && apt-get install -yq --no-install-recommends libfuse-dev nano fuse vim git \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*
USER $NB_USER

RUN conda install --yes -c conda-forge \
    cytoolz \
    dask=0.17.0 \
    distributed=1.21.0 \
    fastparquet \
    ipywidgets \
    jupyterlab \
    matplotlib \
    nb_conda_kernels \
    netcdf4 \
    nomkl \
    numba \
    numcodecs \
    numpy \
    pandas \
    python-blosc \
    scipy \
    scikit-image \
    xarray \
    zict \
    && conda clean -tipsy

RUN jupyter labextension install @jupyter-widgets/jupyterlab-manager @jupyterlab/hub-extension

RUN pip install fusepy click jedi kubernetes --upgrade --no-cache-dir

RUN pip install daskernetes==0.1.3 \
                git+https://github.com/zarr-developers/zarr \
                git+https://github.com/pydata/xarray \
                gcsfs==0.0.5 \
                --no-cache-dir

RUN pip install distributed==1.21.1 \
                dask==0.17.1 \
                --no-dependencies \ 
                --no-cache-dir

RUN pip install git+https://github.com/jupyterhub/nbserverproxy --no-cache-dir
RUN jupyter serverextension enable --py nbserverproxy --sys-prefix

USER root
COPY prepare.sh /usr/bin/prepare.sh
RUN chmod +x /usr/bin/prepare.sh
RUN mkdir /home/$NB_USER/examples && chown -R $NB_USER /home/$NB_USER/examples
RUN mkdir /pre-home && mkdir /pre-home/examples && chown -R $NB_USER /pre-home
COPY worker-template.yaml /pre-home
COPY examples/ /pre-home/examples/
ENV DASKERNETES_WORKER_TEMPLATE_PATH /home/$NB_USER/worker-template.yaml
ENV DASKERNETES_DIAGNOSTICS_LINK {JUPYTERHUB_SERVICE_PREFIX}proxy/{port}/status
ENV DASKERNETES_WORKER_NAME dask-{JUPYTERHUB_USER}-{uuid}
RUN mkdir /gcs && chown -R $NB_USER /gcs
RUN mkdir /opt/app

# Add NB_USER to sudo
RUN echo "$NB_USER ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/notebook
RUN sed -ri "s#Defaults\s+secure_path=\"([^\"]+)\"#Defaults secure_path=\"\1:$CONDA_DIR/bin\"#" /etc/sudoers
USER $NB_USER

ENTRYPOINT ["tini", "--", "/usr/bin/prepare.sh"]
CMD ["start.sh jupyter lab"]
