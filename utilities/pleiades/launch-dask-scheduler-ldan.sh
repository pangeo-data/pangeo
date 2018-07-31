#!/bin/bash
#PBS -N dask-sched
#PBS -W group_list=g26209
#PBS -l select=1:ncpus=16:mpiprocs=4
#PBS -l walltime=7:59:00
#PBS -q ldan
#PBS -j oe
#PBS -m abe

export LANG="en_US.utf8"
export LANGUAGE="en_US.utf8"
export LC_ALL="en_US.utf8"

# Connect with
# >>> from dask.distributed import Client
# >>> client = Client(scheduler_file='~/scheduler.json')

# Setup Environment
module purge
source activate pangeo

SCHEDULER=/nobackup/$USER/dask/scheduler.json
rm -f $SCHEDULER
mpirun --np 4 dask-mpi --nthreads 4 \
    --memory-limit 0.24 \
    --interface ib0 \
    --local-directory /nobackup/$USER/dask \
    --scheduler-file=$SCHEDULER
