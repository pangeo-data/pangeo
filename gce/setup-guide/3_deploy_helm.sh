#!/bin/bash

set -e

helm repo add pangeo https://pangeo-data.github.io/helm-chart/
helm repo update

helm install pangeo/pangeo \
#   --version=$VERSION \
   --namespace=pangeo --name=pangeohub  \
   -f /opt/pangeo/secret_config.yaml \
   -f /opt/pangeo/jupyter_config.yaml
