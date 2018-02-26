#!/bin/bash
#PBS -N dask-worker
#PBS -W group_list=g26209
#PBS -l select=1:ncpus=16:mpiprocs=4
#PBS -q ldan
#PBS -l walltime=7:59:00
#PBS -j oe
#PBS -m abe

export LANG="en_US.utf8"
export LANGUAGE="en_US.utf8"
export LC_ALL="en_US.utf8"

# Setup Environment
module purge
source activate pangeo

# Setup dask worker
SCHEDULER=/nobackup/$USER/dask/scheduler.json
mpirun --np 4 dask-mpi --nthreads 4 \
    --memory-limit 0.24 \
    --interface ib0 \
    --no-scheduler --local-directory /nobackup/$USER/dask \
    --scheduler-file=$SCHEDULER
