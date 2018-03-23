# Pangeo Helm Chart

This is the helm chart for installing Pangeo.

This chart is mainly going to be a wrapper to subcharts along with custom resources to tie them together.

Chart dependencies:
 - [jupyterhub](https://zero-to-jupyterhub.readthedocs.io/en/latest/)

## Usage

First off you need [helm](https://github.com/kubernetes/helm) if you don't have it already.

You also need to add the dependent chart repos.

```shell
# Add repos
helm repo add jupyterhub https://jupyterhub.github.io/helm-chart/

# Update repos
helm repo update
```

You then need to create a `values.yaml` file with your own config options in. As this chart is a collection of dependant charts you will need to refer to their configuration documentation for details. See the [values.yaml](pangeo/values.yaml) file for more information.

```shell
# Get chart dependencies
helm dependency update pangeo

# Install Pangeo
helm install pangeo --name=<release name> --namespace=<namespace> -f /path/to/custom/values.yaml

# Apply changes to Pangeo
helm upgrade <release name> pangeo -f /path/to/custom/values.yaml

# Delete Pangeo
helm delete <release name> --purge
```
