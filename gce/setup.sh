# Start cluster on Google cloud
gcloud container clusters create pangeo --num-nodes=3 --machine-type=n1-standard-2 --zone=us-central1-b  --cluster-version=1.8.4-gke.1
gcloud container clusters get-credentials pangeo --zone us-central1-b --project pangeo-181919

# Set up Kubernetes
kubectl create clusterrolebinding cluster-admin-binding --clusterrole=cluster-admin --user=mrocklinWgmail.com
kubectl --namespace kube-system create sa tiller
kubectl create clusterrolebinding tiller --clusterrole cluster-admin --serviceaccount=kube-system:tiller
helm init --service-account tiller
kubectl --namespace=kube-system patch deployment tiller-deploy --type=json --patch='[{"op": "add", "path": "/spec/template/spec/containers/0/command", "value": ["/tiller", "--listen=localhost:44134"]}]'

# Get Helm repositories
helm repo add dask https://dask.github.io/helm-chart/
helm repo add jupyterhub https://jupyterhub.github.io/helm-chart/
helm repo update

# Install JupyterHub and Dask on the cluster
helm install jupyterhub/jupyterhub --version=v0.5 --name=jupyter --namespace=pangeo -f jupyter-config.yaml
helm install dask/dask --name=dask --namespace=pangeo -f dask-config.yaml

# Look for publised services.  Route domain name A records to these IPs.
kubectl get services --namespace pangeo
# Look for dask-scheduler
#      and proxy-...


# In notebooks, connect to the Dask cluster like so:
# from dask.distributed import Client
# client = Client()
# client
