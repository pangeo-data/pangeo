Installing Pangeo on Azure
--------------------------

This guide takes you through the steps necessary to install Pangeo on Microsoft's Azure Cloud Platform.
We'll make use of Azure's Kubernetes as a Service offering, called AKS (Azure Kubernetes Service),
for installing Pangeo on Azure.
Documentation on AKS can be found here: https://docs.microsoft.com/en-gb/azure/aks/.

.. Note::
  This guide lays out only the fundamental steps required to install Pangeo on Azure AKS.
  Further work, for example to secure your cluster, is highly advised but not directly
  covered here.


Step One: Build Kubernetes service
==================================

The first step to installing Pangeo on Azure is to set up a Kubernetes service
that can be used to run Pangeo. This can be done either by using the web interface
or by using the Azure commandline interface (CLI). These are both practical options,
so we'll cover each one in turn.

Using the web interface
~~~~~~~~~~~~~~~~~~~~~~~

To use the Azure web interface you must first have a Microsoft account that you
can use to log into the Azure web interface. If you have an existing Microsoft
account (for example, a hotmail.com or outlook.com email address) then you can use
that, or you can create a new account.

Once you have logged into the Azure web interface, navigate to Kubernetes services
and click the blue Add logo in the top left. This will display the Create Kubernetes cluster
wizard.

Work through the wizard customising the Kubernetes service to be created as you
see necessary (though the defaults are largely reasonable). In the last step before
the cluster is created a validation process is run, ensuring that the customisations you have
made will produce a working cluster. At this step you can also download a
template file to make reproducing or automating cluster creation simpler in the future.

Autoscaling
```````````

One benefit of the web interface is that we can easily create an AKS resource that implements
autoscaling via virtual nodes (see https://docs.microsoft.com/en-us/azure/aks/virtual-nodes-portal
for further details on this concept). Virtual nodes are still a preview feature in Azure, so some
limitations currently apply. To enable virtual nodes you need to have followed the setup steps in the
link above and also be using an Azure region where nodes are supported.

With both of these requirements met, you can enable virtual nodes for autoscaling your Kubernetes
service. In the Scale tab, ensure that both the Virtual Nodes and VM scale sets selectors are
set to 'Enabled'.


Using the Azure CLI
~~~~~~~~~~~~~~~~~~~

Instructions for downloading and installing the Azure CLI on major Operating Systems
can be found at: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest.
All interactions with the Azure CLI are via the ``az`` command.

To create a basic Kubernetes service using the Azure CLI:

.. code-block:: bash

  az aks create \
    --resource-group $RESOURCE_GROUP_NAME \
    --name $AKS_RESOURCE_NAME \
    --kubernetes-version 1.12.6 \
    --node-count 1 \
    --node-vm-size Standard_B8ms

You'll need to specify a name for your Kubernetes service (as ``$AKS_RESOURCE_NAME``) and a
name for an (existing) resource group (as ``$RESOURCE_GROUP_NAME``). Note that here
we've also asked for a medium-sized VM to host the node rather than the default.
You can specify any VM name listed in the links from this page as the value to this key:
https://docs.microsoft.com/en-us/azure/virtual-machines/windows/sizes.

.. note::
  RBAC (Role-Based Access Control) is enabled by default on Kubernetes services set up using
  the Azure CLI. If you need to change this default behaviour, you can specify the
  ``disable-rbac`` flag when creating your Kubernetes cluster.

The ``az aks create`` command above assumes that you have already set up a resource group
to deploy your Kubernetes service into. If you have not already set up a resource group,
run this command *before* creating your Kubernetes service:

.. code-block:: bash

  az group create \
    --name $RESOURCE_GROUP_NAME \
    --location $RESOURCE_REGION \

The location of the resource group needs to be specified as a single word
programmatic name for an Azure region. A list of available locations can be found
by running the following:

.. code-block:: bash

  az account list-locations | grep name

Autoscaling
```````````

To create a Kubernetes service with autoscaling enabled you can add extra keys
to the previous ``az aks create`` command:

.. code-block:: bash

  az aks create \
    --resource-group $RESOURCE_GROUP_NAME \
    --name $AKS_RESOURCE_NAME \
    --kubernetes-version 1.12.6 \
    --node-count 1 \
    --node-vm-size Standard_B8ms \
    --enable-vmss \
    --enable-cluster-autoscaler \
    --min-count 1 \
    --max-count 10

You can also update an existing Kubernetes service to add autoscaling:

.. code-block:: bash

  az aks update \
  --resource-group $RESOURCE_GROUP_NAME \
  --name $AKS_RESOURCE_NAME \
  --enable-cluster-autoscaler \
  --min-count 1 \
  --max-count 3

More information on autoscaling with Azure AKS is available here:
https://docs.microsoft.com/en-gb/azure/aks/cluster-autoscaler.


Step Two: Customise cluster
===========================

With a working Kubernetes service now built we can customise it in readiness for installing Pangeo
on the cluster. At its most basic, this means installing helm and tiller, but other
customisations (such as authentication) can also be added at this stage.
The customisations need to be performed using the Azure CLI. If you don't have the Azure CLI available,
you can either:

* follow the steps at the link above to install the Azure CLI locally, or
* use the cloud shell built into the web interface
  (click the ``>_`` logo at the right of the blue bar at the top of the web interface).
  The cloud shell includes the Azure CLI and a basic implementation of Visual Studio Code editor.

Kubernetes credentials
~~~~~~~~~~~~~~~~~~~~~~

Before we can progress we need to acquire kubernetes credentials for our newly-created
AKS resource:

.. code-block:: bash

  az aks get-credentials -g $RESOURCE_GROUP_NAME -n $AKS_RESOURCE_NAME --overwrite-existing


You will need to provide the name of the AKS resource that you just created (as ``$AKS_RESOURCE_NAME``)
and the group within which the resource was created (as ``$RESOURCE_GROUP_NAME``).


Helm and tiller
~~~~~~~~~~~~~~~

Installing helm and tiller allows us to customise our Kubernetes service by applying
helm charts to it. We need to ensure that helm and tiller will work correctly with
RBAC, which is enabled by default on Azure Kubernetes services.

.. code-block:: bash

  kubectl apply -f helm_rbac.yaml
  helm init --upgrade --service-account tiller --wait

The contents of ``helm_rbac.yaml`` are as follows:

.. code-block:: yaml

  apiVersion: v1
  kind: ServiceAccount
  metadata:
    name: tiller
    namespace: kube-system
  ---
  apiVersion: rbac.authorization.k8s.io/v1
  kind: ClusterRoleBinding
  metadata:
    name: tiller
  roleRef:
    apiGroup: rbac.authorization.k8s.io
    kind: ClusterRole
    name: cluster-admin
  subjects:
    - kind: ServiceAccount
      name: tiller
      namespace: kube-system


Step 3: Install Pangeo
======================

Now we can move onto installing Pangeo on our Kubernetes service. This can be done
as follows:

.. code-block:: bash

  helm repo add pangeo https://pangeo-data.github.io/helm-chart/
  helm repo update
  helm upgrade --install --namespace pangeo pangeo pangeo/pangeo -f pangeo.yaml

The contents of the ``pangeo.yaml`` file came from the Zero to Jupyterhub guide.


Test install
~~~~~~~~~~~~

To test that Pangeo has installed successfully on your Kubernetes service, find
the IP address of the Pangeo proxy:

.. code-block::

  kubectl get svc proxy-public --namespace=pangeo

Navigate to the ``EXTERNAL-IP`` address listed there in your web browser.
If JupyterHub loads then you have successfully installed Pangeo on your Azure Kubernetes service!


Autoscaling
~~~~~~~~~~~

If you set up your autoscaling Kubernetes service using the cluster autoscaler then autoscaling
should work with no further customisation neeeded. If instead you set up autoscaling using
virtual nodes and VM scale sets then a little more work is needed. In particular we need to
modify the Pangeo ``worker-template.yaml`` file to add two more key groups to the ``spec`` section
of the yaml:

.. code-block:: yaml

  nodeSelector:
    kubernetes.io/role: agent
    beta.kubernetes.io/os: linux
    type: virtual-kubelet
  tolerations:
  - key: virtual-kubelet.io/provider
    operator: Exists
  - key: azure.com/aci
    effect: NoSchedule
