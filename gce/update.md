Instructions to Update Pangeo Deployment
========================================

This document includes detailed instructions on how to update the default
environment for the specific pangeo.pydata.org deployment.  It may also be of
general use for other deployments.


Update Docker Images
--------------------

Modify the Dockerfiles in `gce/notebook` and `gce/worker` to suit your needs,
possibly including new versions of libraries.  Consider also adding new
examples to the `gce/notebook/examples` directory.

We recommend that you first modify the worker docker image because you will
need to include its new tag in the `gce/notebook/worker-template.yaml` file.

### Build worker image

Navigate to the worker directory and build the docker image.  We currently use
the date like `YYYY-MM-DD` as a tag.

```bash
cd gce/worker
# edit Dockerfile
docker build -t pangeo/notebook:TAG .
```

You will probably have to do this a few times.


### Build Notebook image

Navigate to the `gce/notebook` directory and modify the Dockerfile, notebooks,
and `worker-template.yaml` file as necessary.  In particular you should update
the `image:` tag to match the tag of the worker that you have just built.

```bash
docker build -t pangeo/notebook:TAG .
```

### Push to dockerhub

You can push both images to docker hub:

```bash
docker push pangeo/worker:TAG
docker push pangeo/notebook:TAG
```


Update JupyterHub config file
-----------------------------

The JupyterHub deployment is defined in the `gce/jupyter-config.yaml` file.
You might want to take this opportunity to add new administrators, define
memory and CPU resources limits for the Jupyter servers, etc..
You will also need to update the tag of the `pangeo/notebook`
docker image to the TAG that you created above (likely the date `YYYY-MM-DD`).

You will also notice that two entries have been marked `SECRET`.
You will need to fill these entries with values known to the Pangeo
maintainers.  Request these personally by e-mail from whomever you know that
manages the cluster.


Update the deployment with Helm
-------------------------------

### Install Helm

You will need Helm.

```bash
curl https://raw.githubusercontent.com/kubernetes/helm/master/scripts/get > install-helm.bash
bash install-helm.bash --version v2.6.2
```

### Connect Kubectl to Pangeo Kubernetes deployment

And you will need kubectl (see web for instructions) and a connection to the
Pangeo deployment.  You can find the connection information by navigating to
the
[console](https://console.cloud.google.com/kubernetes/list?project=pangeo-181919)
and pressing the "connect" button near the cluster that you care about.


### Upgrade

Finally, use helm to *upgrade* the JupyterHub deployment.  You will need to
specify the jupyter-config.yaml file and a particular version of JupyterHub

```bash
helm upgrade jupyter pangeo/pangeo -f jupyter-config.yaml -f secret-config.yaml --version=v0.1.0-673e876
```

Verify
------

Please verify that things work nicely.
You may need to kill and restart sessions for jupyter containers to be reset.
You may want to use `helm rollback` to revert to previous deployments.
