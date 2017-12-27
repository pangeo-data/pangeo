FROM daskdev/dask

RUN conda install -n dask --yes -c conda-forge \
    xarray \
    netcdf4 \
    scipy \
    && conda clean -tipsy
