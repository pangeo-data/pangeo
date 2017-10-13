#!/bin/bash
#PBS -N dask-worker
#PBS -q economy
#PBS -A UCLB0022
#PBS -l select=1:ncpus=36:mpiprocs=6:ompthreads=6
#PBS -l walltime=11:59:00
#PBS -j oe
#PBS -m abe

# Setup Environment
module purge
source activate pangeo

# Setup dask worker
SCHEDULER=/glade/scratch/$USER/scheduler.json
mpirun --np 6 dask-mpi --nthreads 6 --memory-limit 22e9 --interface ib0 \
    --no-scheduler --local-directory /glade/scratch/$USER \
    --scheduler-file=$SCHEDULER
