#!/bin/bash
#SBATCH -J dask-scheduler
#SBATCH -o scheduler.%j.out
#SBATCH -p normal
# #SBATCH --reservation=dssd+TG-OCE170002+2427
#SBATCH -N 1
#SBATCH -n 6
#SBATCH -t 02:00:00

# Writes ~/scheduler.json file in home directory
# Connect with
# >>> from dask.distributed import Client
# >>> client = Client(scheduler_file='~/scheduler.json')

# Setup Environment
module purge
source activate pangeo

# fast SSH global scratch storage
LDIR=/gpfs/flash/users/$USER

# dask-mpi was not compatible with the ibrun mpi launcher on wrangler
# https://portal.tacc.utexas.edu/user-guides/STAMPEDE#launching

# launch jupyterlab
export JUPYTER_RUNTIME_DIR=$WORK
jupyter lab --ip '*' --no-browser --port 8888 \
            --notebook-dir $HOME &

SCHEDULER=$HOME/scheduler.json
rm -f $SCHEDULER
dask-scheduler --scheduler-file $SCHEDULER \
               --local-directory $LDIR &
# if I set the interface, I can't connect to the bokeh
#	       --interface ib0 &

# wait for scheduler to start
while [ ! -f $SCHEDULER ]; do 
    sleep 1
done

# now launch some workers
# save some memory and cores for jupyterlab
dask-worker --memory-limit 0.15 --nthreads 4 --nprocs 5 \
            --local-directory $LDIR \
            --scheduler-file=$SCHEDULER \
            --interface ib0 
