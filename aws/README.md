## Setup for Juypterhub/Dask on AWS
We used the Heptio quickstart template as described [here](https://zero-to-jupyterhub-with-kubernetes.readthedocs.io/en/latest/create-k8s-cluster.html#setting-up-kubernetes-on-amazon-web-services-aws) to initialize an a kubernetes cluster on AWS

The only major difference between the setup for AWS and GCE is in the jupyter-config.yaml file. 

The [setup.sh](/setup.sh) script has also modified to remove the automatic provisioning of kubernetest clusters on GCP. Again, use the setup described on Z2JH to provision kubernetes clusters on AWS. 

Note: The setup for GCE incorporates FUSE to dial in GCS buckets; I have taken that out - you should able to use s3fs but I have not describe it here.


## Steps
1. Launch the Heptio Quickstart Template to initialize a kubernetes cluster on AWS. Follow the steps [here](https://zero-to-jupyterhub-with-kubernetes.readthedocs.io/en/latest/create-k8s-cluster.html#setting-up-kubernetes-on-amazon-web-services-aws)
2. In your terminal, run the setup.sh script;
 `bash setup.sh`

3. Provision a DNS name for your server; you can point to the public-proxy of your balancer using a C-NAME
      
 
