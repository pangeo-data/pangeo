#!/bin/bash
set -e

export LANG="en_US.utf8"
export LANGUAGE="en_US.utf8"
export LC_ALL="en_US.utf8"

echo "Launching dask scheduler"
s=`qsub launch-dask-scheduler-ldan.sh`
sjob=${s}
echo ${s}

workers=${1:-4}
echo "Launching dask workers (${workers})"
qsub -J 1-$workers launch-dask-worker-ldan.sh

qstat ${sjob}

# block until the scheduler job starts
while true; do
    status=`qstat ${sjob} | tail -n 1`
    echo ${status}
    if [[ ${status} =~ " R " ]]; then
        break
    fi
    sleep 1
done

if [[ -z $WORKDIR ]]; then
    WORKDIR=/nobackup/$USER/dask
fi

# doesn't work on ldan
#default=$HOME
default=/pleiades/u/$USER
notebook=${2:-$default}
echo "Setting up Jupyter Lab, Notebook dir: ${notebook}"
source activate pangeo
./setup-jlab.py --log_level=DEBUG --jlab_port=8877 --dash_port=8878 \
    --notebook_dir $notebook --scheduler_file $WORKDIR/scheduler.json \
    --hostname pfe
