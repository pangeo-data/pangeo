#!/bin/bash

#SBATCH --exclusive
#SBATCH -N 1
#SBATCH -J dask-worker
#SBATCH --time=6:00:00

# Writes ~/scheduler.json file in home directory
# Connect with
# >>> from dask.distributed import Client
# >>> client = Client(scheduler_file='~/scheduler.json')

# Setup Environment
module load anaconda
source activate pangeo

SCHEDULER=$HOME/scheduler.json
mpirun --np 6 dask-mpi --nthreads 4 \
    --memory-limit 12e9 \
    --interface ib0 \
    --no-scheduler --local-directory /local \
    --scheduler-file=$SCHEDULER
