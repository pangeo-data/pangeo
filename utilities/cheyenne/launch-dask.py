#!/usr/bin/env python
from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import subprocess
import re
import time
import logging
import socket
from contextlib import contextmanager
from textwrap import dedent

import click
from dask.distributed import Client
from distributed.utils import tmpfile


WORKER_TEMPLATE = '''\
    #!/bin/bash
    #PBS -N dask-worker
    #PBS -l select=1:ncpus=36:mpiprocs=9:ompthreads=4:mem=109GB
    #PBS -j oe

    # Setup Environment
    module purge
    source activate pangeo

    # Setup dask worker
    SCHEDULER=/glade/scratch/$USER/scheduler.json
    mpirun --np 9 dask-mpi --nthreads 4 \
        --memory-limit 12e9 \
        --interface ib0 \
        --no-scheduler --local-directory /glade/scratch/$USER \
        --scheduler-file=$SCHEDULER
    '''

SCHEDULER_TEMPLATE = '''\
    #!/bin/bash
    #PBS -N dask-scheduler
    #PBS -l select=1:ncpus=36:mpiprocs=9:ompthreads=4:mem=109GB
    #PBS -j oe

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
    '''

USER = os.environ.get("USER")
DEFAULT_WORKDIR = os.path.join("/glade", "scratch", USER)
DEFAULT_NOTEBOOK_DIR = os.path.join("/glade", "p", "work", USER)


@click.command()
@click.option("--project", default=os.environ.get("PROJECT"),
              help="Specify a project id for the case (optional). Used for "
                   "accounting when on a batch system. The default is "
                   "user-specified environment variable PROJECT")
@click.option("--nnodes", default=0, type=int,
              help="Number of client nodes to launch")
@click.option("--walltime", default="01:00:00",
              help="Set the wallclock limit for all nodes.")
@click.option("--queue", default="economy",
              help="Set the queue to use for submitted jobs.")
@click.option("--workdir", default=DEFAULT_WORKDIR,
              help="Set the working diirectory")
@click.option("--notebookdir", default=DEFAULT_NOTEBOOK_DIR,
              help="Set the notebook diirectory")
@click.option("--notebook-port", type=int, default=8877,
              help="Set the notebook tcp/ip port")
@click.option("--dashboard-port", type=int,
              default=8878, help="Set the notebook tcp/ip port")
@click.option("--scheduler-file", default=None,
              help='Filename to an existing JSON file including encoded '
                   'scheduler information.')
def main(project, nnodes, walltime, queue, workdir, notebookdir, notebook_port,
         dashboard_port, scheduler_file):

    if project is None:
        raise ValueError('project number was not specified')

    jobids = []
    if scheduler_file is None:
        with job_file(SCHEDULER_TEMPLATE) as scheduler_job_file:
            scheduler_jobid = launch_job(scheduler_job_file, project, walltime,
                                         queue)
            jobids.append(scheduler_jobid)

    with job_file(WORKER_TEMPLATE) as worker_job_file:
        for i in range(nnodes):
            jobids.append(launch_job(worker_job_file, project, walltime,
                                     queue))

    if scheduler_file is not None:
        return

    wait = True
    while wait:
        time.sleep(5)
        proc = subprocess.Popen("qstat {} ".
                                format(scheduler_jobid),
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                shell=True)

        output, errput = proc.communicate()
        output = output.decode('utf-8')
        proc.wait()
        if ' R ' in output:
            logger.info("jobid {} started".format(scheduler_jobid))
            wait = False
        if ' Q ' in output:
            logger.info("jobid {} in queue".format(scheduler_jobid))

    setup_jlab(os.path.join(workdir, "scheduler.json"),
               notebook_port, dashboard_port, notebookdir, "cheyenne.ucar.edu")


@contextmanager
def job_file(lines):
    """ Write job submission script to temporary file """
    with tmpfile(extension='sh') as fn:
        with open(fn, 'w') as f:
            f.write(dedent(lines))
        yield fn


def launch_job(jobname, project, walltime, job_queue):

    logger.info("submit job {}".format(jobname))

    cmd = "qsub -A {} -l walltime={} -q {} {}".format(project, walltime,
                                                      job_queue, jobname)

    logger.debug(cmd)

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            shell=True)

    output, errput = proc.communicate()

    stat = proc.wait()
    if stat != 0:
        print("ERROR stat {}".format(stat))

    search_jobid = re.search("^(\S+)$", output.decode('utf-8'))
    jobid = search_jobid.group(1)
    return jobid


def start_jlab(dask_scheduler, host=None, port='8888', notebook_dir=''):
    cmd = ['jupyter', 'lab', '--ip', str(host),
           '--no-browser', '--port', str(port),
           '--notebook-dir', notebook_dir]

    proc = subprocess.Popen(cmd)
    dask_scheduler.jlab_proc = proc


def get_logger(log_level):
    ch = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(' - '.join(
        ["%(asctime)s", "%(name)s", "%(levelname)s", "%(message)s"]))
    ch.setFormatter(formatter)
    logger = logging.getLogger(__file__)
    logger.setLevel(log_level)
    ch.setLevel(log_level)
    logger.addHandler(ch)
    return logger


def setup_jlab(scheduler_file, jlab_port, dash_port, notebook_dir,
               hostname):

    assert os.path.isfile(scheduler_file)

    logger.info('getting client with scheduler file: %s' % scheduler_file)
    client = Client(scheduler_file=scheduler_file, timeout=60)
    logger.debug('Client: %s' % client)

    logger.debug('Getting hostname where scheduler is running')
    host = client.run_on_scheduler(socket.gethostname)
    logger.info('host is %s' % host)

    logger.info('Starting jupyter lab on host')
    client.run_on_scheduler(start_jlab, host=host, port=jlab_port,
                            notebook_dir=notebook_dir)
    logger.debug('Done.')

    print('Run the following command from your local machine:')
    print(f'ssh -N -L {jlab_port}:{host}:{jlab_port} '
          f'-L {dash_port}:{host}:8787 {USER}@{hostname}')
    print('Then open the following URLs:')
    print(f'\tJupyter lab: http://localhost:{jlab_port}')
    print(f'\tDask dashboard: http://localhost:{dash_port}', flush=True)


logger = get_logger("DEBUG")

if __name__ == "__main__":
    main()
