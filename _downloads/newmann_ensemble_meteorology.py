#!/usr/bin/env python
# coding: utf-8

# US Precipitation and Temperature Analysis
# ====
# 
# Example of an analysis of gridded ensemble precipitation and temperature estimates over the contiguous United States
# 
# by [Joe Hamman](https://github.com/jhamman/) and [Matthew Rocklin](https://github.com/mrocklin/)
# 
# 
# For this example, we'll open a 100 member ensemble of precipitation and temperature data. Each ensemble member is stored in a seperate netCDF file and are otherwise formatted identically. The analysis we do below is quite simple but the problem is a good illustration of an IO bound task. 
# 
# Link to dataset: https://www.earthsystemgrid.org/dataset/gridded_precip_and_temp.html

# In[ ]:



import logging
logging.captureWarnings(True)
logging.getLogger('py.warnings').setLevel(logging.ERROR)


# In[ ]:


get_ipython().run_line_magic('matplotlib', 'inline')

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt


# ### Connect to Dask Distributed Cluster

# In[ ]:


from dask.distributed import Client
client = Client(scheduler_file='/glade/scratch/jhamman/scheduler.json')
client


# ### Open the dataset using Xarray
# 
# Here we open the 100 member ensemble. Each ensemble member is stored as a single file and we use `xarray.open_mfdataset` to concatenate them along a new `ensemble` dimension. In addition to chunking along the `ensemble` dimension (defaults to 1 chunk per file), we'll also chunk along the `time` dimension. 

# In[ ]:


ds = xr.open_mfdataset('/glade/u/home/jhamman/workdir/GARD_inputs/newman_ensemble/conus_ens_[01]*',
                       engine='netcdf4', concat_dim='ensemble', chunks={'time': 366})


# In[ ]:


# These clean up tasks can be removed after xarray 0.10 is release
ds['elevation'] = ds['elevation'].isel(ensemble=0, drop=True)
ds['mask'] = ds['mask'].isel(ensemble=0, drop=True).astype(np.int)
ds['mask'] = ds['mask'].where(ds['mask'] > 0)


# #### Metadata
# Let's start by printing some metadata before we get started with the fun
# 

# In[ ]:


print('ds size in GB {:0.2f}\n'.format(ds.nbytes / 1e9))

ds.info()


# ### Figure: Domain mask
# A quick plot of the mask to give us an idea of the spatial domain we're working with
# 

# In[ ]:


ds['mask'].plot()
plt.title('mask')


# ### Look! All these arrays are dask arrays under the hood. Note the chunk sizes
# 

# In[ ]:


for name, da in ds.data_vars.items():
    print(name, da.data)


# ### Intra-ensemble range
# We can start by calculating the intra-ensemble range for all the mean daily temperature in this dataset.
# 

# In[ ]:


# calculates the long term mean along the time dimension
da_mean = ds['t_mean'].mean(dim='time')
# calculate the intra-ensemble range of long term means
da_spread = da_mean.max(dim='ensemble') - da_mean.min(dim='ensemble')
da_spread


# ### Calling compute
# The expressions above didn't actually compute anything. They just build the dask task graph. To do the computations, we call the `compute` method:

# In[ ]:


get_ipython().run_line_magic('time', 'da_spread = da_spread.compute()')


# #### Figure: Intra-ensemble range
# 

# In[ ]:


da_spread.plot(robust=True, figsize=(10, 6))
plt.title('Intra-ensemble range in mean annual temperature')


# ### Persisting data on the cluster
# 
# (Make sure you have well over 300GB of RAM on your cluster, you can change the `ensemble=slice(0, 25)` section below to use more/less ensemble members.
# 
# Most of the time spent in the last calculation was loading data from disk.  After we were done with this data, Dask threw it away to free up memory.  If we plan to reuse the same dataset many times then we may want to `persist` it in memory.

# In[ ]:


t_mean = ds['t_mean'].isel(ensemble=slice(0, 25))
t_mean = t_mean.persist()
t_mean


# Now the t_mean DataArray is resident in memory on our workers.  We can repeat our computation from last time much more quickly.

# In[ ]:


get_ipython().run_cell_magic('time', '', "temp_mean = t_mean.mean(dim='time')\nspread = temp_mean.max(dim='ensemble') - temp_mean.min(dim='ensemble')  # calculates the intra-ensemble range of long term means\nmean = spread.compute()")


# In[ ]:


mean.plot(robust=True, figsize=(10, 6))
plt.title('Intra-ensemble range in mean annual temperature')


# And we can also modify the computation and try something new.  Keeping data in memory allows to *iterate quickly*, which is the whole point of this exercise.

# In[ ]:


get_ipython().run_cell_magic('time', '', "temp_mean = t_mean.std(dim='time')\nspread = temp_mean.max(dim='ensemble') - temp_mean.min(dim='ensemble')  # calculates the intra-ensemble range of long term means\nstd = spread.compute()")


# In[ ]:


std.plot(robust=True, figsize=(10, 6))
plt.title('Intra-ensemble range in standard deviation of annual temperature')

