.. _packages:

Packages
========

Pangeo is not one specific software package.
A Pangeo environment is made of up of many different open-source software packages.
Each of these packages has its own repository, documentation, and development team.

.. note::

  Many people and organizations were involved in the development of the
  software described on this page. Most of them have nothing to do with Pangeo.
  By listing software packages on this website, we are in no way claiming
  credit for their hard work. Full information about the developers
  responsible for creating these tools can be found by following the links
  below.

Pangeo Core Packages
--------------------

Because of the :ref:`architecture` of Pangeo environments, these three core
packages are considered essential to the project.

Xarray
~~~~~~

.. image:: https://github.com/pydata/xarray/raw/master/doc/_static/dataset-diagram-logo.png
   :width: 300 px

- Website: http://xarray.pydata.org/en/latest
- GitHub: https://github.com/pydata/xarray

Xarray is an open source project and Python package
that provides a toolkit for working with labeled multi-dimensional arrays of
data. Xarray adopts the `Common Data Model`_ for self-
describing scientific data in widespread use in the Earth sciences:
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
`UK Met Office<http://www.metoffice.gov.uk/>` Analysis, Visualisation and Data team (AVD).

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

1. Use an open-source license. See `Jake VanderPlas' article on
   licensing scientific
   code <http://www.astrobetter.com/blog/2014/03/10/the-whys-and-hows-of-licensing-scientific-code/>`__
   or `these more general guidelines <https://choosealicense.com/>`__
2. Use version control for source code (for example, on
   `github <http://github.org>`__)
3. Provide thorough test coverage and continuous integration of testing
4. Maintain comprehensive Documentation
5. Establish a `code of
   conduct <https://opensource.guide/code-of-conduct/>`__ for
   contributors

The `open-source guide <https://opensource.guide/>`__ provides some
great advice on building and maintaining open-source projects.

Best Practices for Pangeo Projects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To address the needs of geoscience researchers, we have developed some
additional recommendations.

1. *Solve a general problem:* packages should solve a general problem
   that is encountered by a relatively broad groups of researchers.
2. *Clearly defined scope:* packages should have a clear and relatively
   narrow scope, solving the specific problem[s] identified in the point
   above (rather than attempting to cover every possible aspect of
   geoscience research computing).
3. *No duplication:* developers should try to leverage existing packages
   as much as possible to avoid duplication of effort. (In early-stage
   development and experimentation, however, some duplication will be
   inevitable as developers try implementing different solutions to the
   same general problems.)
4. *Consume and Produce Xarray Objects:* Xarray data structures
   facilitate mutual interoperability between packages.
5. *Operate Lazily:* whenever possible, packages should avoid explicitly
   triggering computation on Dask objects.

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
capability is a key ingredient to the Big-Data scalability of Pangeo
packages. Very frequently the bottleneck in data processing pipelines is
reading and writing files.

Another important aspect of scalability is the use of Dask for parallel
and out-of-core computations. The raw data underlying Xarray objects can
be either standard in-memory `numpy arrays <http://www.numpy.org/>`__ or
`Dask arrays <http://dask.pydata.org/en/latest/array.html>`__. Dask
arrays behave nearly identically to numpy arrays (they support the same
API), but instead of storing raw data directly, they store a symbolic
computational graph of operations (e.g. reading data from disk or
network, performing transformations or mathematical calculations, etc.)
that must be executed in order to obtain the data. No operations are
actually executed until actual numerical values are required, such as
for making a figure. (This is called *lazy execution*.) Dask figures out
how to execute these computational graphs efficiently on different
computer architectures using sophisticated techniques. By chaining
operations on dask arrays together, researchers can symbolically
represent large and complex data analysis pipelines and then deploy them
effectively on large computer clusters.
