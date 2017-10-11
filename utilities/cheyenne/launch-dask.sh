#!/bin/bash
# set -x
set -e

echo "Launching dask schduler"
s=`qsub launch-dask-scheduler.sh`
sjob=${s%.*}
echo ${s}

workers=${1:-4}
echo "Launching dask workers (${workers})"
for i in $(seq 1 ${workers}); do
    qsub launch-dask-worker.sh
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

sleep 10 # give the scheduler a bit of time to get started

source activate pangeo

echo "Setting up Jupyter Lab"
./setup-jlab.py --log_level=DEBUG --jlab_port=8877 --dash_port=8878 \
    --notebook_dir /glade/p/work/jhamman/pangeo/src/pangeo/notebooks/ \
    --scheduler_file $WORKDIR/scheduler.json
