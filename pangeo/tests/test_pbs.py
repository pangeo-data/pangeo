from time import time, sleep

import pytest

from dask.distributed import Client
from distributed.deploy.adaptive import Adaptive
from distributed.utils_test import loop
from pangeo import PBSCluster


def test_basic(loop):
    with PBSCluster(walltime='00:02:00', threads_per_worker=2, memory='7e9',
                    interface='ib0', loop=loop) as cluster:
        with Client(cluster) as client:
            workers = cluster.start_workers(2)
            future = client.submit(lambda x: x + 1, 10)
            assert future.result() == 11
            assert cluster.jobs

            info = client.scheduler_info()
            w = list(info['workers'].values())[0]
            assert w['memory_limit'] == 7e9
            assert w['ncores'] == 2

            cluster.stop_workers(workers)

            start = time()
            while len(client.scheduler_info()['workers']) > 0:
                sleep(0.100)
                assert time() < start + 10

            assert not cluster.jobs


def test_adaptive(loop):
    with PBSCluster(walltime='00:02:00', loop=loop) as cluster:
        adapt = Adaptive(cluster.cluster.scheduler, cluster, startup_cost=5)
        with Client(cluster) as client:
            future = client.submit(lambda x: x + 1, 10)
            assert future.result() == 11

            assert cluster.jobs

            del future

            start = time()
            while len(client.scheduler_info()['workers']) > 0:
                sleep(0.100)
                assert time() < start + 10


def test_errors(loop):
    with pytest.raises(ValueError) as info:
        PBSCluster()

    assert 'project=' in str(info.value)
