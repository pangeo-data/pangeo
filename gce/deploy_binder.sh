#!/usr/bin/env bash

# on GCP
# 0) get a GCP account if you don't already have one
# 1) create a project with a project name of pangeo and note the project id
# 2) switch to the pangeo project
# 3) in APIs and Services enable the Kubernetes Engine API for the pangeo project

# on local computer
# 1) install google cloud sdk (https://cloud.google.com/sdk/downloads)
# 2) install helm >=v2.8.2 (https://github.com/kubernetes/helm/blob/master/docs/install.md)
# 3) setup gcloud sdk
#    - gcloud components update
#    - gcloud components install kubectl
#    - gcloud config set container/new_scopes_behavior true
#    - gcloud auth login
# 4) modify secret-config.yaml file, replacing TOKEN with output from `openssl rand -hex 32`
# 5) modify the settings section of this file to match your settings and requirements
# 6) run this file on a not-windows machine

# settings
EMAIL='jhamman1@gmail.com'
PROJECTID='pangeo-181919'
ZONE='us-central1-b'
NUM_NODES=2
MIN_WORKER_NODES=0
MAX_WORKER_NODES=10
CLUSTER_NAME='pangeo-binder'

# create cluster on GCP
gcloud config set project $PROJECTID
gcloud container clusters create $CLUSTER_NAME --num-nodes=$NUM_NODES --machine-type=n1-standard-2 --zone=$ZONE --no-enable-legacy-authorization
gcloud container node-pools create worker-pool --zone=$ZONE --cluster=$CLUSTER_NAME --machine-type=n1-standard-4 --preemptible --enable-autoscaling --num-nodes=$MIN_WORKER_NODES --max-nodes=$MAX_WORKER_NODES --min-nodes=$MIN_WORKER_NODES
gcloud container clusters get-credentials $CLUSTER_NAME --zone=$ZONE --project $PROJECTID

# set up kubernetes
kubectl create clusterrolebinding cluster-admin-binding --clusterrole=cluster-admin --user=$EMAIL
kubectl create serviceaccount tiller --namespace=kube-system
kubectl create clusterrolebinding tiller --clusterrole=cluster-admin --serviceaccount=kube-system:tiller
helm init --service-account tiller
#helm init --wait --service-account tiller
kubectl --namespace=kube-system patch deployment tiller-deploy --type=json --patch='[{"op": "add", "path": "/spec/template/spec/containers/0/command", "value": ["/tiller", "--listen=localhost:44134"]}]'

# get helm repositories
helm repo add jupyterhub https://jupyterhub.github.io/helm-chart/
helm repo update

# install jupyterhub on the cluster
echo "Installing jupyterhub."
helm install jupyterhub/binder --version=v0.1.0-856e3e6 --name=jupyter --namespace=jupyter -f binder_config.yaml -f binder_secret.yaml

# to upgrade:
# helm upgrade pangeo-binder jupyterhub/binderhub --version=v0.1.0-856e3e6 -f binder_config.yml -f binder_secret.yml --force --recreate-pods
