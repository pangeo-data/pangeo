.. _cloud:

Deploying Pangeo on the Cloud
=============================

The commercial cloud is a powerful environment in which to deploy a Pangeo environment.
However, cloud computing is unfamiliar to most researchers.
The point of this guide is to describe how to setup up your own Pangeo cluster
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

.. _google-cloud-sdk:

Google Cloud SDK
~~~~~~~~~~~~~~~~

The Google Cloud SDK is the command-line interface for Google Cloud Platform
products and services. Download and installation instructions are at
https://cloud.google.com/sdk/downloads.

Kubernetes kubectl
~~~~~~~~~~~~~~~~~~

Kubernetes_ is an open source system for managing containerized applications in
the cloud. The Kubernetes command-line tool, ``kubectl``, allows you to deploy
and manage applications on Kubernetes. It is necessary to deploy a Pangeo
cluster.

If you have already installed the Google Cloud SDK, the easiest way to install
kubectl is to run the following command on the command line::

gcloud components install kubectl

More comprehensive documentation for installing Kubernetes can be found at
https://kubernetes.io/docs/tasks/tools/install-kubectl/.

Helm Client
~~~~~~~~~~~

Helm_ is a package manager for Kubernetes. Helm helps you automatically download
and deploy the Pangeo default configuration for your cluster.

To install the helm command line client, follow the installation instructions at
https://docs.helm.sh/install/.

To do this in one line from the command line, run::

  curl https://raw.githubusercontent.com/kubernetes/helm/master/scripts/get | bash

Pangeo scripts template
~~~~~~~~~~~~~~~~~~~~~~~

Following chapters describe some batch scripts that are available in the pangeo
repo. Clone the repo using git and go to the appropriate folder to use
them

.. code-block:: bash

  git clone https://github.com/pangeo-data/pangeo.git
  cd pangeo/gce/setup-guide

You can then edit your configuration parameters in
``gce-pangeo-environment.sh`` file and then export them

.. code-block:: bash

  source gce-pangeo-environment.sh

Step Two: Create a Kubernetes Cluster
-------------------------------------

First, you must create an account on the cloud provider of your choice.
Here we are using `Google Cloud Platform`_.

All Google Cloud services are provisioned within the context of a
`project <https://cloud.google.com/resource-manager/docs/creating-managing-projects>`_.
If you haven't done so already, you should create a project and switch to it
in the Google Cloud console.
From the *APIs and Services* section of the cloud console, you must then
enable the Kubernetes Engine API for the project.

To create the cluster from the command line, you must first be authenticated.
Run the following from the commmand line:

.. code-block:: bash

  gcloud auth login

Following this step, you will need to run a set of bash commands to
create a cluster with the components that Pangeo requires:

  - An incompressible default node pool for the Jupyterhub, web proxy, and user
    notebook servers.
  - An auto scaling node pool for Dask workers.

This script is availabe in pangeo/gce/setup-guide as `1_create_cluster.sh`_, so
you can use it directly.

.. Note::
  If you expect your notebook images to be fairly large, it may be adventageous
  to setup your cluster to use faster SSD boot disks. This will typically provide
  faster boot times for notebooks and Dask workers. To do this, you'll want
  to setup your cluster and any node pools with the ``--disk-type pd-ssd`` option.
  More information on how to configure SSD boot disks can be found in the `GCP
  documentation <https://cloud.google.com/kubernetes-engine/docs/how-to/custom-boot-disks>`_.

Step Three: Configure Kubernetes
--------------------------------

This script sets up the Kubernetes `Role Based Access Control
<https://kubernetes.io/docs/reference/access-authn-authz/rbac/>`_
necessary for a secure cluster deployment.

This script is available in pangeo/gce/setup-guide as `2_configure_kubernetes.sh`_.

Step Four: Create Cluster-Specific Configuration
------------------------------------------------

There are two configuration files needed to deploy the Pangeo helm chart. Those
files are available in the pangeo/gce/setup-guide folder of this repo. The
first, `jupyter_config.yaml`_, specifies modifications to the configuration
that are unique to each deployment, so you will need to edit it.

The most important thing to configure here is the  ``loadBalancerIP``.
If you have not `reserved a static external IP
<https://cloud.google.com/compute/docs/ip-addresses/reserve-static-external-ip-address>`_,
you can do so by running::

  gcloud compute addresses create pangeo-jhubip --region $REGION
  gcloud compute addresses list | grep pangeo-jhubip

Other things you might want to configure, but that can be left as is:

  - EXTRA_PIP_PACKAGES: for adding some python modules to your user environment.
  - GCSFUSE_BUCKET: for mounting some google cloud storage bucket as a standard
    file system.

The other file is `secret_config.yaml`_, which specifies cluster specific
encryption tokens.

The jupyterhub proxy secret token is a random hash, which you can generate as follows:

.. code-block:: bash

  openssl rand -hex 32

Replace `<SECRET>` in the `secretToken` section with the output of this (note:
you will stilll need the quotes around this value)


Most pangeo deployments use `GitHub OAuth Callback`_, (or `GitHub OAuth for developers`_)
to authenticate users.

This authentication method needs an IP or domain name to work. This should be
the IP you've reserved above, if you don't have a domain name yet. Insert
this IP in the following block::

  proxy:
      service:
        loadBalancerIP: <GCE_EXTERNAL_IP>

Instead of `GCE_EXTERNAL_IP`.

Replace `clientId`, `clientSecret` and `callbackUrl` values in the
`secret_config.yaml` file with the values obtained from the GitHub app that you
create for this.

Alternatively, you can also change authentication method, see the
`Zero to Jupyterhub`_ guide for more information on that.

Step Five: Deploy Helm Chart
----------------------------

The following script deploys the most recent Pangeo Helm chart to your
Kubernetes cluster.

If you want to use a specific version, check `Pangeo Helm Chart
<https://pangeo-data.github.io/helm-chart/>`_ for the version you want. You can
then add a ``--version=0.1.1-a14d55b`` argument (for example) to ``helm
install`` command, only keeping the last part of the release, without
the ``pangeo-v`` prefix from the helm chart web-page.

This script is available as `3_deploy_helm.sh`_ in the repo.

If you have not specified a static IP address in your configuration, the
jupyterhub will come up at a random IP address. To get the address, run the
command

.. code-block:: bash

   kubectl --namespace=pangeo get svc proxy-public

Here's what we see for pangeo.pydata.org when we run this commmand::

  NAME           TYPE           CLUSTER-IP      EXTERNAL-IP    PORT(S)        AGE
  proxy-public   LoadBalancer   10.23.255.193   35.224.8.169   80:30442/TCP   18d

The ``EXTERNAL-IP`` value is the address of the hub.

Upgrade Cluster
---------------

If you want to change the configuration, or to upgrade the cluster to a new
version of the Helm Chart, run the following commmand (if you are just updating
jupyterhub authentication IP, ``--force`` and ``--recreate-pods`` are not
needed).

The scripts `4_upgrade_helm.sh`_ and `5_upgrade_helm_soft.sh`_ are available
for that.

Pangeo Helm Chart and Docker Images
-----------------------------------

Pangeo maintains its own Helm_ Chart and Docker_ images. These hold the
default configuration for a Pangeo cloud deployment. These items live in
the Pangeo helm-chart repository:

- https://github.com/pangeo-data/helm-chart

.. _jupyter_config.yaml: https://github.com/pangeo-data/pangeo/blob/master/gce/setup-guide/jupyter_config.yaml
.. _secret_config.yaml: https://github.com/pangeo-data/pangeo/blob/master/gce/setup-guide/secret_config.yaml
.. _Github OAuth for developers: https://developer.github.com/apps/building-oauth-apps/creating-an-oauth-app/
.. _GitHub OAuth Callback: https://help.github.com/enterprise/2.13/admin/guides/user-management/using-github-oauth/
.. _Zero to Jupyterhub: https://zero-to-jupyterhub-with-kubernetes.readthedocs.io/en/latest/
.. _Google Cloud Platform: https://cloud.google.com/
.. _Kubernetes: https://kubernetes.io/docs/home/
.. _Helm: https://docs.helm.sh/
.. _Docker: https://docker.com/
.. _1_create_cluster.sh: https://github.com/pangeo-data/pangeo/blob/master/gce/setup-guide/1_create_cluster.sh
.. _2_configure_kubernetes.sh: https://github.com/pangeo-data/pangeo/blob/master/gce/setup-guide/2_configure_kubernetes.sh
.. _3_deploy_helm.sh: https://github.com/pangeo-data/pangeo/blob/master/gce/setup-guide/3_deploy_helm.sh
.. _4_upgrade_helm.sh: https://github.com/pangeo-data/pangeo/blob/master/gce/setup-guide/4_upgrade_helm.sh
.. _5_upgrade_helm_soft.sh: https://github.com/pangeo-data/pangeo/blob/master/gce/setup-guide/5_upgrade_helm_soft.sh
