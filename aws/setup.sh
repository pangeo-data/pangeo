# Set up Kubernetes
kubectl create clusterrolebinding cluster-admin-binding --clusterrole=cluster-admin --user=mrocklin@gmail.com
kubectl --namespace kube-system create sa tiller
kubectl create clusterrolebinding tiller --clusterrole cluster-admin --serviceaccount=kube-system:tiller
helm init --service-account tiller
kubectl --namespace=kube-system patch deployment tiller-deploy --type=json --patch='[{"op": "add", "path": "/spec/template/spec/containers/0/command", "value": ["/tiller", "--listen=localhost:44134"]}]'

# Get Helm repositories
helm repo add jupyterhub https://jupyterhub.github.io/helm-chart/
helm repo update

# Install JupyterHub and Dask on the cluster
helm install jupyterhub/jupyterhub --version=v0.6.0-9701a90 --name=jupyter --namespace=pangeo -f jupyter-config.yaml
helm install dask/dask --name=dask --namespace=pangeo -f dask-config.yaml

# Look for publised services.  For AWS, route CNAME records to load balancer public proxy
kubectl get services --namespace pangeo
# Look for dask-scheduler
#      and proxy-...


# In notebooks, connect to the Dask cluster like so:
# from dask.distributed import Client
# client = Client()
# client
