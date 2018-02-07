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

    execgy  # or execca

after a brief minute, you should see something like:

::

    mem =
    amount of memory is default
    setting x forwarding for cheyenne6.ucar.edu:16.0
    Submitting interactive job to slurm using account uclb0022 ...

    submit  cmd is
    salloc  -C geyser   -N 1  -n 1 -t 6:00:00 -p dav --account=uclb0022 srun --pty --export=HOME=/glade/u/home/username,PATH=/bin:/usr/bin,TERM=xterm-256color,SHELL=/bin/bash,DISPLAY=cheyenne6.ucar.edu:16.0,XAUTHORITY=/glade2/scratch2/username/.xauth.43241  /bin/bash -c "export DISPLAY=cheyenne6.ucar.edu:16.0; exec /bin/bash "
    salloc: Pending job allocation 147402
    salloc: job 147402 queued and waiting for resources
    salloc: job 147402 has been allocated resources
    salloc: Granted job allocation 147402
    salloc: Waiting for resource configuration
    salloc: Nodes geyser01 are ready for job

Now you can load the python and jupyter modules and run the ``start-notebook`` command:

.. code:: bash

    module load python pyzmq/16.0.2 tornado/4.4.3
    module load jupyter
    start-notebook  # run the start-notebook command on geyser

after a brief moment, you should see something like:

::

    ssh -N -l username -L 8888:geyser08-ib:8888 geyser08.ucar.edu

From your local machine, run the ssh command and open the url to the notebook
server (http://localhost:8888).

Finally, from within the notebook you'll be using, use the following snippit to
start a ``LocalCluster`` and and connect dask to it.

.. code:: python

    from pangeo import SlurmCluster
    from distributed import Client

    cluster = SlurmCluster(project='UCLB0022')
    client = Client(cluster)

The SlurmCluster controls the dask workers and you can either manually scale up/down
the cluster using the ``scale_up`` / ``scale_down`` methods:

.. code:: python

    cluster.scale_up(4)
    # ...
    cluster.scale_down(4)

Or you can instruct the cluster to adapt to the computational load:

.. code:: python

    cluster.adapt()
