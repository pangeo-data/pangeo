# Start cluster on Google cloud
gcloud container clusters create pangeo --no-enable-legacy-authorization --num-nodes=10 --machine-type=n1-standard-2 --zone=us-central1-b  --cluster-version=1.9.3-gke.0

gcloud container clusters get-credentials pangeo --zone us-central1-b --project pangeo-181919

# Set up Kubernetes
kubectl create clusterrolebinding cluster-admin-binding --clusterrole=cluster-admin --user=jhamman1@gmail.com
kubectl --namespace kube-system create sa tiller
kubectl create clusterrolebinding tiller --clusterrole cluster-admin --serviceaccount=kube-system:tiller
helm init --service-account tiller
kubectl --namespace=kube-system patch deployment tiller-deploy --type=json --patch='[{"op": "add", "path": "/spec/template/spec/containers/0/command", "value": ["/tiller", "--listen=localhost:44134"]}]'

# Get Helm repositories
helm repo add pangeo https://pangeo-data.github.io/helm-chart/
helm repo update

# Install JupyterHub and Dask on the cluster
helm install pangeo/pangeo --version=v0.1.0-673e876 --name=jupyter --namespace=pangeo -f jupyter-config.yaml -f secret-config.yaml

# Look for publised services.  Route domain name A records to these IPs.
kubectl get services --namespace pangeo
# Look for dask-scheduler
#      and proxy-...


# In notebooks, connect to the Dask cluster like so:
# from dask.distributed import Client
# client = Client()
# client
