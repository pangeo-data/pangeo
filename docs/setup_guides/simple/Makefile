# Makefile for the simple deploymet.
# Before running, make sure to install the prerequisites and update `secrets.yaml`
# with the secret tokens
.PHONY: group cluster dhub clean

LOCATION?=westeurope
GROUP?=pangeo
CLUSTER?=pangeoCluster
MIN_COUNT?=1
MAX_COUNT?=3

group:
	az group create --name $(GROUP) --location $(LOCATION)

cluster:
	az aks create --resource-group $(GROUP) --name $(CLUSTER) --generate-ssh-keys \
	--node-count=1 --enable-cluster-autoscaler --min-count=$(MIN_COUNT) --max-count=$(MAX_COUNT)
	az aks get-credentials  --name $(CLUSTER) --resource-group $(GROUP)

dhub:
	helm upgrade --wait --install --create-namespace \
		dask dask/daskhub \
		--namespace=dhub \
		--values=secrets.yaml

clean:
	az group delete -n $(GROUP)