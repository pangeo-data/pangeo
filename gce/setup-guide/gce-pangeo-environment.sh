# Google project id
export PROJECTID='<YOUR GOOGLE CLOUD PROJECT ID>'
# Kubernetes cluster admin
export EMAIL='<THE EMAIL ADDRESS ASSOCIATED WITH YOUR GOOGLE CLOUD ACCOUNT>'

# Set up zone and region (see: https://cloud.google.com/compute/docs/regions-zones/)
export ZONE='<CLOUD ZONE>'
export REGION='<CLOUD_REGION>'

# cluster size settings: modify as needed to fit your needs / budget
export MIN_WORKER_NODES=0
export MAX_WORKER_NODES=100
export CLUSTER_NAME='pangeo-cluster'

# https://cloud.google.com/compute/pricing
# change the machine typer based on your computing needs
export WORKER_MACHINE_TYPE='n1-standard-4'

# HELM Pangeo version if needed
export VERSION="0.1.1-c02878a"
