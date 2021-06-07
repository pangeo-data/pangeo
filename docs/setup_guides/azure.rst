Installing Pangeo on Azure
==========================

In this guide, you'll deploy a Pangeo-style JupyterHub on Microsoft Azure. This will deploy a multi-user JupyterHub enabled with Dask for scalable computing.

We'll use

* `Azure Kubernetes Service <https://docs.microsoft.com/en-us/azure/aks/intro-kubernetes>`__ (AKS), Azure's managed Kubernetes service
* The `daskhub Helm Chart <https://github.com/dask/helm-chart/tree/main/daskhub>`__, an easy way to install JupyterHub and Dask-Gateway

We describe two deployment scenarios, a :ref:`simple` and a :ref:`recommended`. If you're new to Azure, Kubernetes, or JupyterHub, then you should try the simple deployment to verify that the basics work, before moving on to the more advanced recommend deployment.

This guide uses the Azure CLI to create the Azure Resources.
Both deployment scenarios include a ``Makefile`` with targets for the AKS cluster and Hub deployment. If you're just looking to deploy a Hub, feel free to use and adapt the Makefiles. If you're looking to build understanding, read through the guide.

As an alternative to this guide, you might use `Qhub <https://docs.qhub.dev/en/latest/>`_, which provides a higher-level tool to obtain a JupyterHub and Dask deployment on Kubernetes (or HPC).

.. note::

   These examples create the Azure Resources in the West Europe region. This is a good
   choice if you wish to access the data from `Microsoft's Planetary Computer <https://planetarycomputer.microsoft.com/catalog>`__.
   Make sure to deploy your cluster in the same region as the data you'll be accessing.


Prerequisites
-------------

We'll assume that you've completed the `prerequisites <https://docs.microsoft.com/en-us/azure/aks/kubernetes-walkthrough#prerequisites>`__ for creating an AKS cluster. This includes

* Obtaining an `Azure Subscription <https://docs.microsoft.com/en-us/azure/guides/developer/azure-developer-guide#understanding-accounts-subscriptions-and-billing>`_.
* Installing and configuring the `Azure CLI <https://docs.microsoft.com/en-us/cli/azure/install-azure-cli>`__
* Installing `kubectl <https://kubernetes.io/docs/tasks/tools/>`__ (``az aks install-cli``)
* Installing `Helm <https://helm.sh/docs/intro/install/>`__

.. _simple:

Simple deployment
-----------------

This section walks through the simplest possible deployment, but lacks basic features like authentication, HTTPS, and a user-friendly DNS name. We recommend trying this deployment to ensure that the tools work, before deleting things and moving on to the advanced deployment.
You can download the :download:`Makefile <simple/Makefile>` and :download:`Helm config <simple/secrets.yaml>` for this deployment.

Kubernetes Cluster
^^^^^^^^^^^^^^^^^^

Following the `Kubernetes walkthrough <https://docs.microsoft.com/en-us/azure/aks/kubernetes-walkthrough>`__, we'll use the Azure CLI to create an AKS cluster.

For ease of reading we'll repeat the steps here, but visit the `<guide https://docs.microsoft.com/en-us/azure/aks/kubernetes-walkthrough>`__ to build understanding about what each command does.  For ease of cleanup, we recommend creating
a brand-new resource group.

.. code-block:: console

   # Create a Resource group
   $ az group create --name pangeo --location westeurope
   {
     "id": "/subscriptions/<guid>/resourceGroups/pangeo",
     "location": "westeurope",
     "managedBy": null,
     "name": "pangeo",
     "properties": {
       "provisioningState": "Succeeded"
     },
     "tags": null
   }

   # Create an AKS cluster
   $ az aks create --resource-group pangeo --name pangeoCluster --generate-ssh-keys \
     --node-count=1 --enable-cluster-autoscaler --min-count=1 --max-count=5

   # Get credentials for kubectl / helm
   $ az aks get-credentials  --name pangeoCluster --resource-group pangeo

At this point, you should have a Kubernetes Cluster up and running. Verify that things are are working OK with ``kubectl``

.. code-block:: console

   $ kubectl get node
   NAME                                STATUS   ROLES  AGE   VERSION
   aks-nodepool1-26963941-vmss000000   Ready    agent   1m   v1.19.11

JupyterHub and Dask Gateway
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Now we're ready to install JupyterHub and Dask Gateway using the `daskhub <https://helm.dask.org/>`__ helm chart. Visit the documentation at https://github.com/dask/helm-chart/tree/main/daskhub for more background. 


1. Download or update the ``daskhub`` helm chart

.. code-block:: console

   $ helm repo add dask https://helm.dask.org
   $ helm repo update

2. Generate two secret tokens: one for JupyterHub's proxy and one for Dask Gateway to act as a JupyterHub service.

.. code-block:: console

   $ openssl rand -hex 32
   <secret token - 1>

   $ openssl rand -hex 32
   <secret token - 2>

3. Create a configuration file with the customizations to the ``daskhub`` helm chart. We'll call ours ``secrets.yaml``. You should replace ``<secret token - 1>`` and ``<secret token - 2>`` with the outputs of the previous commands.

.. code-block:: yaml

   # file: secrets.yaml
   jupyterhub:
     proxy:
       # output from openssl rand -hex 32. Must match dask-gateway.gateway.auth.jupyterhub.apiToken
       secretToken: "<secret token - 1>"
   
     hub:
       # Disable hub network Policy, so that the dask gateway server can reach the hub directly
       # https://github.com/dask/helm-chart/issues/142
       networkPolicy:
         enabled: false
   
       services:
         dask-gateway:
           # output from openssl rand -hex 32. Must match dask-gateway.gateway.auth.jupyterhub.apiToken
           apiToken: "<secret token - 2>"
   
   dask-gateway:
     gateway:
       auth:
         jupyterhub:
           # output from openssl rand -hex 32. Must match jupyterhub.services.dask-gateway.apiToken
           apiToken: "<secret token - 2>"

4. Install ``daskhub``. We'll install it into a new ``dhub`` namespace, but you can use whatever namespace you like.

.. code-block:: console

   $ helm upgrade --wait --install --create-namespace \
     dask dask/daskhub \
     --namespace=dhub \
     --values=secrets.yaml
   Release "dask" does not exist. Installing it now.
   NAME: dask
   LAST DEPLOYED: Fri Jun  4 14:21:33 2021
   NAMESPACE: dhub
   STATUS: deployed
   REVISION: 1
   TEST SUITE: None
   NOTES:
   DaskHub
   -------
   
   Thank you for installing DaskHub, a multiuser, Dask-enabled JupyterHub!
   
   Your release is named dask and installed into the namespace dhub.
   
   
   Jupyter Hub
   -----------
   
   You can find if the hub and proxy is ready by doing:
   
    kubectl --namespace=dhub get pod
   
   and watching for both those pods to be in status 'Ready'.
   
   You can find the public IP of the JupyterHub by doing:
   
    kubectl --namespace=dhub get svc proxy-public
   
   It might take a few minutes for it to appear!

Now DaskHub is deployed. The instructions printed above demonstrate how to get the IP address of your hub.

.. warning::

   This simple deployment doesn't have any kind of authentication. See :ref:`recommended` for how to create a deployment with authentication.

When you log in and start a notebook sever, you should be able to connect to the Dask Gateway server and create a cluster.

.. code-block:: python

   >>> from dask_gateway import Gateway
   >>> gateway = Gateway()
   >>> gateway.list_clusters()
   []
   >>> cluster = gateway.new_cluster()
   >>> client = cluster.get_client()
   >>> cluster.scale(1)

After a moment, the Dask Scheduler and Worker pods should start up. Check the pods with ``kubectl -n dhub get pods``.

Cleanup
^^^^^^^

The easiest way to clean up the resources is to delete the resource group

.. code-block:: console

   $ az group delete -n pangeo


.. _recommended:

Recommended Deployment
----------------------

This deployment is a bit more more complicated. Compared to the simple deployment, it 

1. Supports HTTPs and uses a hostname rather than IP Address
2. Uses multiple node pools, one per type of worker, with spot (preemptible) nodes for Dask workers to save on costs

Just like before, we'll create the Azure Resources first, and deploy `daskhub` second. We'll use the following values

========================== =============
Name                       value
========================== =============
Resource group             pangeo
Cluster name               pangeoCluster
Azure AD Application Name  pangeo-app
Hub Name                   pangeo-hub
========================== =============

Azure Resources
^^^^^^^^^^^^^^^

1. Create a Resource Group
""""""""""""""""""""""""""

.. code-block:: console

   # Create a Resource group
   $ az group create --name pangeo --location westeurope
   {
     "id": "/subscriptions/<subscriptionId>/resourceGroups/pangeo",
     "location": "westeurope",
     "managedBy": null,
     "name": "pangeo",
     "properties": {
       "provisioningState": "Succeeded"
     },
     "tags": null,
   }

2. Create an App Registration
"""""""""""""""""""""""""""""

To authenticate users, we'll create an Azure AD App registration following `the instructions <https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app>`__.
In this example, the *sign-in audience* will be **Accounts in this organizational directory only**. This is appropriate when your administering a Hub for other users within your Azure AD tenant.

The redirect URI should match where your users will access the Hub. If your organization already has a DNS provider, use that.
Otherwise, you can have Azure handle the DNS for your Hub service automatically, which is what we'll use in this guide.
We're calling our cluster ``pangeo-hub`` and deploying it in West Europe, so the callback URL is ``https://pangeo-hub.westeurope.cloudapp.azure.com/hub/oauth_callback``.
In general the pattern is ``https://<hub-name>.<azure-region>.cloudapp.azure.com/hub/oauth_callback``.

Finally, create a Client Secret to pass to JupyterHub: Under the *Manage* section, select *Certificates and Secrets* then *New client secret*. We'll use the ``Value`` later on.
You will also need the App Registration's ``Client ID`` and ``Tenant ID``, which are available on its main page, under *Essentials*.

To summarize, we now have our app registration's

- Client ID
- Tenant ID
- Client Secret
- OAuth callback URL

For more on authentication see `Authentication and Authorization <https://zero-to-jupyterhub.readthedocs.io/en/latest/administrator/authentication.html>`__, in particular the section on `Azure AD <https://zero-to-jupyterhub.readthedocs.io/en/latest/administrator/authentication.html#azure-active-directory>`__.

3. Create a Kubernetes Cluster
""""""""""""""""""""""""""""""

Now we'll create a Kubernetes cluster. Compared to last time, we'll have three node pools: A "core" pool for JupyterHub pods (the Hub, etc.) and Kubernetes itself, a "user" pool for user pods and Dask schedulers, and a "worker" pool for Dask workers.

.. code-block:: console

   # Create an AKS cluster
   $ az aks create --resource-group pangeo --name pangeoCluster --generate-ssh-keys \
     --node-count=1 \
     --nodepool-name core \
     --nodepool-labels hub.jupyter.org/node-purpose=core

   # Add a node-pool: one for the users and Dask schedulers
   $ az aks nodepool add \
       --name users \
       --cluster-name pangeoCluster \
       --resource-group pangeo \
       --enable-cluster-autoscaler \
       --node-count 1 \
       --min-count 0 --max-count 10 \
       --node-vm-size Standard_D2s_v3 \
       --labels hub.jupyter.org/node-purpose=user

   # Add a node-pool for Dask workers.
   $ az aks nodepool add \
       --name workers \
       --cluster-name pangeoCluster \
       --resource-group pangeo \
       --enable-cluster-autoscaler \
       --node-count 1 \
       --min-count 0 --max-count 50 \
       --node-vm-size Standard_D2s_v3 \
       --priority Spot \
       --eviction-policy Delete \
       --spot-max-price -1 \
       --labels="k8s.dask.org/dedicated=worker"

At this point, you should have a functioning Kubernetes Cluster with multiple node-pools. For example

.. code-block:: console

   $ az aks get-credentials \
       --name pangeoCluster \
       --resource-group pangeo \
       --output table

   $ kubectl get node
   NAME                              STATUS   ROLES   AGE     VERSION
   aks-core-26963941-vmss000000      Ready    agent   15m     v1.19.11
   aks-users-26963941-vmss000000     Ready    agent   8m19s   v1.19.11
   aks-workers-26963941-vmss000000   Ready    agent   3m3s    v1.19.11


Deploy DaskHub
^^^^^^^^^^^^^^

1. Get the Helm chart
"""""""""""""""""""""

Download or update the ``daskhub`` helm chart.

.. code-block:: console

   $ helm repo add dask https://helm.dask.org
   $ helm repo update

2. Generate secret tokens
"""""""""""""""""""""""""

We need two secret tokens: one for JupyterHub's proxy and one for Dask Gateway to act as a JupyterHub service.

.. code-block:: console

   $ openssl rand -hex 32
   <secret token - 1>
   
   $ openssl rand -hex 32
   <secret token - 2>

3. Create a configuration file
""""""""""""""""""""""""""""""

This configuration file is used to customize the deployment with Helm. You can start with the :download:`reference config file<advanced/config.yaml>`.

.. warning::

   For simplicity, we've included all of the configuration values
   in a single `config.yaml` file, including sensitive values. We recommend keeping the sensitive values in a separate, encrypted file
   that's decrypted just when deploying.

.. literalinclude:: advanced/config.yaml
   :language: yaml

4. Install ``daskhub``
""""""""""""""""""""""

We'll install it into a new ``dhub`` namespace, but you can use whatever namespace you like.

.. code-block:: console

   $ helm upgrade --wait --install --create-namespace \
     dask dask/daskhub \
     --namespace=dhub \
     --values=config.yaml

Verify that all the pods are running with

.. code-block:: console

   $ kubectl -n dhub get pod
   NAME                                           READY   STATUS    RESTARTS   AGE
   api-dask-dask-gateway-947887bf9-f748w          1/1     Running   0          18m
   autohttps-66bd64d49b-wskqc                     2/2     Running   0          18m
   continuous-image-puller-nwq4l                  1/1     Running   0          18m
   controller-dask-dask-gateway-ccf4595c8-lx2h7   1/1     Running   0          18m
   hub-56d584b5b5-7rxvk                           1/1     Running   0          18m
   proxy-5b4bb9b8bb-q8r7x                         1/1     Running   0          18m
   traefik-dask-dask-gateway-d9d4cc45c-whmmw      1/1     Running   0          18m
   user-scheduler-86c6bc8cd-h6dx2                 1/1     Running   0          18m
   user-scheduler-86c6bc8cd-hhhbn                 1/1     Running   0          18m

.. note::

   If you see an HTTPS error accessing the hub, you may need to recreate the ``autohttps`` pod created by JupyterHub.

   .. code-block:: console

      $ kubectl -n dhub delete pod -l app=jupyterhub,component=autohttps

   This will recreate the ``autohttps`` pod and successfully get a TLS certificate so that the Hub can be accessed
   over HTTPS.

When you log in and start a notebook sever, you should be able to connect to the Dask Gateway server and create a cluster.

.. code-block:: python

   >>> from dask_gateway import Gateway
   >>> gateway = Gateway()
   >>> gateway.list_clusters()
   []
   >>> cluster = gateway.new_cluster()
   >>> client = cluster.get_client()
   >>> cluster.scale(1)

After a moment, the Dask Scheduler and Worker pods should start up. Check the pods with ``kubectl -n dhub get pods``.


Cleanup
^^^^^^^

The easiest way to clean up the resources is to delete the resource group

.. code-block:: console

   az group delete -n pangeo

Next steps
----------

Your AKS cluster and JupyterHub deployments can be customized in various ways. Visit the the `Azure Kubernetes Service overivew <https://docs.microsoft.com/en-us/azure/aks/intro-kubernetes>`__ for more on AKS, `Zero to JupyterHub with Kubernetes <https://zero-to-jupyterhub.readthedocs.io/en/latest/>`__ documentation for more on JupyterHub and the JupyterHub helm chart, and `Dask Gateway <https://gateway.dask.org/>`__ for more on Dask Gateway.