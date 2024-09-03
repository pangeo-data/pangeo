.. _cloud:

Pangeo Cloud
============

Pangeo Cloud is an experimental service providing cloud-based data-science environments.
Pangeo Cloud is currently supported by the NSF EarthCube program `award 2026932 <https://www.nsf.gov/awardsearch/showAward?AWD_ID=2026932>`_,
which also supports `Pangeo Forge <https://pangeo-forge.readthedocs.io/>`_.
Funding is in place through the end of 2023. After that, we can make no firm committments about the longevity of the platform.

Operated by 2i2c
----------------

Pangeo Cloud is operated by `2i2c <https://2i2c.org>`_.
You can see the deployment configuration here: https://github.com/2i2c-org/infrastructure/tree/master/config/clusters/pangeo-hubs

Quickstart
----------

.. raw:: html

    <embed>
      <a href="https://us-central1-b.gcp.pangeo.io" class="btn btn-primary btn-lg btn-block" >Google Cloud Deployment</a>
    </embed>

Getting Support
----------------

We would like for Pangeo Cloud to one day be a full-featured, professional
service. **But it's not yet!**
It is an experiment, run by scientists and hackers who devote
their nights and weekends to this project.
Professional level support (a service-level agreement, a 24-hour helpdesk) is non-existent.

With those caveats, support requests for Pangeo Cloud can be made on our Discourse forum

- https://discourse.pangeo.io/c/Cloud/Tech-support-forum-for-Pangeo-Cloud/17

We use this forum to track technical support requests for Pangeo Cloud.
Someone will do their best to respond to you as quickly as possible given the circumstances.
This is not a place for general support requests about scientific python.
This forum is specific to issues related to Pangeo Cloud such as:

- login problems
- environment configuration
- reading / writing cloud data
- Dask Gateway on Pangeo Cloud

In making a support request, please provide the following information:

- Which cluster are you using (e.g. ``us-central1-b.gcp.pangeo.io``)
- A concise summary of your problem
- If your problem involves code, please do your best to include a
  `minimum reproducible example <https://matthewrocklin.com/blog/work/2018/02/28/minimal-bug-reports>`_


Sign Up
-------

Pangeo Cloud is available to researchers across the world engaged in
data-intensive Earth and Environmental Science.
Prospective users must apply using the following form:

- `Pangeo Cloud Application`_

Access will be granted based on a review of the proposed research project
and its technical suitability for Pangeo Cloud.

.. _Pangeo Cloud Application: https://forms.gle/J3hVVBgobwpYVWHF8

If your application is approved, you will receive an invitation to join
a GitHub Team in the ``pangeo-data`` organization.
You must accept this invitation to gain access to Pangeo Cloud resources.


Hubs
----

Currently active Pangeo JupyterHubs depend on grant funding:

- `us-central1-b.gcp.pangeo.io <https://us-central1-b.gcp.pangeo.io/>`_: A hub in
  Google Cloud Platform.

We recommend choosing a hub based on what data you want to access. See for example
`Google Cloud Datasets <https://cloud.google.com/datasets>`_.)

Once your application is approved, you will be able to log in to the resources
you requested.


.. _cloud.software_environment:

Software Environment
--------------------

JupyterHubs contains a customized data-science software environment based
off the docker images built in https://github.com/pangeo-data/pangeo-docker-images.
These are the steps for adding a package to the environment:

1. Make a pull request to https://github.com/pangeo-data/pangeo-docker-images
   updating the `environment.yml` file for the `pangeo-notebook` docker image
   at https://github.com/pangeo-data/pangeo-docker-images/blob/master/pangeo-notebook/environment.yml.
2. When that pull request is merged, the Pangeo maintainers will push a tag
   with today's date, triggering a release of new docker images.
3. A bot will submit a pull request to `pangeo-cloud-federation` updating the
   images (https://github.com/pangeo-data/pangeo-cloud-federation/pull/733).
   When this is merged, you can test your changes in the staging environment
   (at either https://staging.us-central1-b.gcp.pangeo.io or https://staging.aws-uswest2.pangeo.io)
4. If things look good, the Pangeo maintainers can trigger a deploy to production,
   making the package avaiable to everyone.

Users may use ``pip`` and ``conda`` to install new packages in their own
environments, but this approach currently has some limitations noted below.
To install into your personal environment, it's crucial that you include the
``--user`` flag to pip. This installs the package in ``~/.local/lib/PYTHON/site-packages/``.
Since it's in your home directory, it will persist across jupyterlab sessions.

.. code-block: console

   # Running on a Pangeo Jupyterhub
   (notebook) jovyan@jupyter-tomaugspurger:~$ pip install --user cf-xarray
   Collecting cf-xarray
     Downloading cf_xarray-0.2.0-py3-none-any.whl (20 kB)
     ...
   Installing collected packages: cf-xarray
   Successfully installed cf-xarray-0.2.0
   (notebook) jovyan@jupyter-tomaugspurger:~$ ls ~/.local/lib/python3.7/site-packages/
   cf_xarray  cf_xarray-0.2.0.dist-info

- Changes in the environment are not propagated to Dask ps (though see
  below for a way to include packages on the workers too).
- Installing additional packages with pip into an existing conda environment
  risks breaking the environment if doesn't see packages installed by conda and
  vice versa. You shouldn't install / update packages that are already in
  the environment.


Hardware Environment
--------------------

Pangeo Cloud clusters offer different amounts of RAM and CPU to the user
notebook upon login.
Please choose the least resource-intensive option for the work you need to do.
Larger virtual machines cost us more money.

Files and Data in the Cloud
---------------------------

Please see the 2i2c documentation on `Files and Data in the Cloud <https://docs.2i2c.org/en/latest/user/storage.html>`_.

Dask
----

`Dask <http://dask.pydata.org/>`_ is an important component of Pangeo Cloud and can be used to help parallelize large calculations.
All environments support the standard multi-threaded dask scheduler, and by default,
zarr-backed cloud data datasets will open in Xarray as collections of Dask arrays.

Guidelines for using Dask
^^^^^^^^^^^^^^^^^^^^^^^^^

- Familiarize yourself with `Dask best practices <https://docs.dask.org/en/latest/array-best-practices.html>`_.
- Don’t use Dask! Or more specifically, only use a distributed cluster if you really need it, i.e. if your calculations are running out of memory or are taking an unacceptably long time to complete.
- Start small; work on a small subset of your problem to debug before scaling up to a very large dataset.
- If you use a distributed cluster, use `adapative mode <https://jobqueue.dask.org/en/latest/index.html#adaptivity>`_ rather than a fixed size cluster; this will help share resources more effectively.
- Use the Dask dashboard heavily to monitor the activity of your cluster.

.. _dask_gateway:

Dask Gateway
^^^^^^^^^^^^

Pangeo cloud environments are configured to work with
`Dask Gateway <https://gateway.dask.org/>`_.
Dask gateway gives you the power to create a distributed cluster using many
cloud compute nodes. *Please use this power carefully!*

.. warning::
    Avoid large, long-running, idle clusters, which are a waste of Pangeo's limited cloud computing budget.
    Only use a cluster while you need

To do scalable computations with Dask you need to create a cluster with Dask Gateway
and connect to it

.. code-block:: python

   from dask_gateway import GatewayCluster

   cluster = GatewayCluster()
   cluster.adapt(minimum=2, maximum=10)  # or cluster.scale(n) to a fixed size.
   client = cluster.get_client()

That will create a Dask cluster with the default settings we've configured for
you. From that point, any computations using Dask will be done on the cluster.
The ``cluster`` and ``client`` reprs will have a link to your Dask Dashboard.

When you're done with your computation, you can close the cluster explicitly

.. code-block:: python

   cluster.close()

Or restart the notebook kernel, or stop your JupyterHub server. Finally, as
a safeguard, Pangeo will automatically close your Dask cluster if it's idle
for 60 minutes (but we prefer that you close it yourself if possible, to avoid
paying for unnecessary compute).

If you need to customize things, you'll need to connect to the Gateway.

.. code-block:: python

   from dask_gateway import Gateway
   gateway = Gateway()
   options = gateway.cluster_options()

   # set the options programatically, or through their HTML repr
   options.worker_memory = 10  # 10 GB of memory per worker.

   # Create a cluster with those options
   cluster = gateway.new_cluster(options)
   cluster.scale(...)
   client = cluster.get_client()

Dask Gateway can optionally keep clusters running past the lifetime of your notebook. You can set the cluster shutdown behavior using  the `shutdown_on_close <https://gateway.dask.org/api-client.html?highlight=shutdown_on_close#gatewaycluster/>`_ parameter. Note the default setting for the `shutdown_on_close` parameter is different for different API calls.

If you need to reconnect to an *already running* cluster, to continue a computation
or shut it down, use the `gateway` object.

.. code-block:: python

   >>> gateway = Gateway()
   >>> gateway.list_clusters()
   [ClusterReport<name=prod.c288c65c429049e788f41d8308823ca8, status=RUNNING>]

   # connect to the cluster
   cluster = g.connect(g.list_clusters()[0].name)
   # shut it down
   cluster.close()


Choosing Cluster Options
^^^^^^^^^^^^^^^^^^^^^^^^

Your workload might constrain the choice of how much memory your workers need.
For example, if some stage of your computation requires loading in 5 arrays of
3GB each, then you'd need *at least* 15GB of memory on your worker nodes.

That said, certain values for the cores / memory per worker will work better for
pangeo's Kubernetes cluster than others.

At the end of the day, pangeo is launching Dask worker *pods* on our Kubernetes cluster.
Each of these worker pods is scheduled on a Kubernetes *node*: a physical machine
with some CPU and memory capacity. Depending on your per-worker CPU and memory requests,
we maybe be able to pack more than one Dask worker *pod* on each *node*, leading
to better cluster utilization (and potentially more total workers for you).

At the moment, our nodes have 4 CPUs and 26124 Mi of memory. So you want to
avoid requesting something like 3CPUs or anywhere from ~13GB-26GB.
If you're performing a large computation and *if your workload allows for it*
make sure to request less than half of the physical machine's memory per worker
(in practice, make it less than 11GB of memory per worker, to allow for some
other kubernetes pods to be scheduled on the node too).

Environment variables on the cluster
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Some scalable computations running on the cluster depend on environment variables
set on remote processes. In general, environment variables set on your local
Jupyter session will not propagate to the Dask scheduler and workers.

To set environment variables on the scheduler and workers, you must use the
``environment`` option.

.. code-block:: python

   >>> from dask_gateway import Gateway
   >>> gateway = Gateway()
   >>> options = gateway.cluster_options()

As described in :ref:`dask_gateway` these options can be set programmatically
or through the HTML widget. For example, to set the environment variable
``MY_VARIABLE`` on our scheduler and workers:

.. code-block:: python

   >>> options.environment = {"MY_VARIABLE": "1"}

Which can be verified with:

.. code-block:: python

   >>> cluster = gateway.new_cluster(options)
   >>> cluster.scale(1)
   >>> client = cluster.get_client()

   >>> def check():
   ...     import os
   ...     return os.environ["MY_VARIABLE"]

   >>> client.run(check)
   {'tls://10.36.248.180:33361': '1'}

This can be combined with `Dask's configuration system <https://docs.dask.org/en/latest/configuration.html>`_
to the Dask scheduler and workers. For example,

.. code-block:: python

   >>> env = {
   ...     "DASK_DISTRIBUTED__SCHEDULER__WORK_STEALING": False,
   ...     "DASK_DISTRIBUTED__SCHEDULER__ALLOWED_FAILURES": 5,
   ... }
   >>> options.environment = env
   >>> cluster = gateway.new_cluster(options)
   
Dask Software Environment
^^^^^^^^^^^^^^^^^^^^^^^^^

The default image used on Dask Clusters (the scheduler and workers) matches
the image used for JupyterHub. It won't, however, have changes you've made
in your "local" environment in your home directory on the hub.

Long-term, the best way to add packages to the environemnt is by updating the
Docker images, as described in :ref:`cloud.software_environment`. But for quickly
prototyping something on the Dask cluster you can use a the 
`Dask PipInstall plugin <https://distributed.dask.org/en/stable/plugins.html#built-in-worker-plugins>`_.
`Dask WorkerPlugin <https://distributed.dask.org/en/latest/plugins.html#distributed.diagnostics.plugin.WorkerPlugin>`_.
To install packages in dask workers (the example below installs `bulwark <https://pypi.org/project/bulwark/>`_),
you'd create a cluster normally and add the plugin, specifying which packages to intall:

.. code-block:: python

   >>> from dask.distributed import PipInstall
   >>> from dask_gateway import GatewayCluster
   >>> cluster = GatewayCluster()  # create the cluster nomrally
   >>> client = cluster.get_client()
   >>> # Now create and register the plugin. We'll install 'bulwark'
   >>> plugin = PipInstall(packages=['bulwark'])
   >>> client.register_worker_plugin(plugin)

We can verify the package is now present::

.. code-block:: python

   >>> def check():
   ...     import bulwark
   ...     return bulwark.__version__
   >>> cluster.scale(2)
   >>> client.wait_for_workers(2)
   >>> client.run(check)
   {'tls://10.36.248.117:40785': '0.6.1', 'tls://10.37.142.70:43031': '0.6.1'}


A few caveats are in order:

1. You should register the plugin before scaling to ensure that your packages
   are installed on all the workers.
2. You should take care with dependencies. Pip doesn't always respect packages
   that have been installed with conda.
3. If you need to *upgrade existing* packages, take special care. You may need
   to ``client.restart()`` the cluster to ensure that the new packages are
   used.
4. This will slow down the startup time of your workers, especially if the
   package takes a while to install.
