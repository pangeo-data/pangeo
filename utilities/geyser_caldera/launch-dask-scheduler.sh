#!/bin/bash
#SBATCH -C geyser
#SBATCH -J dask-scheduler
#SBATCH -n 10
#SBATCH --mem-per-cpu=50G
#SBATCH -t 11:59:00
#SBATCH -A UCLB0022
#SBATCH -p dav
#SBATCH -e dask-scheduler.err.%J
#SBATCH -o dask-scheduler.out.%J

# Writes ~/scheduler.json file in home directory
# Connect with
# >>> from dask.distributed import Client
# >>> client = Client(scheduler_file='/glade/scratch/$USER/scheduler.json')
export LANG="en_US.utf8"
export LANGUAGE="en_US.utf8"
export LC_ALL="en_US.utf8"

echo "launching scheduler"

# Setup Environment
source /glade/u/apps/opt/slurm_init/init.sh
module purge
# module load openmpi-slurm/3.0.0 ?
source /glade/u/home/jhamman/anaconda/bin/activate pangeo

export TMPDIR=/glade/scratch/$USER/temp
mkdir -p $TMPDIR

SCHEDULER=/glade/scratch/$USER/dav_scheduler.json
rm -f $SCHEDULER

# setup scheduler
dask-scheduler --scheduler-file $SCHEDULER --local-directory $TMPDIR &
