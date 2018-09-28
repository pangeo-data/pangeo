.. _data:

Pangeo and Data
===============

Pangeo provides the computational tools to do scalable analysis of large
geoscience datasets.
For decades, our field has operated on a "download model," under which
scientists download the data they wish to analyze from remote FTP servers
to their personal computers.
Pangeo operates on a different philosophy; instead of bringing the data to the
computer, we bring the computer to the data.
The Pangeo :ref:`deployments` provide high-performance computing clusters in
close proximity to high-performance storage.
Many widely used datasets are already stored on these systems.

If you are interested in analyzing a specific large dataset, you should
attempt to determine if this dataset is already stored on an existing
:ref:`deployments`; you can then request access to that specific deployment to
perform your analysis.
Alternatively, if you lab or group already operates a data repository, you can
consider deploying a Pangeo environment on computing resources proximal to the
data server (consult the :ref:`setup-guides` for more detail).

We envision a future in which all relevant data is readily accessible to
scalable computing; this will likely require the large-scale migration to the
cloud.
We aren't there yet, but Pangeo is working towards this goal.

.. note::

  The capability to read data in pangeo is dependent on the underlying
  :ref:`packages`. The file formats and options are largely determined by:

  - `Xarray's I/O options <http://xarray.pydata.org/en/latest/io.html>`_
  - `Iris's I/O options <https://scitools.org.uk/iris/docs/latest/userguide/loading_iris_cubes.html>`_
  - `Pandas's I/O options <https://pandas.pydata.org/pandas-docs/stable/io.html>`_

Data on HPC
-----------

Many high-performance computing clusters serve as de-facto data repositories,
particularly for the model simulations that run on those systems. Pangeo
provides a way to leverage those same systems for data analysis.
The most common data formats encountered on HPC systems are netCDF_ and HDF_.
Pangeo on HPC works well with the standard archives of netCDF files commonly
encountered on such systems.

Particular effort has been made to integrate Pangeo with the systems operated
by NCAR's `Computational and Information Systems Lab <CISL>`_, in particular
the Cheyenne, Geyser, and Caldera clusters.
NCAR's `Research Data Archive`_ catalogs a huge number of datasets available
from those clusters via the GLADE file systems.
All of those datasets are accessible to Pangeo now via the Cheyenne deployment.

Specific use case examples which load data from HPC platforms include:

- Sean's thing
- What else?

Data in the Cloud
-----------------

The Pangeo community is very excited about the opportunities presented by the
cloud for scientific research in terms of scalability, reproducibility, and
efficiency.
However, the cloud presents new challenges; the data formats that work well
on personal computers and HPC systems don't necessarily translate well to the
cloud environment.
For an overview of these challenges, we recommend Matt Rocklin's excellent
blog post:

- `HDF in the Cloud: challenges and solutions for scientific data <http://matthewrocklin.com/blog/work/2018/02/06/hdf-in-the-cloud>`_

The Pangeo community is actively engaged in defining what constitutes
"analysis ready geoscience data" on the cloud.
We are experimenting with many different technologies and options.
This is a rapidly evolving area.
If you have ideas on this topic you would like to share with our community,
please  `reach out to us on Github <https://github.com/pangeo-data/pangeo/issues>`_.

Our *current preference* for storing multidimensional array data in the cloud
is the Zarr_ format.
Zarr is a new storage format which, thanks to its simple yet well-designed
specification, makes large datasets easily accessible to distributed computing.
In Zarr datasets, the arrays are divided into chunks and compressed.
These individual chunks can be stored as files on a filesystem or as objects
in a cloud storage bucket.
The metadata are stored in lightweight ``.json`` files.
Zarr works well on both local filesystems and cloud-based object stores.
Existing datasets can easily be converted to zarr via
`xarray's zarr functions <http://xarray.pydata.org/en/latest/io.html#zarr>`_.

Google Cloud Storage Data Catalog
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Thanks to our :ref:`NSF Award <earthcube>`, Pangeo has a substantial allocation
on Google Cloud Platform which we are currently using to host several large
datasets.
These datasets are directly accessible from the Google Cloud Pangeo deployment:
`pangeo.pydata.org <http://pangeo.pydata.org>`_.

See the list of available data sets in the :ref:`data catalog <catalog>`.

.. _cloud-data-guide:

Guide to Preparing Cloud-Optimized Data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

How do you get data into the cloud in a format that is optimized for pangeo
to read?
This guide outlines our current practices for converting netCDF data to
Zarr_ and placing it on the cloud.
These recommendations may change as cloud storage technology evolves.

.. note::

  One important difference between local data storage and cloud data storage is
  that local storage is based on *individual files* while Zarr_ is based on
  *entire datasets* (which may be derived from many individual files, a.k.a.
  "granules"). When preparing data for cloud storage, you should ask
  *what is the entire dataset we want to work with?* That's what you will be
  preparing and uploading.

.. why doesn't the intersphinx :py:meth:`xarray.open_mfdataset` link work?

#. **Open your Entire Dataset in Xarray**.

   Xarray is designed to
   load many netCDF files into a single :py:class:`xarray.DataArray` object.
   The easiest way to accomplish this is using the :py:meth:`xarray.open_mfdataset`
   function. Suppose you have a directory full of netCDF files that comprise
   a single dataset stored in the directory ``/path/to/mydataset``. If the files
   are properly formatted and sufficiently homogeneous, you can open them with
   a single line of xarray code.

   .. code-block:: python

      import xarray as xr
      ds = xr.open_mfdataset('/path/to/mydataset/*.nc')

   More complicated datasets can be constructed manually by using
   :py:meth:`xarray.concat` and :py:meth:`xarray.merge` to combine individual
   files or sub-datasets into a single object.

   In creating your dataset, you should pay particular attention to the
   Dask chunk size. Consult
   `xarray's documentation on chunking and performance <http://xarray.pydata.org/en/latest/dask.html#chunking-and-performance>`_
   for guidance on choosing appropriately sized chunks. You may wish to manually
   specify the ``chunks`` argument when calling ``xarray.open_dataset``
   and ``xarray.open_mfdataset``.

   Inspect the representation of your dataset by printing its representation
   (i.e. ``print(ds)``) and examining its full metadata (``ds.info()``).
   Make sure all the expected variables and metadata are present and have the
   correct shape / chunk structure.

#. **Export to Zarr Format**

   The next step is to export your ``xarray.Dataset`` to a
   :py:class:`zarr Directory Store <zarr.storage.DirectoryStore>`. This is
   done as follows

   .. code-block:: python

      ds.to_zarr('/path/to/output/mydataset')

   If ``/path/to/output/mydataset`` does not exist yet, it will be created.
   (It's best if does not exist, as conflicts with existing files could cause
   problems.)

   If your dataset is very large, this can take a very long time.
   The speed is generally constrained by the rate at which the data can be read
   from the storage device where the original files are located. If you are
   on a high-performance cluster, you might consider using a dask distributed to
   parallelize the operation across multiple nodes.

   Xarray and Zarr have many different options for encoding and compression of
   the datasets. This can be passed to ``to_zarr`` via the ``encoding`` keyword
   argument. Consult the relevant
   `xarray documentation <http://xarray.pydata.org/en/latest/io.html#zarr-compressors-and-filters>`_
   and
   `zarr documentation <http://zarr.readthedocs.io/en/latest/tutorial.html#compressors>`_
   for more detail.
   In our somewhat limited experience, the default encoding and compression
   perform adequately for most purposes.

#. **Upload to Cloud Storage**

   Once the export to zarr is complete, you now upload the directory and all
   its contents to cloud storage. In order to do this step, you will need
   the command line utilities from your cloud provider installed on your system.
   In this example, we use Google Cloud Platform, which requires installing the
   :ref:`google-cloud-sdk`.

   First you must authenticate to obtain credentials to perform the upload::

     gcloud auth login

   Now you can upload the dataset to the cloud-storage bucket of your choice.
   In this example, we upload to the ``pangeo-data`` bucket on Google Cloud
   Storage::

     gsutil -m cp -r /path/to/output/mydataset gs://pangeo-data/

   This command can also take a long time to execute, depending on the size of
   your dataset and the bandwidth of your internet connection. The dataset will
   be available at the ``pangeo-data/mydataset`` path.

#. **Verify Dataset from a Pangeo Cloud Deployment**

   The data you uploaded should be read from a Pangeo deployment in the same
   cloud and the same region as the bucket in which it resides.
   Otherwise, you may suffer from diminished performance and accrue extra
   charges for data transfers.
   The ``pangeo-data`` bucket is in Google Cloud Storage in the ``US-CENTRAL1``
   region. It can therefore be accessed by the flagship
   `pangeo.pydata.org <http://pangeo.pydata.org>`_ deployment.

   To open the dataset we just uploaded from within a notebook or script in
   pangeo.pydata.org, do the following:

   .. code-block:: python

      import xarray as xr
      import gcsfs
      ds = xr.open_zarr(gcsfs.GCSMap('pangeo-data/mydataset'))

   You should see all the variables and metadata from your original dataset in
   step 1. The dataset will automatically be created with dask chunks matching
   the underlying zarr chunks.


.. _CISL: https://www2.cisl.ucar.edu/
.. _netCDF: https://www.unidata.ucar.edu/software/netcdf/
.. _HDF: https://www.hdfgroup.org/
.. _Research Data Archive: https://rda.ucar.edu/
.. _Zarr: http://zarr.readthedocs.io/en/stable/
