FROM jupyter/base-notebook

USER root
RUN apt-get update \
  && apt-get install -yq --no-install-recommends libfuse-dev nano fuse vim git \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*
USER $NB_USER

RUN conda install --yes -c defaults -c pyviz/label/dev -c bokeh/channel/dev -c intake \
    bokeh=0.12.16 \
    cython \
    cytoolz \
    dask=0.17.5 \
    dask-ml \
    datashader \
    distributed=1.21.8 \
    fastparquet \
    ipywidgets \
    jupyterlab=0.32.1 \
    jupyterlab_launcher=0.10.5 \
    holoviews \
    lz4 \
    matplotlib \
    nb_conda_kernels \
    netcdf4 \
    nomkl \
    numba \
    numcodecs \
    numpy=1.14.3 \
    pandas \
    python-blosc \
    scipy \
    scikit-image \
    scikit-learn \
    tornado \
    zict \
    intake-xarray \
    && conda clean -tipsy

RUN pip install --upgrade pip

RUN pip install fusepy click jedi kubernetes==4.0.0 dask-kubernetes s3fs \
                gcsfs==0.1.0 zarr==2.2.0 xarray==0.10.4 \
                nbserverproxy==0.8.1 \
                --upgrade --no-cache-dir

RUN pip install git+https://github.com/xgcm/xgcm \
                --no-cache-dir \
                --upgrade

RUN jupyter labextension install @jupyter-widgets/jupyterlab-manager \
                                 @jupyterlab/hub-extension \
                                 @pyviz/jupyterlab_pyviz

RUN jupyter serverextension enable --py nbserverproxy --sys-prefix

USER root
COPY prepare.sh /usr/bin/prepare.sh
RUN chmod +x /usr/bin/prepare.sh
RUN mkdir /home/$NB_USER/examples && chown -R $NB_USER /home/$NB_USER/examples
RUN mkdir /pre-home && mkdir /pre-home/examples && chown -R $NB_USER /pre-home
COPY worker-template.yaml /pre-home
COPY examples/ /pre-home/examples/

ENV DASK_TICK_MAXIMUM_DELAY=5s
ENV DASKERNETES_DIAGNOSTICS_LINK {JUPYTERHUB_SERVICE_PREFIX}proxy/{port}/status
ENV DASKERNETES_WORKER_TEMPLATE_PATH /home/$NB_USER/worker-template.yaml
ENV DASKERNETES_WORKER_NAME dask-{JUPYTERHUB_USER}-{uuid}
ENV DASK_DIAGNOSTICS_LINK {JUPYTERHUB_SERVICE_PREFIX}proxy/{port}/status
ENV DASK_KUBERNETES_WORKER_TEMPLATE_PATH /home/$NB_USER/worker-template.yaml
ENV DASK_KUBERNETES_WORKER_NAME dask-{JUPYTERHUB_USER}-{uuid}

RUN mkdir /gcs && chown -R $NB_USER /gcs
RUN mkdir /opt/app

# Add NB_USER to sudo
RUN echo "$NB_USER ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/notebook
RUN sed -ri "s#Defaults\s+secure_path=\"([^\"]+)\"#Defaults secure_path=\"\1:$CONDA_DIR/bin\"#" /etc/sudoers
USER $NB_USER

ENTRYPOINT ["tini", "--", "/usr/bin/prepare.sh"]
CMD ["start.sh jupyter lab"]
