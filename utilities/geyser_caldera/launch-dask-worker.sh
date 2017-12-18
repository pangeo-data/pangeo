#!/bin/bash
#SBATCH -C geyser
#SBATCH -J dask-worker
#SBATCH -n 1
#SBATCH --mem-per-cpu=24G
#SBATCH -t 11:59:00
#SBATCH -A UCLB0022
#SBATCH -p dav
#SBATCH -e dask-worker.err.%J
#SBATCH -o dask-worker.out.%J


# Setup Environment
source /glade/u/apps/opt/slurm_init/init.sh
module purge
source /glade/u/home/jhamman/anaconda/bin/activate pangeo

export TMPDIR=/glade/scratch/$USER/temp
mkdir -p $TMPDIR

# Setup dask worker
SCHEDULER=/glade/scratch/$USER/dav_scheduler.json

dask-worker --scheduler-file $SCHEDULER \
    --nprocs=1 \
    --nthreads=4 \
    --interface ib0 \
    --memory-limit 25e9 \
    --local-directory $TMPDIR
