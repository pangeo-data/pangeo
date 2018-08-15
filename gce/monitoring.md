```
kubectl create ns monitoring

helm install stable/prometheus --name prometheus --namespace monitoring -f prometheus.yaml

helm install stable/grafana --name grafana --namespace monitoring -f grafana.yaml
```
