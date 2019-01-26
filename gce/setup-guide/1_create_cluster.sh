#!/bin/bash

set -e

NUM_NODES=2

# create cluster on GCP
gcloud config set project $PROJECTID
gcloud services enable container.googleapis.com #To enable the Kubernetes Engine API

gcloud container clusters create $CLUSTER_NAME --num-nodes=$NUM_NODES --zone=$ZONE \
    --machine-type=n1-standard-2 --no-enable-legacy-authorization
#gcloud container node-pools create worker-pool --zone=$ZONE --cluster=$CLUSTER_NAME \
#    --machine-type=$WORKER_MACHINE_TYPE --preemptible --enable-autoscaling \
#    --num-nodes=$MIN_WORKER_NODES --max-nodes=$MAX_WORKER_NODES --min-nodes=$MIN_WORKER_NODES
gcloud container node-pools create worker-pool --zone=$ZONE --cluster=$CLUSTER_NAME \
    --machine-type=$WORKER_MACHINE_TYPE --preemptible --num-nodes=$MIN_WORKER_NODES
gcloud container clusters update $CLUSTER_NAME --zone=$ZONE --node-pool=worker-pool --enable-autoscaling --max-nodes=$MAX_WORKER_NODES --min-nodes=$MIN_WORKER_NODES
gcloud container clusters get-credentials $CLUSTER_NAME --zone=$ZONE --project $PROJECTID
