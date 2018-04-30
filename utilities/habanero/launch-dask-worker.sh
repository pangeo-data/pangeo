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
source mod_env_setup.sh

# memory-limit is per process
# since we use six processes, we request approx 1/6 of system memory
# 0.15 < 0.1666666

LDIR=/local/$USER
rm -rf $LDIR

SCHEDULER=$HOME/scheduler.json
mpirun --np 6 dask-mpi --nthreads 4 \
    --memory-limit 0.15 \
    --interface ib0 \
    --no-scheduler --local-directory $LDIR \
    --scheduler-file=$SCHEDULER
