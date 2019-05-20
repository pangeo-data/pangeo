#!/usr/bin/env python
# coding: utf-8

# # CESM Large Ensemble Tracer Budget
# 
# Example of calculating the oceanic DIC budget
# 
# Here we calculate the DIC budget from the ocean component model (POP2) of the CESM Large Ensemble (CESM-LENS). This code can be used to create budgets, as is, for any tracer. Also, by replacing the load function in cell 6,`pl.open_pop_ensemble`, with `pl.open_pop_single_var_file` or `pl.open_pop_multi_var_file`, you can use this notebook to calculate tracer budgets with any POP2 output.
# 
# CESM-LENS is a set climate simulations that allow for the study of natural climate varability and climate change. More about the project can be found [here](http://www.cesm.ucar.edu/projects/community-projects/LENS/). To represent the full envelope of natural variability, the fully coupled version of the CESM has been run 40 times representing 40 different realizations of the period 1920-2100. Dask and xarray are the perfect tools to handle the large data volume

# In[ ]:


get_ipython().system('qselect -N dask-worker | xargs qdel')


# In[ ]:


import xarray as xr
import numpy as np
import poploader as pl # faster xarray dataset creation for POP2 (https://gist.github.com/sridge/fe5f180c7e1332212fcce0161c461716)
from tqdm import tqdm # progressbar


# In[ ]:


from dask_jobqueue import PBSCluster

cluster = PBSCluster(local_directory = '/glade/scratch/sridge/spill/',
                     processes=18,
                     threads=4, memory="6GB",
                     project='UCLB0022',
                     queue='premium',
                     resource_spec='select=1:ncpus=36:mem=109G',
                     walltime='1:00:00')
cluster.start_workers(16)

from dask.distributed import Client
client = Client(cluster)


# In[ ]:


client


# In[ ]:


tracer = 'DIC_ALT_CO2'

ddir = '/glade/scratch/sridge/*/'
outdir = '/glade/scratch/sridge/'

memberlist = [1, 2, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27,
              28, 29, 30, 31, 32, 33, 101, 102, 103, 104, 105]

memberlist = memberlist[1:5] #smaller version to test

transport_terms = ['UE_','VN_','WT_','HDIFE_','HDIFN_','HDIFB_','DIA_IMPVF_','KPP_SRC_']#,'J_']

transport_varnames=[]

for term in transport_terms:

    transport_varnames += [term + tracer]


# ## Open the Dataset
# If you're not using the ensemble, you may also want to try:
# `pl.open_pop_single_var_file`
# `pl.open_pop_multi_var_file`

# In[ ]:


# function that strips uneeded coordinate variables and groups  all model output into a single dataset
ds = pl.open_pop_ensemble(ddir, transport_varnames[0:8], memberlist)


# In[ ]:


ds


# In[ ]:


# # J_DIC was averaged with nco. Need to open separate ds and then correct time 
# ds_J = pl.open_pop_ensemble(ddir, [transport_varnames[8]], memberlist)


# In[ ]:


# ds_J['time'] = ds['time']

# ds = xr.merge([ds,ds_J])
# ds.chunk({'time': 1})


# ## Convert Units
# All terms are converted to nmol/s

# In[ ]:


tarea = ds['TAREA']
vol = (ds.dz)*tarea


# In[ ]:


# adjust coords to z_t for later computation of divergence
hdifb_t = ds['HDIFB_' + tracer]
hdifb_t = hdifb_t.rename({'z_w_bot':'z_t'})
hdifb_t['z_t'] = ds['z_t']

wt_t = ds['WT_' + tracer]
wt_t = wt_t.rename({'z_w_top':'z_t'})
wt_t['z_t'] = ds['z_t']


# In[ ]:


# terms in units of mmol m^{-3} s^{-1}
transport_terms = ['UE_','VN_','HDIFE_','HDIFN_','KPP_SRC_']#,'J_']

for term in tqdm(transport_terms):
    
  ds[term + tracer] = ds[term + tracer]*vol
  ds[term + tracer].attrs['units'] = 'nmol/s'
  
wt_t = wt_t*vol
print('WT_' + tracer)
hdifb_t = hdifb_t*vol
print('HDIFB_' + tracer)


# In[ ]:


# DIA_IMPVF is in units of mmol m^{-2} cm s^{-1} 
# convert to mmol s^{-1} 
ds['DIA_IMPVF_' + tracer] = (ds['DIA_IMPVF_' + tracer])*tarea
ds['DIA_IMPVF_' + tracer].attrs['units'] = 'nmol/s'

# adjust coords to z_t for later computation of divergence
diadiff_t = ds['DIA_IMPVF_' + tracer]
diadiff_t = diadiff_t.rename({'z_w_bot':'z_t'})
diadiff_t['z_t'] = ds['z_t']


# In[ ]:


ue_t = ds['UE_' + tracer]
vn_t = ds['VN_' + tracer]
wt_t = wt_t
hdife_t = ds['HDIFE_' + tracer]
hdifn_t = ds['HDIFN_' + tracer]
hdifb_t = hdifb_t
# bio_sms_t = ds['J_' + tracer]
kpp_sms_t = ds['KPP_SRC_' + tracer]
diadiff_t = diadiff_t


# ## Calculate Divergence
# Methods are described in the __[POP Manual](http://www.cesm.ucar.edu/models/cesm2.0/ocean/doc/sci/POPRefManual.pdf)__ 

# ## Vertical Divergence: Resolved Advection

# In[ ]:


wt_t_kp1  = wt_t.shift(z_t=-1).fillna(0.)
wdiv_t = wt_t_kp1 - wt_t
wdiv_t.attrs['units'] = 'nmol/s'


# ## Vertical Divergence: Submesoscale Eddies and Isopycnal Diffusion

# In[ ]:


hdifb_t_km1 = hdifb_t.shift(z_t=1).fillna(0.)
wdiv_hdifb_t = hdifb_t_km1 - hdifb_t
wdiv_hdifb_t.attrs['units'] = 'nmol/s'


# ## Vertical Divergence: Diapycnal Diffusion 
# (KPP parameterization, __[Large et al. 1994](http://www.cesm.ucar.edu/models/cesm2.0/ocean/doc/sci/POPRefManual.pdf)__)
# 

# In[ ]:


diadiff_t_km1 = diadiff_t.shift(z_t=1).fillna(0.)
wdiv_diadiff_t = diadiff_t_km1 - diadiff_t
wdiv_diadiff_t.attrs['units'] = 'nmol/s'


# ## Horizontal Divergence: Resolved Advection

# In[ ]:


ue_t_im1 = ue_t.roll(nlon=1)
udiv_t = ue_t_im1 - ue_t

vn_t_jm1 = vn_t.roll(nlat=1)
vdiv_t = vn_t_jm1 - vn_t

udiv_t.attrs['units'] = 'nmol/s'
vdiv_t.attrs['units'] = 'nmol/s'

hdiv_t = udiv_t + vdiv_t


# ## Horizontal Divergence: Submesoscale Eddies and Isopycnal Diffusion

# In[ ]:


hdife_t_im1 = hdife_t.roll(nlon=1)
udiv_hdife_t = hdife_t - hdife_t_im1

hdifn_t_jm1 = hdifn_t.roll(nlat=1)
vdiv_hdifn_t = hdifn_t - hdifn_t_jm1

udiv_hdife_t.attrs['units'] = 'nmol/s'
vdiv_hdifn_t.attrs['units'] = 'nmol/s'

hdiv_hdif_t = udiv_hdife_t + vdiv_hdifn_t


# ## Write to Disk
# 
# The final product is grid cell by grid cell tracer divergence (nmol/s) that can be integrated vertically to the depth of your choosing for the column budget

# In[ ]:


# take ensemble mean and write to disk

# you don't have to worry about the warnings
# https://github.com/dask/distributed/issues/730

budget_filelist = [hdiv_t,wdiv_t,hdiv_hdif_t,wdiv_hdifb_t,kpp_sms_t,wdiv_diadiff_t]#,bio_sms_t]
budget_filelist_str = ['hdiv_','wdiv_','hdiv_hdif_','wdiv_hdifb_','kpp_sms_','wdiv_diadiff_',]#'bio_sms_']

for budget_file,budget_file_str in tqdm(zip(budget_filelist,budget_filelist_str)):
    budget_file = budget_file.mean(dim='member')
    budget_file.to_netcdf((outdir + '{}{}_{}.1850-2100.nc'.format(budget_file_str,tracer,memberlist[0])))

