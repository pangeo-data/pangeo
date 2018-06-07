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

All Google Cloud services are provisioned within the context of a
`project <https://cloud.google.com/resource-manager/docs/creating-managing-projects>`_.
If you haven't done so already, you should create a project and switch to it
in the Google Cloud console.
From the *APIs and Services* section of the cloud console, you must then
enable the Kubernetes Engine API for the project.

To create the cluster from the command line, you must first be authenticated.
Run the following from the commmand line

.. code-block:: bash

  gcloud config set container/new_scopes_behavior true
  gcloud auth login

Now here is a bash script that will create a cluster:

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
  gcloud config set project $PROJECTID
  gcloud container clusters create $CLUSTER_NAME --num-nodes=$NUM_NODES --zone=$ZONE \
      --machine-type=n1-standard-2 --no-enable-legacy-authorization
  gcloud container node-pools create worker-pool --zone=$ZONE --cluster=$CLUSTER_NAME \
      --machine-type=$WORKER_MACHINE_TYPE --preemptible --enable-autoscaling \
      --num-nodes=$MIN_WORKER_NODES --max-nodes=$MAX_WORKER_NODES --min-nodes=$MIN_WORKER_NODES
  gcloud container clusters get-credentials $CLUSTER_NAME --zone=$ZONE --project $PROJECTID


Step Three: Configure Kubernetes
--------------------------------

This script sets up the Kubernetes
`Role Based Access Control <https://kubernetes.io/docs/reference/access-authn-authz/rbac/>`_
necessary for a secure cluster deployment.

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
The first, ``jupyter_config.yaml``, specifies modifications to the configuration
that are unique to each deploymment.

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
encryption tokens. The jupyerhub proxy secret token is just a random hash, which you
can generate as follows.

.. code-block:: bash

  $ openssl rand -hex 32

Pangeo.pydata.org uses
`GitHub OAuth Callback <https://help.github.com/enterprise/2.13/admin/guides/user-management/using-github-oauth/>`_
to authenticate users. The ``clientSecret`` token needs to be obtained via
github.

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

Check the `Pangeo Helm Chart <https://pangeo-data.github.io/helm-chart/>`_ for
the latest helm chart version. Here the version we are using is ``0.1.1-a14d55b``.

.. code-block:: bash

  #!/bin/bash

  set -e

  VERSION=0.1.1-a14d55b

  helm repo add pangeo https://pangeo-data.github.io/helm-chart/
  helm repo update

  helm install pangeo/pangeo --version=$VERSION \
     --namespace=pangeo --name=jupyter  \
     -f secret-config.yaml \
     -f jupyter-config.yaml


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
version of the Helm Chart, run the following commmand

.. code-block:: bash

  $ helm upgrade --force --recreate-pods jupyter pangeo/pangeo \
     --version=$VERSION \
     -f secret-config.yaml \
     -f jupyter-config.yaml


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
