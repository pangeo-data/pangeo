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

`Pangeo Gallery`_ showcases real-world science applications of the
Pangeo stack. The use cases are formatted as `Jupyter Notebooks`_, a
self-describing computational document including text, code, and figures.
A great way to get started is to find a use case that is similar to the
analysis you want to do and modify it to suit your needs.

A great way for novices to learn how to use Pangeo is to start from one of these
use cases and modify it for your needs.

Try Out a Pangeo
---------------------------

The best way to try out Pangeo is to explore one of the interactive
Binders in `Pangeo Gallery`_.
If you're interested in working in a cloud based environment, you can sign
up for :ref:`cloud`.
If none of these meets your needs, you can create your own deployment on HPC
or cloud by following the :ref:`setup-guides`.

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
in the :ref:`Pangeo Gallery`. It's easy to add a new gallery!
Feel free to raise an issue on the `Pangeo Discourse Forum`_ to propose your
use case.

Contribute Data
---------------

Datasets are central to Pangeo. Our goal is to bring the computing to the data,
rather than the other way around.
If you have data you would like to make accessible to Pangeo, your best bet is
to place it on a large shared HPC cluster or in cloud storage.
You can then add your dataset to `catalog.pangeo.io <https://catalog.pangeo.io`_.
via the GitHub repo `https://github.com/pangeo-data/pangeo-datastore <https://github.com/pangeo-data/pangeo-datastore>`_.

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
.. _Pangeo Gallery: http://gallery.pangeo.io/
.. _Pangeo Discourse Forum: https://discourse.pangeo.io/c/science/5
