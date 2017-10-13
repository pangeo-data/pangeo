#!/bin/bash
#PBS -N dask-scheduler
#PBS -q economy
#PBS -A UCLB0022
#PBS -l select=1:ncpus=36:mpiprocs=6:ompthreads=6
#PBS -l walltime=11:59:00
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
mpirun --np 6 dask-mpi --nthreads 6 --memory-limit 22e9 --interface ib0 \
    --local-directory /glade/scratch/$USER --scheduler-file=$SCHEDULER
