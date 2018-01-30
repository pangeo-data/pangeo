Getting Started with Dask on Kubernetes
=======================================
This documents how to set up a cluster to run Dask on Kubernetes using GCP.

1. Install conda and creating an environments
1. Setup with Google Container Engine
1. Install dask-kubernetes
1. Create and launch your named cluster
1. Open the notebook, status page, and JupyterLab

Installing a software environment
---------------------------------

Download and install Miniconda:

    wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
    chmod +x Miniconda3-latest-Linux-x86_64.sh
    ./Miniconda3-latest-Linux-x86_64.sh

This contains a self-contained Python environment that we can manipulate
safely without requiring the involvement of IT. It also allows you to
create isolated software environments so that we can experiment in the
future safely.

Create a new conda environment for our pangeo dask-kubernetes work:


    conda env create -f environment.yml

Activate this environment

    source activate pangeo-dask-k8s

Your prompt should now look like this:

    (pangeo-dask-k8s) $

And if you ask where your Python command lives, it should direct you to
somewhere in your home directory:


    (pangeo-dask-k8s) # which python
    /Users/mmccarty/miniconda3/envs/pangeo-dask-k8s/bin/python

Setup with Google Container Engine
----------------------------------

You will need to install the following:

* <a href='https://cloud.google.com/sdk/gcloud/'>gcloud</a> for authentication and launching clusters
* <a href='https://kubernetes.io/docs/tasks/tools/install-kubectl/'>kubectl</a> for interacting with the kubernetes driver.

Register on the <a href='https://cloud.google.com/'>Google Cloud Platform</a>, setup a billing account and create a project with the Google Compute Engine API enabled.

Ensure that your client SDK is up to date:

    $ gcloud components update


Install dask-kubernetes
------------------------------------

    $ git clone git@github.com:pangeo-data/dask-kubernetes.git
    $ git checkout pangeo
    $ python setup.py install


Create and launch your named cluster
------------------------------------

    $ dask-kubernetes create NAME
    $ dask-kubernetes notebook NAME
    $ dask-kubernetes lab NAME
    $ dask-kubernetes state NAME

Removing your cluster
---------------------

When you are done, delete the cluster with the following:

    dask-kubernetes delete NAME

See <a href='https://github.com/pangeo-data/dask-kubernetes/tree/pangeo'>dask-kubernetes ReadMe</a> for more information.
