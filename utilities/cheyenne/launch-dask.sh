#!/bin/bash
set -e

echo "Launching dask scheduler"
s=`qsub -A $PROJECT launch-dask-scheduler.sh`
sjob=${s%.*}
echo ${s}

workers=${1:-4}
echo "Launching dask workers (${workers})"
for i in $(seq 1 ${workers}); do
    qsub -A $PROJECT launch-dask-worker.sh
done

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
    WORKDIR=/glade/scratch/$USER
fi

default=/glade/p/work/$USER
notebook=${2:-$default}
echo "Setting up Jupyter Lab, Notebook dir: ${notebook}"
source activate pangeo
./setup-jlab.py --log_level=DEBUG --jlab_port=8877 --dash_port=8878 \
    --notebook_dir $notebook --scheduler_file $WORKDIR/scheduler.json
