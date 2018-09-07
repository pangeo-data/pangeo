#!/usr/bin/env python
# coding: utf-8

# # Sea Surface Altimetry Data Analysis
# 
# Example on using the gridded sea-surface altimetry data from The Copernicus Marine Environment
# 
# http://marine.copernicus.eu/services-portfolio/access-to-products/?option=com_csw&view=details&product_id=SEALEVEL_GLO_PHY_L4_REP_OBSERVATIONS_008_047
# 
# This is a widely used dataset in physical oceanography and climate.
# 
# ![globe image](http://marine.copernicus.eu/documents/IMG/SEALEVEL_GLO_SLA_MAP_L4_REP_OBSERVATIONS_008_027.png)
# 
# The dataset has already been extracted from copernicus and stored in google cloud storage in [xarray-zarr](http://xarray.pydata.org/en/latest/io.html#zarr) format.

# In[ ]:



import logging
logging.captureWarnings(True)
logging.getLogger('py.warnings').setLevel(logging.ERROR)


# In[ ]:


import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import gcsfs
plt.rcParams['figure.figsize'] = (15,10)
get_ipython().run_line_magic('matplotlib', 'inline')


# ### Initialize Dataset
# 
# Here we load the dataset from the zarr store. Note that this very large dataset initializes nearly instantly, and we can see the full list of variables and coordinates.

# In[ ]:


gcsmap = gcsfs.mapping.GCSMap('pangeo-data/dataset-duacs-rep-global-merged-allsat-phy-l4-v3-alt')
ds = xr.open_zarr(gcsmap)
ds


# ### Examine Metadata
# 
# For those unfamiliar with this dataset, the variable metadata is very helpful for understanding what the variables actually represent

# In[ ]:


for v in ds.data_vars:
    print('{:>10}: {}'.format(v, ds[v].attrs['long_name']))


# ### Create and Connect to Dask Distributed Cluster

# In[ ]:


from dask.distributed import Client, progress

from dask_kubernetes import KubeCluster
cluster = KubeCluster(n_workers=20)
cluster


# ** ☝️ Don't forget to click the link above to view the scheduler dashboard! **

# In[ ]:


client = Client(cluster)
client


# ## Visually Examine Some of the Data
# 
# Let's do a sanity check that the data looks reasonable:

# In[ ]:


plt.rcParams['figure.figsize'] = (15, 8)
ds.sla.sel(time='1982-08-07', method='nearest').plot()


# ## Timeseries of Global Mean Sea Level
# 
# Here we make a simple yet fundamental calculation: the rate of increase of global mean sea level over the observational period.

# In[ ]:


# the number of GB involved in the reduction
ds.sla.nbytes/1e9


# In[ ]:


# the computationally intensive step
sla_timeseries = ds.sla.mean(dim=('latitude', 'longitude')).load()


# In[ ]:


sla_timeseries.plot(label='full data')
sla_timeseries.rolling(time=365, center=True).mean().plot(label='rolling annual mean')
plt.legend()
plt.grid()


# Astute readers will note that this global mean is biased because the pixels were averaged naively, neglecting the spherical geometry of Earth. Below we repeat with a proper a weighing factor based on cosine of latitude.

# In[ ]:


coslat = np.cos(np.deg2rad(ds.latitude)).where(~ds.sla.isnull())
weights = coslat / coslat.sum(dim=('latitude', 'longitude'))
sla_timeseries_weighted = (ds.sla * weights).sum(dim=('latitude', 'longitude'))
sla_timeseries_weighted.load()


# In[ ]:


sla_timeseries.rolling(time=365, center=True).mean().plot(label='unweighted')
sla_timeseries_weighted.rolling(time=365, center=True).mean().plot(label='weighted')
plt.legend()
plt.grid()


# In this case, the weighting actually didn't make much difference!
# 
# In order to understand how the sea level rise is distributed in latitude, we can make a sort of [Hovmöller diagram](https://en.wikipedia.org/wiki/Hovm%C3%B6ller_diagram).

# In[ ]:


sla_hov = ds.sla.mean(dim='longitude').load()


# In[ ]:


fig, ax = plt.subplots(figsize=(12,4))
sla_hov.transpose().plot(vmax=0.2, ax=ax)


# We can see that most sea level rise is actually in the Southern Hemisphere.

# ## Sea Level Variability
# 
# We can quantify the natural variability in sea level by looking at its standard deviation in time.
# (We have not bothered to remove the trend; in this case, the trend is much smaller than the interannual variability.)

# In[ ]:


sla_std = ds.sla.std(dim='time').load()


# In[ ]:


sla_std.plot()


# In[ ]:




