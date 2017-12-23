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
#PBS -l %(resouce_spec)s
#PBS -l walltime=%(walltime)s
#PBS -j oe
#PBS -m abe

%(base_path)s/dask-worker %(scheduler)s \
    --nprocs %(workers_per_node)d \
    --nthreads %(threads_per_worker)d \
    --memory-limit %(memory)s \
     %(extra)s
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
                 queue='regular',
                 project=None,
                 resouce_spec='select=1:ncpus=36:mem=109GB',
                 workers_per_node=9,
                 threads_per_worker=4,
                 memory='7e9',
                 walltime='00:30:00',
                 interface=None,
                 extra='',
                 **kwargs):
        """ Initialize a PBS Cluster

        Parameters
        ----------
        name : str
            Name of worker jobs. Passed to `$PBS -N` option.
        queue : str
            Destination queue for each worker job. Passed to `#PBS -q` option.
        project : str
            Accounting string associated with each worker job. Passed to
            `#PBS -A` option.
        resource_spec : str
            Request resources and specify job placement. Passed to `#PBS -l`
            option.
        workers_per_node : int
            Number of worker processes per job.
        threads_per_worker : int
            Number of threads per worker.
        memory : str
            Bytes of memory that the worker can use. This can be an integer
            (bytes), float (fraction of total system memory), 'auto', or zero
            for no memory management.
        walltime : str
            Walltime for each worker job.
        interface : str
            Network interface like 'eth0' or 'ib0'.
        extra : str
            Additional arguments to pass to `dask-worker`
        kwargs : dict
            Additional keyword arguments to pass to `LocalCluster`
        """

        if interface:
            host = get_ip_interface(interface)
            extra += ' --interface  %s ' % interface
        else:
            host = socket.gethostname()

        project = project or os.environ.get('PBS_ACCOUNT')
        if not project:
            raise ValueError("Must specify a project like `project='UCLB1234' "
                             "or set PBS_ACCOUNT environment variable")
        self.cluster = LocalCluster(n_workers=0, ip=host, **kwargs)
        self.config = {'name': name,
                       'queue': queue,
                       'project': project,
                       'resouce_spec': resouce_spec,
                       'workers_per_node': workers_per_node,
                       'threads_per_worker': threads_per_worker,
                       'walltime': walltime,
                       'scheduler': self.cluster.scheduler.address,
                       'base_path': dirname,
                       'memory': memory.replace(' ', ''),
                       'extra': extra}
        self.jobs = set()

        logger.debug("Job script: \n %s" % self.job_script())

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
        with self.job_file() as fn:
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
