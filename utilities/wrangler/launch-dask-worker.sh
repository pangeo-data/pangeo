#!/bin/basH
#SBATCH -J dask-worker
#SBATCH -o worker.%j.out
#SBATCH -p normal
# #SBATCH --reservation=dssd+TG-OCE170002+2427
#SBATCH -N 1
#SBATCH -n 6
#SBATCH -t 02:00:00

# Setup Environment
module purge
source activate pangeo

# fast SSH global scratch storage
LDIR=/gpfs/flash/users/$USER

SCHEDULER=$HOME/scheduler.json
dask-worker --memory-limit 0.15 --nthreads 4 --nprocs 6 \
            --local-directory $LDIR \
            --scheduler-file=$SCHEDULER \
            --interface ib0 
