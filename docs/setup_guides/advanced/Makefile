# Makefile for the recommended deploymet.
# Before running, make sure to install the prerequisites and update `secrets.yaml`
# with the secret tokens
.PHONY: group cluster dhub clean

LOCATION?=westeurope
GROUP?=pangeo
CLUSTER?=pangeoCluster
MAX_USER_NODE_COUNT?=10
MAX_WORKER_NODE_COUNT?=50


group:
	az group create --name $(GROUP) --location $(LOCATION)


cluster:
	az aks create --resource-group $(GROUP) --name $(CLUSTER) --generate-ssh-keys \
		--node-count=1 \
		--nodepool-name core \
		--nodepool-labels hub.jupyter.org/node-purpose=core

	# Add a node-pool: one for the users and Dask schedulers
	az aks nodepool add \
		--name users \
		--cluster-name $(CLUSTER) \
		--resource-group $(GROUP) \
		--enable-cluster-autoscaler \
		--node-count 1 \
		--min-count 0 --max-count $(MAX_USER_NODE_COUNT) \
		--node-vm-size Standard_D2s_v3 \
		--labels hub.jupyter.org/node-purpose=user

	# Add a node-pool for Dask workers.
	az aks nodepool add \
		--name workers \
		--cluster-name $(CLUSTER) \
		--resource-group $(GROUP) \
		--enable-cluster-autoscaler \
		--node-count 1 \
		--min-count 0 --max-count $(MAX_WORKER_NODE_COUNT) \
		--node-vm-size Standard_D2s_v3 \
		--priority Spot \
		--eviction-policy Delete \
		--spot-max-price -1 \
		--labels="k8s.dask.org/dedicated=worker"
	az aks get-credentials --name $(CLUSTER) --resource-group $(GROUP)

dhub:
	helm upgrade --wait --install --create-namespace \
		dask dask/daskhub \
		--namespace=dhub \
		--values=config.yaml

clean:
	az group delete -n $(GROUP)