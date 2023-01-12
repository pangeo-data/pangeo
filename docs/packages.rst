.. _packages:

Packages
========

Pangeo is not one specific software package. It's a community built around open
science. Members of the pangeo community have integrated many different
open-source software packages, each of which has its own source repository,
documentation, and development team.

This page discusses some of the core packages used within Pangeo, and some
best practices libraries should follow to work well with other packages in the
pangeo ecosystem.

If you're interested in learning how to use these packages, consult either the
project's documentation or the `Project Pythia`_ site.

.. note::

  Many people and organizations were involved in the development of the
  software described on this page. Most of them have no formal affiliation with Pangeo.
  By listing software packages on this website, we are in no way claiming
  credit for their hard work. Full information about the developers
  responsible for creating these tools can be found by following the links
  below.

Pangeo Core Packages
--------------------

Because of the :ref:`architecture` of Pangeo environments, these core
packages are considered essential to the project.

Xarray
~~~~~~

.. image:: https://github.com/pydata/xarray/raw/main/doc/_static/dataset-diagram-logo.png
   :width: 300 px

- Website: http://xarray.pydata.org/en/latest
- GitHub: https://github.com/pydata/xarray

Xarray is an open source project and Python package
that provides a toolkit for working with labeled multi-dimensional arrays of
data. Xarray adopts the `Common Data Model`_ for self-describing scientific data in widespread use in the Earth sciences. An
``xarray.Dataset`` is an in-memory representation of a netCDF_ file.
Xarray provides the basic data structures used by many other Pangeo packages,
as well as powerful tools for computation and visualization.

.. _Common Data Model: http://www.unidata.ucar.edu/software/thredds/current/netcdf-java/CDM
.. _netCDF: http://www.unidata.ucar.edu/software/netcdf


Iris
~~~~

.. image:: _static/Iris_logo_banner.png

- Website: https://scitools.org.uk/iris/docs/latest/
- GitHub: https://github.com/SciTools/iris

Iris seeks to provide a powerful, easy to use, and community-driven Python
library for analysing and visualising meteorological and oceanographic data sets.

With Iris you can:

- Use a single API to work on your data, irrespective of its original format.
- Read and write (CF-)netCDF, GRIB, and PP files.
- Easily produce graphs and maps via integration with matplotlib and cartopy.

Iris is an alternative to Xarray. Iris is developed primarily by the
UK `Met Office`_ Analysis, Visualisation and Data team (AVD).

.. _Met Office: http://www.metoffice.gov.uk/

Dask
~~~~

.. image:: _static/dask_horizontal_no_pad.svg
   :width: 300 px

- Website: http://dask.readthedocs.io/en/latest/
- GitHub: https://github.com/dask/dask

Dask is a flexible parallel computing library for analytics.
Dask is the key to the scalability of the Pangeo platform; its data structures are
capable of representing extremely large datasets without actually loading them
in memory, and its distributed schedulers permit supercomputers and cloud
computing clusters to efficiently parallelize computations across many nodes.

Jupyter
~~~~~~~

.. image:: _static/jupyter-logo.svg
  :height: 160 px

- Website: http://jupyter.org/
- GitHub: https://github.com/jupyter


Project Jupyter exists to develop open-source software, open-standards, and
services for interactive computing across dozens of programming languages.
Jupyter provides the interactive layer to the Pangeo platform, allowing
scientists to interact with remote systems where data and computing resources
live.


Pangeo Affiliated Packages
--------------------------

There are many other python packages that can work with the core packages
to provide additional functionality.
We plan to eventually catalog these packages here on the Pangeo website.
For now, please refer to the
`Xarray list of related projects <http://xarray.pydata.org/en/latest/faq.html#what-other-projects-leverage-xarray>`_.


Guidelines for New Packages
---------------------------

Our vision for the Pangeo project is an ecosystem of mutually compatible
Geoscience python packages which follow open-source best practices.
These practices are well established across the scientific python
community.

General Best Practices for Open Source
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

How to develop and maintain an open-source project is a large topic that extends beyond pangeo.
The `pyOpenSci Package Development Guide`_ provides a comprehensive guide.

Projects can submit their package for peer review from pyOpenSci.

Best Practices for Pangeo Projects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In addition to general software best practices, there are some additional
best-practices packages to work well with the pangeo ecosystem.

1. *Solve a general problem*

   Packages should solve a general problem that is encountered by a relatively
   broad groups of users.

2. *Clearly define a scope*
 
   Packages should have a clear and relatively narrow scope, solving the
   specific problem[s] identified in the point above (rather than attempting to
   cover every possible aspect of geoscience research computing). By consuming
   and producing standard data containers (see below) packages can compose
   together to solve large problems.

3. *Avoid duplication*

   Developers should try to leverage existing packages as much as possible to
   avoid duplication of effort. (In early-stage development and experimentation,
   however, some duplication will be inevitable as developers try implementing
   different solutions to the same general problems.)

4. *Consume and produce standard data container*

   Packages should consume and produce standard data containers like
   ``xarray.Dataset`` and ``geopandas.GeoDataFrame``. This facilitate
   interoperability between packages in the ecosystem.

5. *Avoid data I/O where possible*

   Unless the package is specifically focused on reading or writing data, it
   should probably not include its own custom code for reading and writing data.
   Instead, it should produce and consume standard data containers.

   Where data I/O is required, package should use existing libraries (e.g. Zarr
   via Xarray, geoparquet via geopandas, etc.). This ensures that the data
   reading and writing works with a large variety of file systems.

6. *Operate Lazily*

   Whenever possible, packages should avoid explicitly triggering computation on
   Dask objects. Instead, they should return standard data containers that can
   be backed by lazy Dask objects. This allows users to control when computation
   actually occurs.

Why Xarray and Dask?
~~~~~~~~~~~~~~~~~~~~

The Pangeo project strongly encourages the use of Xarray data structures
wherever possible. Xarray Dataset and DataArrays contain
multidimensional numeric array data and also the metadata describing the
data's coordinates, labels, units, and other relevant attributes. Xarray
makes it easy to keep this important metadata together with the raw
data; applications can then take advantage of the metadata to perform
calculations or create visualizations in a coordinate-aware fashion. The
use of Xarray eliminates many common bugs, reduces the need to write
boilerplate code, makes code easier to understand, and generally makes
users and developers happier and more productive in their day-to-day
scientific computing.

Xarray's data model is explicitly based on the `CF
Conventions <http://cfconventions.org/>`__, a well-established community
standard which encompasses many different common scenarios encountered
in Earth System science. However, Xarray is flexible and does not
*require* compliance with CF conventions. We encourage Pangeo packages
to follow CF conventions wherever it makes sense to do so.

Most geoscientists have encountered the CF data model via the ubiquitous
`netCDF file format <https://www.unidata.ucar.edu/software/netcdf/>`__.
While Xarray can easily read and write netCDF files, it doesn't have to.
This is a key difference between software built on Xarray and numerous
other tools designed to process netCDF data (e.g. nco, cdo, etc. etc.):
*Xarray data can be passed directly between python libraries (or over a
network) without ever touching a disk drive.* This "in-memory"
capability is a key ingredient to the big data scalability of Pangeo
packages. Very frequently the bottleneck in data processing pipelines is
reading and writing files.

Another important aspect of scalability is the use of Dask for parallel
and out-of-core computations. The raw data underlying Xarray objects can
be either standard in-memory `numpy arrays <http://www.numpy.org/>`__ or
`Dask arrays <http://dask.pydata.org/en/latest/array.html>`__. Dask
arrays behave nearly identically to numpy arrays (they support the same
API), but instead of storing raw data, they store a symbolic
computational graph of operations. An example computational graph would start by reading data from disk or
network and then preform transformations or mathematical calculations. No operations are
actually executed until actual numerical values are required, such as
for making a figure. This is called *lazy execution*. Dask figures out
how to execute these computational graphs efficiently on different
computer architectures using sophisticated techniques. By chaining
operations on dask arrays together, researchers can symbolically
represent large and complex data analysis pipelines and then deploy them
effectively on large computer clusters.

.. _Project Pythia: https://projectpythia.org/
.. _pyOpenSci Package Development Guide:  https://www.pyopensci.org/python-package-guide/
.. _rechunker: https://rechunker.readthedocs.io/en/latest/
.. _fsspec: https://filesystem-spec.readthedocs.io/en/latest/