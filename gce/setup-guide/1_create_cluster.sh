#!/bin/bash

set -e

echo $PROJECTID

NUM_NODES=2

# create cluster on GCP
gcloud config set project $PROJECTID
gcloud container clusters create $CLUSTER_NAME --num-nodes=$NUM_NODES --zone=$ZONE \
    --machine-type=n1-standard-2 --no-enable-legacy-authorization
gcloud container node-pools create worker-pool --zone=$ZONE --cluster=$CLUSTER_NAME \
    --machine-type=$WORKER_MACHINE_TYPE --preemptible --enable-autoscaling \
    --num-nodes=$MIN_WORKER_NODES --max-nodes=$MAX_WORKER_NODES --min-nodes=$MIN_WORKER_NODES
gcloud container clusters get-credentials $CLUSTER_NAME --zone=$ZONE --project $PROJECTID
