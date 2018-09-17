#!/bin/bash

set -e

helm upgrade pangeohub pangeo/pangeo --devel \
   -f secret_config.yaml \
   -f jupyter_config.yaml
