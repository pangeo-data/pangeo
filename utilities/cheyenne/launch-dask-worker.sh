#!/bin/bash
#PBS -N dask-worker
#PBS -q economy
#PBS -l select=1:ncpus=36:mpiprocs=9:ompthreads=4:mem=109GB
#PBS -l walltime=11:59:00
#PBS -j oe
#PBS -m abe

# Setup Environment
module purge
source activate pangeo

# Setup dask worker
SCHEDULER=/glade/scratch/$USER/scheduler.json
mpirun --np 9 dask-mpi --nthreads 4 \
    --memory-limit 12e9 \
    --interface ib0 \
    --no-scheduler --local-directory /glade/scratch/$USER \
    --scheduler-file=$SCHEDULER
