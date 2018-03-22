#!/bin/bash

#SBATCH --exclusive
#SBATCH -N 1
#SBATCH -J dask-sched
#SBATCH --time=6:00:00

# Writes ~/scheduler.json file in home directory
# Connect with
# >>> from dask.distributed import Client
# >>> client = Client(scheduler_file='~/scheduler.json')

# Setup Environment
source mod_env_setup.sh

LDIR=/local/$USER
rm -rf $LDIR

SCHEDULER=$HOME/scheduler.json
rm -f $SCHEDULER
mpirun --np 6 dask-mpi --nthreads 4 \
    --memory-limit 0.15 \
    --local-directory $LDIR \
    --scheduler-file=$SCHEDULER
    # this makes the bokeh not work
    #--interface ib0 \
