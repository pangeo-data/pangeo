#!/bin/bash
set -e

# Setup Environment
module load slurm
source activate pangeo

export LANG="en_US.utf8"
export LANGUAGE="en_US.utf8"
export LC_ALL="en_US.utf8"

default=/glade/p/work/$USER
notebook=${2:-$default}

if [[ -z $WORKDIR ]]; then
    WORKDIR=/glade/scratch/$USER
fi

echo "Launching dask scheduler"
sjob=$(sbatch --parsable launch-dask-scheduler.sh)
echo ${sjob}

workers=${1:-4}
echo "Launching dask workers (${workers})"
for i in $(seq 1 ${workers}); do
    sbatch launch-dask-worker.sh
done

# Print the queue once (with header)
squeue -u ${USER} -j ${sjob}

# block until the scheduler job starts
while true; do
    squeue -h -u ${USER} -j ${sjob} -t RUNNING
    status=`squeue -h -u ${USER} -j ${sjob} -t RUNNING`
    echo ${status}
    if [[ ! -z ${status} ]]; then
        break
    fi
    sleep 1
done

echo "Setting up Jupyter Lab, Notebook dir: ${notebook}"
./setup-jlab.py --log_level=DEBUG --jlab_port=8877 --dash_port=8878 \
    --notebook_dir $notebook --scheduler_file $WORKDIR/dav_scheduler.json
