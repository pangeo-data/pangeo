.. _cloud:

Deploying Pangeo on the Cloud
=============================

The commercial cloud is a powerful environment in which to deploy a pangeo environment.
However, cloud computing is unfamiliar to most geoscientists.
The point of this guide is to describe how to setup up your own pangeo cluster
on the cloud platform of your choice, assuming zero knowledge of how the cloud works.
We do assume you are comfortable using the unix command line and have access
to one on your personal computer.

.. Note::

  This guide, and the Pangeo cloud configuration in general, is based heavily
  on the `Zero to Jupyterhub`_ guide. We strongly recommend that your read
  that guide closely if you want a more comprehensive understanding.

This guide currently covers only deployment on `Google Cloud Platform`_.
We hope to soon expand it to include AWS and Azure.


Step One: Install the Necessary Software
----------------------------------------

Google Cloud SDK
~~~~~~~~~~~~~~~~

The Google Cloud SDK is the command-line interface for Google Cloud Platform
products and services. Download and installation instructions are at
https://cloud.google.com/sdk/downloads

Kubernetes Kubectl
~~~~~~~~~~~~~~~~~~

Kubernetes_ is an open source system for managing containerized applications in
the cloud. The Kubernetes command-line tool, ``kubectl``, allows you to deploy
and manage applications on Kubernetes. It is necessary to deploy a Pangeo
cluster.

If you have already installed the Google Cloud SDK, the easiest way to install
kubectl is to run the following command on the command line::

  $ gcloud components install kubectl

More comprehensive documentation for installing Kubernetes can be found at
https://kubernetes.io/docs/tasks/tools/install-kubectl/

Helm Client
~~~~~~~~~~~

Helm_ is a package manager for Kubernetes. Helm helps you automatically download
and deploy the Pangeo default configuration for your cluster.

To install the helm command line client, follow the installation instructions at
https://docs.helm.sh/install/

To do this in one line from the command line, run::

  $ curl https://raw.githubusercontent.com/kubernetes/helm/master/scripts/get | bash


Step Two: Create a Cluster
--------------------------

First, you must create an account on the cloud provider of your choice.
Here we are using `Google Cloud Platform`_.

Here is a bash script that will create a cluster:

.. code-block:: bash

  #!/bin/bash

  set -e

  EMAIL='ryan.abernathey@gmail.com'
  PROJECTID='pangeo-181919'
  ZONE='us-central1-b'

  NUM_NODES=2
  MIN_WORKER_NODES=0
  MAX_WORKER_NODES=100
  CLUSTER_NAME='pangeo-beast'
  # https://cloud.google.com/compute/pricing
  WORKER_MACHINE_TYPE='n1-highmem-16'

  # create cluster on GCP
  gcloud config set project $PROJECTID
  gcloud container clusters create $CLUSTER_NAME --num-nodes=$NUM_NODES --zone=$ZONE \
      --machine-type=n1-standard-2 --no-enable-legacy-authorization
  gcloud container node-pools create worker-pool --zone=$ZONE --cluster=$CLUSTER_NAME \
      --machine-type=$WORKER_MACHINE_TYPE --preemptible --enable-autoscaling \
      --num-nodes=$MIN_WORKER_NODES --max-nodes=$MAX_WORKER_NODES --min-nodes=$MIN_WORKER_NODES
  gcloud container clusters get-credentials $CLUSTER_NAME --zone=$ZONE --project $PROJECTID

.. _Zero to Jupyterhub: https://zero-to-jupyterhub-with-kubernetes.readthedocs.io/en/latest/
.. _Google Cloud Platform: https://cloud.google.com/
.. _Kubernetes: https://kubernetes.io/docs/home/
.. _Helm: https://docs.helm.sh/
