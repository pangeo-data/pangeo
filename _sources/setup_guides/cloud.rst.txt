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

  $ gcloud components install kubectl

More comprehensive documentation for installing Kubernetes can be found at
https://kubernetes.io/docs/tasks/tools/install-kubectl/.

Helm Client
~~~~~~~~~~~

Helm_ is a package manager for Kubernetes. Helm helps you automatically download
and deploy the Pangeo default configuration for your cluster.

To install the helm command line client, follow the installation instructions at
https://docs.helm.sh/install/.

To do this in one line from the command line, run::

  $ curl https://raw.githubusercontent.com/kubernetes/helm/master/scripts/get | bash

Pangeo scripts template
~~~~~~~~~~~~~~~~~~~~~~~

Following chapters describe some batch scripts that are available in the pangeo
repo. Just clone the repo using git and go to the appropriate folder to use
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
Run the following from the commmand line

.. code-block:: bash

  gcloud auth login

Now here is a bash script that will create a cluster corresponding to Pangeo
need:
- An incompressible default node pool for the Jupyterhub, web proxy, and user notebook servers.
- An auto scaling node pool for Dask workers.

This script is availabe in pangeo/gce/setup-guide as ``1_create_cluster.sh``,
so you can use it directly.

.. code-block:: bash

  #!/bin/bash

  set -e

  PROJECTID=<YOUR GOOGLE CLOUD PROJECT ID>
  # this is the zone used by pangeo.pydata.org
  ZONE='us-central1-b'

  # cluster size settings: modify as needed to fit your needs / budget
  NUM_NODES=2
  MIN_WORKER_NODES=0
  MAX_WORKER_NODES=100
  CLUSTER_NAME='pangeo'

  # https://cloud.google.com/compute/pricing
  # change the machine typer based on your computing needs
  WORKER_MACHINE_TYPE='n1-standard-4'

  # create cluster on GCP
  gcloud config set container/new_scopes_behavior true
  gcloud config set project $PROJECTID
  gcloud container clusters create $CLUSTER_NAME --num-nodes=$NUM_NODES --zone=$ZONE \
      --machine-type=n1-standard-2 --no-enable-legacy-authorization
  gcloud container node-pools create worker-pool --zone=$ZONE --cluster=$CLUSTER_NAME \
      --machine-type=$WORKER_MACHINE_TYPE --preemptible --enable-autoscaling \
      --num-nodes=$MIN_WORKER_NODES --max-nodes=$MAX_WORKER_NODES --min-nodes=$MIN_WORKER_NODES
  gcloud container clusters get-credentials $CLUSTER_NAME --zone=$ZONE --project $PROJECTID

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

This script is available in pangeo/gce/setup-guide as
``2_configure_kubernetes.sh``.

.. code-block:: bash

  #!/bin/bash

  set -e

  EMAIL=<THE EMAIL ADDRESS ASSOCIATED WITH YOUR GOOGLE CLOUD ACCOUNT>

  kubectl create clusterrolebinding cluster-admin-binding --clusterrole=cluster-admin --user=$EMAIL
  kubectl create serviceaccount tiller --namespace=kube-system
  kubectl create clusterrolebinding tiller --clusterrole=cluster-admin --serviceaccount=kube-system:tiller
  helm init --service-account tiller
  kubectl --namespace=kube-system patch deployment tiller-deploy --type=json \
        --patch='[{"op": "add", "path": "/spec/template/spec/containers/0/command", "value": ["/tiller", "--listen=localhost:44134"]}]'


Step Four: Create Cluster-Specific Configuration
------------------------------------------------

There are two configuration files needed to deploy the Pangeo helm chart.
Those files are available in the pangeo/gce/setup-guide folder of this repo.
The first, ``jupyter_config.yaml``, specifies modifications to the
configuration that are unique to each deployment.

Most important thing to configure here is the  ``loadBalancerIP``. If you've
not `reserved a static external IP
<https://cloud.google.com/compute/docs/ip-addresses/reserve-static-external-ip-address>`_,
you can do so by running::

  gcloud compute addresses create pangeo-jhubip --region $REGION
  gcloud compute addresses list | grep pangeo-jhubip

Other things you might want to configure, but that can be left as is:

- EXTRA_PIP_PACKAGES: for adding some python modules to your user environment.
  file system.
- GCSFUSE_BUCKET: for mounting some google cloud storage bucket as a standard file system.

.. code-block:: yaml

  # file: jupyter_config.yaml

  jupyterhub:
    singleuser:
      cmd: ['start-singleuser.sh']
      extraEnv:
        EXTRA_PIP_PACKAGES: >-
        GCSFUSE_BUCKET: pangeo-data
      storage:
        extraVolumes:
          - name: fuse
            hostPath:
              path: /dev/fuse
        extraVolumeMounts:
          - name: fuse
            mountPath: /dev/fuse
      cloudMetadata:
        enabled: true
      cpu:
        limit: 4
        guarantee: 1
      memory:
        limit: 14G
        guarantee: 4G

    hub:
      extraConfig:
        customPodHook: |
          from kubernetes import client
          def modify_pod_hook(spawner, pod):
              pod.spec.containers[0].security_context = client.V1SecurityContext(
                  privileged=True,
                  capabilities=client.V1Capabilities(
                      add=['SYS_ADMIN']
                  )
              )
              return pod
          c.KubeSpawner.modify_pod_hook = modify_pod_hook
          c.JupyterHub.logo_file = '/usr/local/share/jupyter/hub/static/custom/images/logo.png'
          c.JupyterHub.template_paths = ['/usr/local/share/jupyter/hub/custom_templates/',
                                        '/usr/local/share/jupyter/hub/templates/']
      image:
        name: jupyterhub/k8s-hub
        tag: v0.6
      extraVolumes:
        - name: custom-templates
          gitRepo:
            repository: "https://github.com/pangeo-data/pangeo-custom-jupyterhub-templates.git"
            revision: "b09721bb1a1248dc115730d3c8a791600eae257e"
      extraVolumeMounts:
        - mountPath: /usr/local/share/jupyter/hub/custom_templates
          name: custom-templates
          subPath: "pangeo-custom-jupyterhub-templates/templates"
        - mountPath: /usr/local/share/jupyter/hub/static/custom
          name: custom-templates
          subPath: "pangeo-custom-jupyterhub-templates/assets"

    cull:
      enabled: true
      users: false
      timeout: 1200
      every: 600

    # this section specifies the IP address for pangeo.pydata.org
    # remove or change for a custom cluster
    proxy:
      service:
        loadBalancerIP: 35.224.8.169

The other file is ``secret_config.yaml``, which specifies cluster specific
encryption tokens. The jupyterhub proxy secret token is just a random hash,
which you can generate as follows.

.. code-block:: bash

  $ openssl rand -hex 32

Pangeo.pydata.org uses `GitHub OAuth Callback
<https://help.github.com/enterprise/2.13/admin/guides/user-management/using-github-oauth/>`_,
(or `GitHub OAuth for developer <https://developer.github.com/apps/building-oauth-apps/creating-an-oauth-app/>`_)
to authenticate users. The ``clientSecret`` token needs to be obtained via
github.

This authentication method needs an IP or domain name to work, the IP you've
reserved above and put in jupyter_config.yaml if you don't have a domain name
yet (just put the IP in place of pangeo.pydata.org domain name).

Alternatively, you can also change authentication method, see
`Zero to Jupyterhub`_ guide for more information on that.

.. code-block:: yaml

  # file: secret_config.yaml

  jupyterhub:
    proxy:
      secretToken: <SECRET>

    # comment this out if not using github authentication
    auth:
      type: github
      github:
        clientId: "2cb5e09d5733ff2e6ae3"
        clientSecret: <SECRET>
        callbackUrl: "http://pangeo.pydata.org/hub/oauth_callback"
      admin:
        access: true
        users:
          - mrocklin
          - jhamman
          - rabernat
          - yuvipanda
          - choldgraf
          - jacobtomlinson


Step Five: Deploy Helm Chart
----------------------------

The following script deploy the last Pangeo chart on your Kubernetes cluster.

If you want to use a specific version, check `Pangeo Helm Chart
<https://pangeo-data.github.io/helm-chart/>`_ for the version you want.
You can then add a ``--version=0.1.1-a14d55b`` argument to ``helm install``
command, only keeping the last part of the realease, without ``pangeo-v``.

This script is available as ``3_deploy_helm.sh`` in the repo.

.. code-block:: bash

  #!/bin/bash

  set -e

  helm repo add pangeo https://pangeo-data.github.io/helm-chart/
  helm repo update

  helm install pangeo/pangeo --namespace=pangeo --name=jupyter \
     -f secret_config.yaml -f jupyter_config.yaml

  # helm install pangeo/pangeo --namespace=pangeo --name=jupyter \
  #   --version=0.1.1-a14d55b \
  #   -f secret_config.yaml -f jupyter_config.yaml


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

Scripts ``4_upgrade_helm.sh`` and ``5_upgrade_helm_soft.sh`` are available for
that.

.. code-block:: bash

  $ helm upgrade --force --recreate-pods jupyter pangeo/pangeo \
     --version=$VERSION \
     -f secret_config.yaml -f jupyter_config.yaml


Pangeo Helm Chart and Docker Images
-----------------------------------

Pangeo maintains its own Helm_ Chart and Docker_ images. These hold the
default configuration for a Pangeo cloud deployment. These items live in
the Pangeo helm-chart repository:

- https://github.com/pangeo-data/helm-chart


.. _Zero to Jupyterhub: https://zero-to-jupyterhub-with-kubernetes.readthedocs.io/en/latest/
.. _Google Cloud Platform: https://cloud.google.com/
.. _Kubernetes: https://kubernetes.io/docs/home/
.. _Helm: https://docs.helm.sh/
.. _Docker: https://docker.com/
