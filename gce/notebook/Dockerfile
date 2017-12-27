FROM daskdev/dask-notebook
    
RUN conda install --yes -c conda-forge \
    xarray \
    netcdf4 \
    scipy \
    && conda clean -tipsy
