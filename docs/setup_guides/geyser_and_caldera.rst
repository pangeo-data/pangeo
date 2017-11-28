Getting Started with Dask on Geyser and Caldera
===============================================

This setup guide provides instructions for setting up a "local cluster" on
Geyser or Caldera. This creates a “cluster” of a scheduler and workers running
on a single Geyser or Caldera node. Because these nodes have a large number of
cores and a large amount of memory, this can be a simple alternative to the full
distributed cluster that can be run on Cheyenne.

Begin by following the first two steps from the
`Getting Started with Dask on Cheyenne <setup_guides/cheyenne.html>`_ page:

1. Install conda and creating an environment
2. Configure Jupyter

Once you have Conda and Jupyter configured. Load a few python modules and start
a Jupyter session on Geyser or Caldara using the ``execgy`` or ```execca``
utilities, respectively.

.. code:: bash

    module load python all-python-libs
    export DAV_CORES=8  # request 8 cores
    execgy start-notebook  # run the start-notebook command on geyser

after a brief minute, you should see something like:

::

    Requesting 8 core(s) to geyser queue,
    to submit start-notebook the usage is to be charged into UCLB0022
    running

    bsub -Is -q geyser -n8 -PUCLB0022 -W24:00 "start-notebook"

    please wait..

    Job <552080> is submitted to queue <geyser>.
    <<Waiting for dispatch ...>>
    Logging this session in /glade/scratch/username/.jupyter-notebook/log.20171128T001004


    Run the following command on your desktop or laptop:
    ssh -N -l username -L 8888:geyser08-ib:8888 yellowstone.ucar.edu

    Log in with your token (there will be no prompt). Then
    open a browser and go to http://localhost:8888.

From your local machine, run the ssh command and open the url to the notebook
server (http://localhost:8888).

.. note::

   Geyser and Caldra are shared systems. If you are going to use multiple cores,
   it is a best practice to request multiple cores on the system via the
   ``DAV_CORES`` environment variable.

Finally, from within the notebook you'll be using, use the following snippit to
start a ``LocalCluster`` and and connect dask to it.

.. code:: python

    from distributed import LocalCluster, Client

    cluster = LocalCluster(processes=True, n_workers=4, threads_per_worker=4)
    client = Client(cluster)
