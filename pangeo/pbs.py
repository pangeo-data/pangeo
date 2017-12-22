from contextlib import contextmanager
import logging
import os
import socket
import subprocess
import sys

from distributed import LocalCluster
from distributed.utils import tmpfile, get_ip_interface

template = """
#!/bin/bash
#PBS -N %(name)s
#PBS -q %(queue)s
#PBS -A %(project)s
#PBS -l select=1:ncpus=%(threads_per_worker)d:mpiprocs=1:ompthreads=1
#PBS -l walltime=%(walltime)s
#PBS -j oe
#PBS -m abe

%(base_path)s/dask-worker %(scheduler)s --nthreads %(threads_per_worker)d --memory-limit %(memory)s --name $PBS_JOBNAME-$PBS_JOBID-$PBS_TASKNUM %(extra)s
"""


logger = logging.getLogger(__name__)


dirname = os.path.dirname(sys.executable)


class PBSCluster(object):
    """ Launch Dask on a PBS cluster

    Examples
    --------
    >>> from pangeo import PBSCluster
    >>> cluster = PBSCluster(project='...')
    >>> cluster.start_workers(10)  # this may take a few seconds to launch

    >>> from dask.distributed import Client
    >>> client = Client(cluster)

    This also works with adaptive clusters.  This automatically launches and
    kill workers based on load.

    >>> from distributed.deploy import Adaptive
    >>> adapt = Adaptive(cluster.cluster.scheduler, cluster)
    """
    def __init__(self,
                 name='dask',
                 q='regular',
                 project='UCLB0022',  # is there an environment variable I can use?
                 threads_per_worker=6,
                 memory='7GB',
                 walltime='00:30:00',
                 interface=None,
                 extra='',
                 scheduler_file=os.path.expanduser('~/scheduler.json'),
                 **kwargs):
        if interface:
            host = get_ip_interface(interface)
            extra += '--interface ' + interface
        else:
            host = socket.gethostname()
        self.cluster = LocalCluster(n_workers=0, ip=host, **kwargs)
        self.config = {'name': name,
                       'queue': q,
                       'project': project,
                       'threads_per_worker': threads_per_worker,
                       'walltime': walltime,
                       'scheduler': self.cluster.scheduler.address,
                       'base_path': dirname,
                       'memory': memory.replace(' ', ''),
                       'extra': extra}
        self.jobs = set()

    def job_script(self):
        return template % self.config

    @contextmanager
    def job_file(self):
        """ Write job submission script to temporary file """
        with tmpfile(extension='sh') as fn:
            with open(fn, 'w') as f:
                f.write(self.job_script())

            yield fn

    def start_workers(self, n=1):
        """ Start workers and point them to our local scheduler """
        with self.job_script() as fn:
            outs = self._calls([['qsub', fn]] * n)
            jobs = [out.decode().split('.')[0] for out in outs]
        self.jobs.update(jobs)
        return jobs

    @property
    def scheduler_address(self):
        return self.cluster.scheduler_address

    def _calls(self, cmds):
        """ Call a command using subprocess.communicate

        This centralzies calls out to the command line, providing consistent
        outputs, logging, and an opportunity to go asynchronous in the future

        Parameters
        ----------
        cmd: List(List(str))
            A list of commands, each of which is a list of strings to hand to
            subprocess.communicate

        Examples
        --------
        >>> self._calls([['ls'], ['ls', '/foo']])

        Returns
        -------
        The stdout result as a string
        Also logs any stderr information
        """
        logger.debug("Submitting the following calls to command line")
        for cmd in cmds:
            logger.debug(' '.join(cmd))
        procs = [subprocess.Popen(cmd,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
                 for cmd in cmds]

        result = []
        for proc in procs:
            out, err = proc.communicate()
            if err:
                logger.error(err.decode())
            result.append(out)
        return result

    def _call(self, cmd):
        """ Singular version of _calls """
        return self._calls([cmd])[0]

    def stop_workers(self, jobs):
        if not jobs:
            return
        self._call(['qdel'] + list(jobs))
        self.jobs -= set(jobs)

    def scale_up(self, n, **kwargs):
        return self.start_workers(n - len(self.jobs))

    def scale_down(self, workers):
        pass
        # needs https://github.com/dask/distributed/pull/1659
        # names = [self.cluster.scheduler.worker_info[w]['name'] for w in workers]
        # job_ids = {name.split('-')[-2] for name in names}
        # self.stop_workers(job_ids)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.stop_workers(self.jobs)
        self.cluster.__exit__(type, value, traceback)
