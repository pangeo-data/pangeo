.. _setup-guides:

Deployment Setup Guides
=======================

The Pangeo software stack is an collection of :ref:`packages` that when used
together facilitate scalable data analysis on a wide range of computing platforms
(see :ref:`deployments` for a list of examples where Pangeo concepts have been
deployed).

This is a growing collection of information that will help you setup your own
Pangeo deployment, whether it be on an `HPC`_ system or on a public `cloud`_.

If you have tips or deployments that you would like to share, or if you see
anything that is incorrect, or have any questions, feel free to reach out at
the `issues page`_.

We have broken our setup guides into two distinct tracks, one for `HPC`_ systems,
and another for `cloud`_ systems:

Setting up Pangeo on HPC Systems
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This tutorial assumes you have access to a HPC system and that you have some
basic Unix skills. We'll walk you through some common steps for getting Pangeo
running on a typical HPC system.

.. toctree::
   :maxdepth: 2

   hpc


Setting up Pangeo on Cloud Systems
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These tutorials describe how to deploy Pangeo using `Kubernetes`_. Most users
will also find the `zero-to-jupyterhub`_ documentation quite useful.

.. toctree::
  :maxdepth: 2

  cloud


.. _HPC: hpc.rst
.. _cloud: cloud.rst
.. _issues page: https://github.com/pangeo-data/pangeo/issues
.. _zero-to-jupyterhub: http://zero-to-jupyterhub.readthedocs.io
.. _Kubernetes: https://kubernetes.io/
