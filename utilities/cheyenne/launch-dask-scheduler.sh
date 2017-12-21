#!/bin/bash
#PBS -N dask-scheduler
#PBS -l select=1:ncpus=36:mpiprocs=9:ompthreads=4:mem=109GB
#PBS -j oe
#PBS -m abe

# Writes ~/scheduler.json file in home directory
# Connect with
# >>> from dask.distributed import Client
# >>> client = Client(scheduler_file='~/scheduler.json')

# Setup Environment
module purge
source activate pangeo

SCHEDULER=/glade/scratch/$USER/scheduler.json
rm -f $SCHEDULER
mpirun --np 9 dask-mpi --nthreads 4 \
    --memory-limit 12e9 \
    --interface ib0 \
    --local-directory /glade/scratch/$USER \
    --scheduler-file=$SCHEDULER
