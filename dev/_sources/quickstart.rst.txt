.. _quickstart:

Guide for Scientists
====================

The goal of Pangeo is to make it quicker and easier to go from raw data to
scientific insights.
We want to spend less time writing boilerplate code and be able to perform
calculations quickly and interactively on very large datasets.
Pangeo is based around the python programming language and the scientific
python software ecosystem.
Pangeo is aimed at users who already have basic familiarity with using
scientific python and are looking for ways to make their analysis workflow more
efficient, scalable, and pleasant.
If you are completely new to scientific python, you should first familiarize
yourself with the basics before moving forward with this guide.
(We recommend the `Scipy Lectures`_ as a starting point.)

Learn About Pangeo Software
---------------------------

Pangeo is not a specific software package.
A Pangeo environment is made of up of many different open-source software packages.
Each of these packages has its own repository, documentation, and development team.
You can learn more about these packages by following the links below.
This loose collection of packages is often referred to as the *Pangeo stack*.

.. toctree::
   :maxdepth: 3

   packages

For more information about how these packages relate to each other, consult the
:ref:`architecture` page.

Explore the Use Cases
---------------------

The Use Case Gallery demonstrates real-world science applications of the
Pangeo stack. The use cases are formatted as `Jupyter Notebooks`_, a
self-describing computational document including text, code, and figures.
A great way to get started is to find a use case that is similar to the
analysis you want to do and modify it to suit your needs.

.. toctree::
  :maxdepth: 2

  use_cases/index

A great way for novices to learn how to use Pangeo is to start from one of these
use cases and modify it for your needs. Many of the use cases are pre-loaded
on the Pangeo deployments listed below.

Try Out a Pangeo Deployment
---------------------------

There are several places where you can access a Pangeo deployment, from which
you can analyze large datasets in a scalable, reproducible way.

.. toctree::
   :maxdepth: 2

   deployments

If none of these meets your needs, you can create your own deployment by
following the :ref:`setup-guides`.

Give Feedback
-------------

Pangeo is a work in progress. We need engagement from scientists like you
to realize the goals of the project. Currently, the best way to provide your
feedback and interact with the Pangeo community is via the
`Pangeo GitHub issue tracker`_. We use this a forum to discuss all details
of the project. Please drop in and share what you are working on, including
any challenges your have encountered along the way.

Contribute a Use Case
---------------------

If you are using Pangeo for your research, we would love to include an example
in the :ref:`Use Case Gallery <use-cases>`.
Please raise an issue on the `Pangeo GitHub issue tracker`_ to propose your
use case.

Contribute Data
---------------

Datasets are central to Pangeo. Our goal is to bring the computing to the data,
rather than the other way around.
If you have data you would like to make accessible to Pangeo, your best bet is
to place it on a large shared HPC cluster or in cloud storage. The data
page below provides a detailed description of how to interface pangeo with
the datasets of your choice.

.. toctree::
   :maxdepth: 2

   data

In the future, we hope to curate a data catalog to make it easier for users to
discover datasets on Pangeo platforms
(see `the discussion on github <https://github.com/pangeo-data/pangeo/issues/39>`_
for more detail.)

Become an Open Source Contributor
---------------------------------

The success of the Pangeo project depends on the sustainable development of
the underlying :ref:`packages`. A great way to contribute to Pangeo is to
contribute to those packages. Some ways to do this include:

- helping to improve the documentation of these packages
- raising issues on the package github repositories to report bugs or identify
  missing features
- fixing bugs or implementing new features yourself



.. _Scipy Lectures: https://www.scipy-lectures.org/
.. _Pangeo GitHub issue tracker: https://github.com/pangeo-data/pangeo/issues
.. _Jupyter Notebooks: https://jupyter-notebook.readthedocs.io/en/stable/notebook.html
