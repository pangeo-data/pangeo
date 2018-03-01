.. _packages:

Pangeo Packages
===============

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
   facilitate mutual interoperability between packages. (For more about
   Xarray , see below.)
5. *Operate Lazily:* whevever possible, packages should avoid explicitly
   triggering computation on
   `Dask <http://dask.pydata.org/en/latest/array.html>`__ objects. (For
   more about Dask, see below)

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
