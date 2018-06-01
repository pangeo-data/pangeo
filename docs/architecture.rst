Technical Architecture
======================

Interoperability, extensibility, and portability are core concepts defining
the Pangeo technical architecture. Rather than designing and creating a single
monolithic application, our vision is an ecosystem of tools that can be used
together. We want you to be able to easily build your own Pangeo, whatever that
means to you.

Where we began
--------------

In large part, Pangeo began as a group of `Xarray`_ users and developers that
were working on various big-data geoscience problems. The typical software and
hardware stack we envisioned for Pangeo is shown in the figure below.

.. image:: _static/pangeo_tech_1.png
   :height: 300px

The key concepts and tools we envisioned in the Pangeo ecosystem were:

- Ability to use high-level data models (e.g. `Xarray`_)
- Ability to leverage parallel computing (e.g. `Dask`_) on HPC systems or on
  cloud computing systems
- Ability to work interactively (e.g. `Jupyter`_) or using batch processing

Although we originally envisioned Pangeo's focus to be on improving the
integration of Xarray, Dask, and Jupyter on HPC systems, the scope of the
project has grown substantially.

Interoperability in Pangeo
--------------------------

Pangeo's ecosystem of interoperable tools allows users to pick and choose from a
collection of related but independent packages. This facilitates portability and
customization in user workflows. The illustration below highlights some of the
interchangeable components within Pangeo.

.. image:: _static/Slide3.jpeg
   :height: 400px

*This figure is a placeholder while we work on something better*

Software
--------

Python
~~~~~~

Data Models
~~~~~~~~~~~

Arrays
~~~~~~


Compute Platforms
-----------------

HPC
~~~

Large homogeneous high-performance computing clusters are the most common
big-data computing platform in the geosciences today. They often offer many
compute nodes, fast interconnects, and parallel file systems - all of which can
be used to facilitate rapid scientific analysis.

Pangeo utilizes

Cloud
~~~~~

Storage Formats
---------------

NetCDF
~~~~~~

Storage on the Cloud
~~~~~~~~~~~~~~~~~~~~




.. _Xarray: http://xarray.pydata.org
.. _Dask: https://dask.pydata.org
.. _Jupyter: https://jupyter.org
