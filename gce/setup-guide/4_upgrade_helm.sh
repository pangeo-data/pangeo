#!/bin/bash

set -e

helm upgrade --force --recreate-pods --devel pangeohub pangeo/pangeo \
#   --version=$VERSION \
   -f /opt/pangeo/secret_config.yaml \
   -f /opt/pangeo/jupyter_config.yaml
