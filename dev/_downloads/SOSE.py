#!/usr/bin/env python
# coding: utf-8

# # SOSE Heat and Salt Budgets
# 
# Evaluating the conservation of heat and salt content in the Southern Ocean State Estimate 
# 
# Author: [Ryan Abernathey](http://github.com/rabernat)
# 
# ![SOSE Logo](http://sose.ucsd.edu/images/SOSEpic.png)
# 
# ## Connect to Dask Cluster
# 
# Below we create a dask cluster with 30 nodes to do our work for us.

# In[ ]:


from dask.distributed import Client, progress
from dask_kubernetes import KubeCluster
cluster = KubeCluster(n_workers=50)
cluster


# ** ☝️ don't forget to follow along on the dashboard **

# In[ ]:


client = Client(cluster)
client


# Import necessary Python packages

# In[ ]:


import xarray as xr
from matplotlib import pyplot as plt
import gcsfs
import dask
import dask.array as dsa
import numpy as np
get_ipython().run_line_magic('matplotlib', 'inline')


# ## Open SOSE Dataset from Cloud Storage

# In[ ]:


ds = xr.open_zarr(gcsfs.GCSMap('pangeo-data/SOSE'))
ds


# In[ ]:


print('Total Size: %6.2F GB' % (ds.nbytes / 1e9))


# A trick for optimization: split the dataset into coordinates and data variables, and then drop the coordinates from the data variables.
# This makes it easier to align the data variables in arithmetic operations.

# In[ ]:


coords = ds.coords.to_dataset().reset_coords()
dsr = ds.reset_coords(drop=True)
dsr


# In[ ]:


coords


# ## Visualize Some Data
# 
# As a sanity check, let's look at some values.

# In[ ]:


import holoviews as hv
from holoviews.operation.datashader import regrid
hv.extension('bokeh')


# In[ ]:


get_ipython().run_cell_magic('opts', "Image [width=900, height=400 colorbar=True] (cmap='Magma')", "\nhv_image = hv.Dataset(ds.THETA.where(ds.hFacC>0).rename('THETA')).to(hv.Image, kdims=['XC', 'YC'], dynamic=True)\nwith dask.config.set(scheduler='single-threaded'):\n    display(regrid(hv_image, precompute=True))")


# ## Create xgcm grid
# 
# [Xgcm](http://xgcm.readthedocs.io) is a package which helps with the analysis of GCM data.

# In[ ]:


import xgcm
grid = xgcm.Grid(ds, periodic=('X', 'Y'))
grid


# ## Tracer Budgets
# 
# Here we will do the heat and salt budgets for SOSE. In integral form, these budgets can be written as
# 
# $$
# \mathcal{V} \frac{\partial S}{\partial t} = G^S_{adv} + G^S_{diff} + G^S_{surf} + G^S_{linfs}
# $$
# 
# 
# $$
# \mathcal{V} \frac{\partial \theta}{\partial t} = G^\theta_{adv} + G^\theta_{diff} + G^\theta_{surf} + G^\theta_{linfs} + G^\theta_{sw}
# $$
# 
# where $\mathcal{V}$ is the volume of the grid cell. The terms on the right-hand side are called _tendencies_. They add up to the total tendency (the left hand side).
# 
# The first term is the convergence of advective fluxes. The second is the convergence of diffusive fluxes. The third is the explicit surface flux. The fourth is the correction due to the linear free-surface approximation. The fifth is shortwave penetration (only for temperature).
# 
# ### Flux Divergence
# 
# First we define a function to calculate the convergence of the advective and diffusive fluxes, since this has to be repeated for both tracers.

# In[ ]:


def tracer_flux_budget(suffix):
    """Calculate the convergence of fluxes of tracer `suffix` where 
    `suffix` is `TH` or `SLT`. Return a new xarray.Dataset."""
    conv_horiz_adv_flux = -(grid.diff(dsr['ADVx_' + suffix], 'X') +
                          grid.diff(dsr['ADVy_' + suffix], 'Y')).rename('conv_horiz_adv_flux_' + suffix)
    conv_horiz_diff_flux = -(grid.diff(dsr['DFxE_' + suffix], 'X') +
                          grid.diff(dsr['DFyE_' + suffix], 'Y')).rename('conv_horiz_diff_flux_' + suffix)
    # sign convention is opposite for vertical fluxes
    conv_vert_adv_flux = grid.diff(dsr['ADVr_' + suffix], 'Z', boundary='fill').rename('conv_vert_adv_flux_' + suffix)
    conv_vert_diff_flux = (grid.diff(dsr['DFrE_' + suffix], 'Z', boundary='fill') +
                           grid.diff(dsr['DFrI_' + suffix], 'Z', boundary='fill') +
                           grid.diff(dsr['KPPg_' + suffix], 'Z', boundary='fill')).rename('conv_vert_diff_flux_' + suffix)
    
    all_fluxes = [conv_horiz_adv_flux, conv_horiz_diff_flux, conv_vert_adv_flux, conv_vert_diff_flux]
    conv_all_fluxes = sum(all_fluxes).rename('conv_total_flux_' + suffix)
    
    return xr.merge(all_fluxes + [conv_all_fluxes])


# In[ ]:


budget_slt = tracer_flux_budget('SLT')
budget_slt


# In[ ]:


budget_th = tracer_flux_budget('TH')
budget_th


# ### Surface Fluxes
# 
# The surface fluxes are only active in the top model layer. We need to specify some constants to convert to the proper units and scale factors to convert to integral form. They also require some xarray special sauce to merge with the 3D variables.

# In[ ]:


# constants
heat_capacity_cp = 3.994e3
runit2mass = 1.035e3

# treat the shortwave flux separately from the rest of the surface flux
surf_flux_th = (dsr.TFLUX - dsr.oceQsw) * coords.rA / (heat_capacity_cp * runit2mass)
surf_flux_th_sw = dsr.oceQsw * coords.rA / (heat_capacity_cp * runit2mass)

# salt
surf_flux_slt = dsr.SFLUX * coords.rA  / runit2mass
lin_fs_correction_th = -(dsr.WTHMASS.isel(Zl=0, drop=True) * coords.rA)
lin_fs_correction_slt = -(dsr.WSLTMASS.isel(Zl=0, drop=True) * coords.rA)

# in order to align the surface fluxes with the rest of the 3D budget terms,
# we need to give them a z coordinate. We can do that with this function
def surface_to_3d(da):
    da.coords['Z'] = dsr.Z[0]
    return da.expand_dims(dim='Z', axis=1)


# ### Shortwave Flux
# 
# Special treatment is needed for the shortwave flux, which penetrates into the interior of the water column

# In[ ]:


def swfrac(coords, fact=1., jwtype=2):
    """Clone of MITgcm routine for computing sw flux penetration.
    z: depth of output levels"""
    
    rfac = [0.58 , 0.62, 0.67, 0.77, 0.78]
    a1 = [0.35 , 0.6  , 1.0  , 1.5  , 1.4]
    a2 = [23.0 , 20.0 , 17.0 , 14.0 , 7.9 ]
    
    facz = fact * coords.Zl.sel(Zl=slice(0, -200))
    j = jwtype-1
    swdk = (rfac[j] * np.exp(facz / a1[j]) +
            (1-rfac[j]) * np.exp(facz / a2[j]))
            
    return swdk.rename('swdk')

_, swdown = xr.align(dsr.Zl, surf_flux_th_sw * swfrac(coords), join='left', )
swdown = swdown.fillna(0)


# In[ ]:


# now we can add the to the budget datasets and they will align correctly
# into the top cell (lazily filling with NaN's elsewhere)
budget_slt['surface_flux_conv_SLT'] = surface_to_3d(surf_flux_slt)
budget_slt['lin_fs_correction_SLT'] = surface_to_3d(lin_fs_correction_slt)
budget_slt


# In[ ]:


budget_th['surface_flux_conv_TH'] = surface_to_3d(surf_flux_th)
budget_th['lin_fs_correction_TH'] = surface_to_3d(lin_fs_correction_th)
budget_th['sw_flux_conv_TH'] = -grid.diff(swdown, 'Z', boundary='fill').fillna(0.)
budget_th


# ### Add it all up
# 
# The total tendency should be given by

# In[ ]:


budget_th['total_tendency_TH'] = (budget_th.conv_total_flux_TH + 
                                  budget_th.surface_flux_conv_TH.fillna(0.) +
                                  budget_th.lin_fs_correction_TH.fillna(0.) + 
                                  budget_th.sw_flux_conv_TH)
budget_th


# In[ ]:


budget_slt['total_tendency_SLT'] = (budget_slt.conv_total_flux_SLT + 
                                    budget_slt.surface_flux_conv_SLT.fillna(0.) +
                                    budget_slt.lin_fs_correction_SLT.fillna(0.))
budget_slt


# ### Include the "truth"
# 
# MITgcm keeps track of the true total tendence in the `TOT?TEND` variables.
# We can use these as check on our budget calculation.

# In[ ]:


volume = (coords.drF * coords.rA * coords.hFacC)
client.scatter(volume)
day2seconds = (24*60*60)**-1

budget_th['total_tendency_TH_truth'] = dsr.TOTTTEND * volume * day2seconds
budget_slt['total_tendency_SLT_truth'] = dsr.TOTSTEND * volume * day2seconds


# ## Validate Budget
# 
# Now we do some checks to verify that the budget adds up.
# 
# ### Vertical and Horizontal Integrals of Budget
# 
# We will take an average over the first 10 timesteps

# In[ ]:


time_slice = dict(time=slice(0, 10))


# In[ ]:


valid_range = dict(YC=slice(-90,-30))

def check_vertical(budget, suffix):
    ds_chk = (budget[[f'total_tendency_{suffix}', f'total_tendency_{suffix}_truth']]
              .sel(**valid_range).sum(dim=['Z', 'XC']).mean(dim='time'))
    return ds_chk

def check_horizontal(budget, suffix):
    ds_chk = (budget[[f'total_tendency_{suffix}', f'total_tendency_{suffix}_truth']]
              .sel(**valid_range).sum(dim=['YC', 'XC']).mean(dim='time'))
    return ds_chk


# In[ ]:


th_vert = check_vertical(budget_th.isel(**time_slice), 'TH').load()
th_vert.total_tendency_TH.plot(linewidth=2)
th_vert.total_tendency_TH_truth.plot(linestyle='--', linewidth=2)
plt.legend()


# In[ ]:


th_horiz = check_horizontal(budget_th.isel(**time_slice), 'TH').load()
th_horiz.total_tendency_TH.plot(linewidth=2, y='Z')
th_horiz.total_tendency_TH_truth.plot(linestyle='--', linewidth=2, y='Z')
plt.legend()


# In[ ]:


slt_vert = check_vertical(budget_slt.isel(**time_slice), 'SLT').load()
slt_vert.total_tendency_SLT.plot(linewidth=2)
slt_vert.total_tendency_SLT_truth.plot(linestyle='--', linewidth=2)
plt.legend()


# In[ ]:


slt_horiz = check_horizontal(budget_slt.isel(**time_slice), 'SLT').load()
slt_horiz.total_tendency_SLT.plot(linewidth=2, y='Z')
slt_horiz.total_tendency_SLT_truth.plot(linestyle='--', linewidth=2, y='Z')
plt.legend()


# ### Histogram Analysis of Error
# 
# The curves look the same. But how do we know whether our error is truly "small"?
# Answer: we compare the distribution of the error
# 
# $$ P( G_{est} - G_{truth} ) $$
# 
# to the distribution of the other terms in the equation, e.g. $P(G_{adv})$.
# 
# First we try to determine the appropriate range for our histograms by looking at the maximum values.

# In[ ]:


budget_th.isel(**time_slice).max().load()


# In[ ]:


budget_slt.isel(**time_slice).max().load()


# In[ ]:


# parameters for histogram calculation
th_range = (-2e7, 2e7)
slt_range = (-1e8, 1e8)
valid_region = dict(YC=slice(-90, -30))
nbins = 301


# In[ ]:


# budget errors
error_th = budget_th.total_tendency_TH - budget_th.total_tendency_TH_truth
error_slt = budget_slt.total_tendency_SLT - budget_slt.total_tendency_SLT_truth


# In[ ]:


# calculate theta error histograms over the whole time range
adv_hist_th, hbins_th = dsa.histogram(budget_th.conv_horiz_adv_flux_TH.sel(**valid_region).data,
                                        bins=nbins, range=th_range)
err_hist_th, hbins_th = dsa.histogram(error_th.sel(**valid_region).data,
                                        bins=nbins, range=th_range)
err_hist_th, adv_hist_th = dask.compute(err_hist_th, adv_hist_th)


# In[ ]:


bin_c_th = 0.5*(hbins_th[:-1] + hbins_th[1:])
plt.semilogy(bin_c_th, adv_hist_th, label='Advective Tendency')
plt.semilogy(bin_c_th, err_hist_th, label='Budget Residual')
plt.legend()
plt.title('THETA Budget')


# In[ ]:


# calculate salt error histograms over the whole time range
adv_hist_slt, hbins_slt = dsa.histogram(budget_slt.conv_horiz_adv_flux_SLT.sel(**valid_region).data,
                                        bins=nbins, range=slt_range)
err_hist_slt, hbins_slt = dsa.histogram(error_slt.sel(**valid_region).fillna(-9e13).data,
                                        bins=nbins, range=slt_range)
err_hist_slt, adv_hist_slt = dask.compute(err_hist_slt, adv_hist_slt)


# In[ ]:


bin_c_slt = 0.5*(hbins_slt[:-1] + hbins_slt[1:])
plt.semilogy(bin_c_slt, adv_hist_slt, label='Advective Tendency')
plt.semilogy(bin_c_slt, err_hist_slt, label='Budget Residual')
plt.title('SALT Budget')
plt.legend()


# These figures show that the error is extremely small compared to the other terms in the budget.
# 
# ## Weddell Sea Budget Timeseries
# 
# Finally, we can do some science: compute the salinity budget for a specific region, such as the upper Weddell Sea.

# In[ ]:


budget_slt_weddell = (budget_slt
                        .sel(YC=slice(-80, -68), XC=slice(290, 360), Z=slice(0, -500))
                        .sum(dim=('XC', 'YC', 'Z'))
                        .load())
budget_slt_weddell


# In[ ]:


plt.figure(figsize=(18,8))
for v in budget_slt_weddell.data_vars:
    budget_slt_weddell[v].rolling(time=30).mean().plot(label=v)
plt.ylim([-4e7, 4e7])
plt.legend()
plt.grid()
plt.title('Weddell Sea Salt Budget')


# In[ ]:


plt.figure(figsize=(18,8))
for v in budget_slt_weddell.data_vars:
    budget_slt_weddell[v].rolling(time=30).mean().plot(label=v)
plt.ylim([-4e6, 4e6])
plt.legend()
plt.grid()
plt.title('Weddell Sea Salt Budget')


# These figures show that, while they advective terms are the largest ones in the budget, the actual variability in salinity is driven primarily by the surface fluxes.
# 
# ### Removing Climatlogy
# 
# The timeseries is pretty short, but nevertheless we can try to remove the climatology to get a better idea of what drives the interannual variability

# In[ ]:


budget_slt_weddell_mm = budget_slt_weddell.groupby('time.month').mean(dim='time')
budget_slt_weddell_anom = budget_slt_weddell.groupby('time.month') - budget_slt_weddell_mm


# In[ ]:


plt.figure(figsize=(18,8))
for v in budget_slt_weddell.data_vars:
    budget_slt_weddell_anom[v].rolling(time=30).mean().plot(label=v)
plt.ylim([-2.5e7, 2.5e7])
plt.legend()
plt.grid()
plt.title('Weddell Sea Anomaly Salt Budget')


# In[ ]:


plt.figure(figsize=(18,8))
for v in budget_slt_weddell.data_vars:
    budget_slt_weddell_anom[v].rolling(time=30).mean().plot(label=v)
plt.ylim([-2.5e6, 2.5e6])
plt.legend()
plt.grid()
plt.title('Weddell Sea Anomaly Salt Budget')


# The monthly anomaly is also premoninantly driven by surface forcing.
