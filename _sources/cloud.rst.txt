.. _cloud:

Pangeo Cloud
============

Pangeo Cloud is an experimental service providing cloud-based data-science
environments.

.. warning::
    We currently have no long-term funding to support Pangeo Cloud.
    At present, we've cobbled together funding from various grants from funding
    agencies and cloud providers.
    All users must understand that Pangeo Cloud environments could disappear
    at any time.

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


Clusters
--------

Pangeo Cloud currently comprises two different computing clusters:

- `us-central1-b.gcp.pangeo.io <https://us-central1-b.gcp.pangeo.io/>`_: A cluster in
  Google Cloud Platform.
- `aws-uswest2.pangeo.io <https://aws-uswest2.pangeo.io>`_: A cluster in AWS.

We recommend choosing a cluster based on which data you want to access.
E.g. if your data live primarily in AWS, choose ``aws-uswest2``.

Once your application is approved, you will be able to log in to the resources
you requested.


Software Environment
--------------------

Each cluster contains a customized data-science software environment.
The environments are built by `repo2docker <https://github.com/jupyter/repo2docker>`_
and configured at the following locations:

- ``us-central1-b.gcp.pangeo.io``: `binder config <https://github.com/pangeo-data/pangeo-cloud-federation/tree/staging/deployments/gcp-uscentral1b/image/binder>`_
- ``uswest2.pangeo.io``: `binder config <https://github.com/pangeo-data/pangeo-cloud-federation/tree/staging/deployments/icesat2/image/binder>`_

Users can propose changes to the environment via issues and pull-requests to
this repository.

Users may use ``pip`` and ``conda`` to install new packages in their own
environments, but this approach currently has some limitations note below.
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

- Changes in the environment are not propagated to Dask workers.
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

Your Home Directory
-------------------

The cloud environment differs from what many UNIX users are used to.
Your are not on a shared server; you are on your own private server.
Your username is ``jovyan``, and your home directory is ``/home/jovyan``.
This is the same for all users.

**You have a 10 GB limit on the size of your home directory.**
Your home directory is intended only for notebooks, analysis scripts,
and small datasets.
It is not an appropriate place to store large datasets.
No one else can see or access the files your home directory.

The easiest way to move files in and out of your home directory is via the JupyterLab web interface.
Drag a file into the file browser to upload, and right-click to download back out.
You can also open a terminal via the JupyterLab launcher and use this to ssh / scp / ftp to remote systems.
However, you can’t ssh in!

The recommended way to move code in and out is via git.
You should clone your project repo from the terminal and use git pull / git push to update and push changes.

SSH Keys
--------

If you have two-factor authentication enabled on your GitHub account,
you will probably want to place an SSH key in your home directory to facilitate easy pushes.
(Read  `Connecting to GitHub with SSH <https://help.github.com/en/articles/connecting-to-github-with-ssh>`_
for more info.)
We recommend creating a new key just for this purpose and using a password.
You then add this key to your github profile at https://github.com/settings/keys.

To get the key to work on the cluster, place it in the /home/jovyan/.ssh/ directory. Then run::

    $ ssh-agent bash
    $ ssh-add ~/.ssh/<name_of_rsa_key>


Cloud Object Storage
--------------------

The preferred way to store data in the cloud is using cloud object storage, such as Amazon S3 or Google Cloud Storage.
Cloud object storage is essentially a key/value storage system.
They keys are strings, and the values are bytes of data.
Data is read and written using HTTP calls.
The performance of object storage is very different from file storage.
On one hand, each individual read / write to object storage has a high overhead (10-100 ms), since it has to go over the network.
On the other hand, object storage “scales out” nearly infinitely, meaning that we can make hundreds, thousands, or millions of concurrent reads / writes.
This makes object storage well suited for distributed data analytics.
However, the software architecture of a data analysis system must be adapted to take advantage of these properties.
All large datasets (> 1 GB) in Pangeo Cloud should be stored in Cloud Object Storage.

Reading Data
^^^^^^^^^^^^

Many pre-existing datasets are browseable at `catalog.pangeo.io <http://catalog.pangeo.io/>`_.
This catalog is pre-configured to make it easy to open the datasets.
In most cases, it's as simple as::

   from intake import open_catalog
   cat = open_catalog("https://raw.githubusercontent.com/pangeo-data/pangeo-datastore/master/intake-catalogs/atmosphere.yaml")
   ds  = cat["gmet_v1"].to_dask()

To open datasets that are not part of an intake catalog, we recommend using
the `filesystem-spec <https://filesystem-spec.readthedocs.io/en/latest/>`_ package
and its related packages `gcsfs <https://gcsfs.readthedocs.io/en/latest/>`_
(for Google Cloud Storage)
and `s3fs <https://s3fs.readthedocs.io/en/latest/>`_
(for Amazon S3 and all S3-compatible object stores).

For example, to open a public file from Google Cloud Storage, you would do::

   import pandas as pd
   import fsspec
   path = 'gs://cmip6/cmip6-zarr-consolidated-stores.csv'
   with fsspec.open(path) as f:
       df = pd.read_csv(f)

Zarr stores can be opened using ``.get_mapper`` methods from fsspec, gscsfs, and s3fs.
For examples, see

- `Zarr Docs on Distributed Cloud Storage <https://zarr.readthedocs.io/en/stable/tutorial.html?highlight=s3fs#distributed-cloud-storage>`_
- `Xarray Docs on Cloud Storage <http://xarray.pydata.org/en/stable/io.html#cloud-storage-buckets>`_


Writing Data
^^^^^^^^^^^^

Writing data (and reading private data) requires credentials for authentication.
Pangeo Cloud does not provide credentials to individual users.
Instead you must sign up for your own account with the cloud provider and manage your own storage.
(Most cloud providers offer several hundred dollars worth of free credits for new accounts.)

On S3-type storage, you will have a client key and client secret associated with you account.
The following code creates a writeable filesystem::

   fs = s3fs.S3FileSystem(key='<YOUR_CLIENT_KEY>', secret='<YOUR_CLIENT_SECRET')

Non-AWS S3 services (e.g. Wasabi Cloud) can be configured by passing an argument
such as ``client_kwargs={'endpoint_url': 'https://s3.us-east-2.wasabisys.com'}``
to ``S3FileSystem``.

For Google Cloud Storage, the best practice is to create a
`service account <https://cloud.google.com/iam/docs/service-accounts>`_ with
appropriate permissions to read / write your private bucket.
You upload your service account key (a .json file) to your Pangeo Cloud
home directory and then use it as follows::

   import json
   import gcsfs
   with open('<your_token_file>.json') as token_file:
       token = json.load(token_file)
   gcs = gcsfs.GCSFileSystem(token=token)

You can then read / write private files with the ``gcs`` object.

Scratch Bucket
^^^^^^^^^^^^^^

Pangeo Cloud environments are configured with a "scratch bucket," which
allows you to temporarily store data. Credentials to write to the scratch
bucket are pre-loaded into your Pangeo Cloud environment.

.. warning::
    Any data in scratch buckets will be deleted once it is 7 days old.
    Do not use scratch buckets to store data permanently.

The location of your scratch bucket is contained in the environment variable ``PANGEO_SCRATCH``.
To create mutable mapping that can write to your scratch bucket with zarr,
the following code should work::

   import os
   PANGEO_SCRATCH = os.environ['PANGEO_SCRATCH']
   # -> gs://pangeo-scratch/<username>
   import fsspec
   mapper = fsspec.get_mapper(f'PANGEO_SCRATCH/sub/path')
   # mapper can now be to read / write zarr stores

.. warning::
    A common set of credentials is currently used for accessing scratch buckets.
    This means users can read, and potentially remove / overwrite, each others'
    data. You can avoid this problem by always using ``PANGEO_SCRATCH`` as a prefix.
    Still, you should not store any sensitive or mission-critical data in
    the scratch bucket.


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

Dask Gateway
^^^^^^^^^^^^

Pangeo cloud environments are configured to work with
`Dask Gateway <https://gateway.dask.org/>`_.
Dask gateway gives you the power to create a distributed cluster using many
cloud compute nodes. *Please use this power carefully!*

.. warning::
    Avoid large, long-running, idle clusters, which are a waste of Pangeo's limited cloud computing budget.
    Only use a cluster while you need

To create a cluster first connect to the gateway, create the cluster, and then connect to it::

    from dask.distributed import Client
    from dask_gateway import Gateway
    gateway = Gateway()  # connect to Gateway
    cluster = gateway.new_cluster()  # create cluster
    cluster.adapt(minimum=2, maximum=10) # adaptive mode
    client = Client(cluster)  # connect Client to Cluster
    # Dask computations are now automatically routed through the cluster
    # When you're done computing:
    client.close()
    cluster.close()

You can specify custom options for your cluster as follows::

    import dask_gateway
    gateway = dask_gateway.Gateway()
    options = gateway.cluster_options()
    options.worker_memory = 10 # each worker will have 10 GB of memory
    cluster = gateway.new_cluster(options)
