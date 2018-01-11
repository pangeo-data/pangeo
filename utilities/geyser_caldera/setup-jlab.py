#!/usr/bin/env python
from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import socket
import subprocess
import logging

import click

from dask.distributed import Client


def start_jlab(dask_scheduler, host=None, port='8888', notebook_dir=''):
    cmd = ['jupyter', 'lab', '--ip', host,
           '--no-browser', '--port', port,
           '--notebook-dir', notebook_dir]
    print(cmd)
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


@click.command()
@click.option('--scheduler_file', default='scheduler.json',
              show_default=True, help='Dask-distributed scheduler file')
@click.option('--jlab_port', default='8888', show_default=True,
              help='port to forward jupyter lab to')
@click.option('--dash_port', default='8787', show_default=True,
              help='port to forward dask dashboard to')
@click.option('--notebook_dir', default='', show_default=True,
              help='The directory to use for notebooks and kernels.')
@click.option('--hostname', default='cheyenne.ucar.edu', show_default=True,
              help='public facing hostname')
@click.option('--log_level', default='INFO', show_default=True,
              help='logging level, useful for debugging')
def cli(scheduler_file, jlab_port, dash_port, notebook_dir,
        hostname, log_level):
    logger = get_logger(log_level)

    logger.info('getting client with scheduler file: %s' % scheduler_file)
    client = Client(scheduler_file=scheduler_file, timeout=30)
    logger.debug('Client: %s' % client)

    logger.debug('Getting hostname where scheduler is running')
    host = client.run_on_scheduler(socket.gethostname)
    logger.info('host is %s' % host)

    logger.info('Starting jupyter lab on host')
    client.run_on_scheduler(start_jlab, host=host, port=jlab_port,
                            notebook_dir=notebook_dir)
    logger.debug('Done.')

    user = os.environ['USER']
    print('Run the following command from your local machine:')
    print(f'ssh -N -L {jlab_port}:{host}:{jlab_port} '
          f'-L {dash_port}:{host}:8787 {user}@{hostname}')
    print('Then open the following URLs:')
    print(f'\tJupyter lab: http://localhost:{jlab_port}')
    print(f'\tDask dashboard: http://localhost:{dash_port}', flush=True)


if __name__ == '__main__':
    cli()
