.. _hpc:

Getting Started with Pangeo on HPC
==================================

This tutorial covers how to set up an environment to run Pangeo on High
Performance Computing (HPC) systems. In particular it covers the following:

1. Install `conda`_ and creating an environment
2. Configure `Jupyter`_
3. Launch `Dask`_ with a job scheduler
4. Launch a `Jupyter`_ server for your job
5. Connect to `Jupyter`_ and the `Dask`_ dashboard from your personal computer

Although the examples on this page were developed using NCAR's `Cheyenne`_ super
computer, the concepts here should be generally applicable to typical HPC systems.
This document assumes that you already have an access to an HPC like Cheyenne,
and are comfortable using the command line. It may be necessary to work with your
system administrators to properly configure these tools for your machine.

You should log into your HPC system now.

Installing a software environment
---------------------------------

After you have logged into your HPC system, download and install Miniconda:

::

    wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
    chmod +x Miniconda3-latest-Linux-x86_64.sh
    ./Miniconda3-latest-Linux-x86_64.sh

This contains a self-contained Python environment that we can manipulate
safely without requiring the involvement of IT. It also allows you to
create isolated software environments so that we can experiment in the
future safely.

Create a new conda environment for our pangeo work:

::

    conda create -n pangeo -c conda-forge \
        python=3.6 xarray \
        jupyterlab nbserverproxy \
        dask distributed mpi4py dask-jobqueue

.. note::

   Depending on your application, you may choose to add additional conda
   packages to this list.

Activate this environment

::

    source activate pangeo

Your prompt should now look something like this (note the pangeo environment name):

::

    (pangeo) $

And if you ask where your Python command lives, it should direct you to
somewhere in your home directory:

::

    (pangeo) $ which python
    /home/username/miniconda3/envs/pangeo/bin/python

Configure Jupyter
-----------------

(If you don't plan to use Jupyter notebooks then you can safely skip
this section.)

.. note::

   When using recent Jupyter iteration the following section can be replaced by simply invoking the command::
   
      jupyter notebook --generate-config
      jupyter notebook password

   And entering desired password.

Jupyter notebook servers include a password for security. We're going to
setup a password for ourselves. First we generate the Jupyter config
file and install a notebook proxy service:

::

    jupyter notebook --generate-config
    jupyter serverextension enable --py nbserverproxy

This created a file in ``~/.jupyter/jupyter_notebook_config.py``. If you
open that file and search for "password", you'll see a line like the
following:

::

    #c.NotebookApp.password = u''

The instructions in the comments of the config file tell you to generate
a hashed password by entering the following commands:

::

    $ ipython

.. code:: python

    In [1]: from notebook.auth import passwd; passwd()
    Enter password:

You can enter a password of your choice, and it will return to you a
encoded password. I entered "password" (do not do this) and go the following
output:

.. code:: python

    Out[1]: 'sha1:69a76df803b9:99ca27341563cd85ba4e78684128e1f4ad2d8d0d'

Copy that string into your ``jupyter_notebook_config.py`` config file

::

    c.NotebookApp.password = u'sha1:69a76df803b9:99ca27341563cd85ba4e78684128e1f4ad2d8d0d'

For security reasons, we recommend making sure your ``jupyter_notebook_config.py``
is readable only by you. For more information on and other methods for
securing Jupyter, check out
`Securing a notebook server <http://jupyter-notebook.readthedocs.io/en/stable/public_server.html#securing-a-notebook-server>`__
in the Jupyter documentation.

::

    chmod 400 ~/.jupyter/jupyter_notebook_config.py

Finally, we may want to configure dask's dashboard to forward through Jupyter.
This can be done by editing the dask distributed config file, e.g.:
``.config/dask/distributed.yaml``. In this file, set:

.. code:: python

    diagnostics-link: "/proxy/{port}/status"

------------

From here, we have two options. Option 1 will start a Jupyter Notebook server
and manage dask using the `dask-jobqueue`_ package. Option 2 will start a dask
cluster using `dask-mpi` and will run a Jupyter server as part of the dask cluster.
We generally recommend starting with Option 1, especially if you will be working
interactively, unless you have a reason for managing the job submission scripts
on your own. Users that will be using dask in batch-style workflows may prefer
Option 2.

Deploy Option 1: Jupyter + dask-jobqueue
----------------------------------------

Start a Jupyter Notebook Server
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Now that we have Jupyter configured, we can start a notebook server. In many
cases, your system administrators will want you to run this notebook server in
an interactive session on a compute node. This is not universal rule, but it is
one we'll follow for this tutorial.

In our case, the Cheyenne super computer uses the PBS job scheduler, so typing:

::

    (pangeo) $ qsub -I -l select=1:ncpus=4 -l walltime=03:00:00 -q regular

This will get us an interactive job on the `regular` queue for three hours. You
may not see the `pangeo` environment anymore in your prompt, in this case, you
will want to reactivate it.

::

    source activate pangeo

From here, we can start jupyter. The Cheyenne computer administrators have
developed a `start-notebook <https://www2.cisl.ucar.edu/resources/computational-systems/cheyenne/software/jupyter-and-ipython#notebook>`__
utility that wraps the following steps into a single execution. You should
check with your system administrators to see if they have something similar.
If not, you'll need to take the following steps:

Copy this line into your terminal. It will echo a command you'll want to use
later.

::

    (pangeo) $ echo "ssh -N -L 8888:`hostname`:8888 $USER@cheyenne.ucar.edu"
    ssh -N -L 8888:r8i4n0:8888 username@cheyenne.ucar.edu

Now we can launch the notebook server:

::

    (pangeo) $ jupyter lab --no-browser --ip=`hostname` --port=8888
    ...
    [I 13:36:52.321 LabApp] The Jupyter Notebook is running at:
    [I 13:36:52.321 LabApp] http://r8i4n0:8888/
    [I 13:36:52.321 LabApp] Use Control-C to stop this server and shut down all kernels (twice to skip confirmation).

Now, connect to the server using an ssh tunnel from your local machine
(this could be your laptop or desktop).

::

    $ ssh -N -L 8888:r8i4n0:8888 username@cheyenne.ucar.edu

You'll want to change the details in the command above but the basic idea is
that we're passing the port 8888 from the compute node `r8i4n0` to our
local system. Now open http://localhost:8888 on your local machine, you should
find a jupyter server running!

Launch Dask with dask-jobqueue
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Most HPC systems use a job-scheduling system to manage job submissions and
executions among many users. The `dask-jobqueue`_ package is designed to help
dask interface with these job queuing systems. Usage is quite simple and can be
done from within your Jupyter Notebook:

.. code:: python

    from dask_jobqueue import PBSCluster

    cluster = PBSCluster(cores=36,
                         processes=18, memory="6GB",
                         project='UCLB0022',
                         queue='premium',
                         resource_spec='select=1:ncpus=36:mem=109G',
                         walltime='02:00:00')
    cluster.scale(18)

    from dask.distributed import Client
    client = Client(cluster)

The `scale()` method submits a batch of jobs to the job queue system
(in this case PBS). Depending on how busy the job queue is, it can take a few
minutes for workers to join your cluster. You can usually check the status of
your queued jobs using a command line utility like `qstat`. You can also check
the status of your cluster from inside your Jupyter session:

.. code:: python

    print(client)

For more examples of how to use
`dask-jobqueue`_, refer to the
`package documentation <http://dask-jobqueue.readthedocs.io>`__.

Deploy Option 2: Jupyter + dask-mpi
-----------------------------------

This approach allows you to deploy dask directly using batch jobs on your HPC
machine.

The MPI library is only used to distribute the dask-workers across the
cluster. MPI is **NOT** used for communication by dask.

.. note::

   The following scripts and procedures have been packed into a convenient wrapper
   script ``launch-dask.sh``. It and its supporting utilities can be found in the
   `pangeo Github reposository <https://github.com/pangeo-data/pangeo/tree/master/utilities/cheyenne>`__.

   The usage of this script is quite simple:

   .. code:: bash

       ./launch-dask.sh ${N_WORK_NODES}

   where ``N_WORK_NODES`` is the number of nodes you want to add to the cluster
   beyond the one that is automatically added for the scheduler. Once this command
   has been run, and after a moment for the jobs to work their way through the queue,
   it will print something like:

   .. code:: bash

       Run the following command from your local machine:
       ssh -N -L 8888:r7i3n13:8888 -L 8787:r7i3n13:8787 username@cheyenne.ucar.edu
       Then open the following URLs:
           Jupyter lab: http://localhost:8888
           Dask dashboard: http://localhost:8787

   It may be necessary to modify the included scripts to use different PBS
   project number, conda environment, or notebook directory.

*The remainder of this section is left here for completeness but for most users,
the ``launch-dask.sh`` script should be enough to get started.*

------------

Copy and paste the following text into a file, dask.sh:

.. code:: bash

    #!/bin/bash
    #PBS -N sample
    #PBS -q economy
    #PBS -A UCLB0022
    #PBS -l select=2:ncpus=36:mpiprocs=6
    #PBS -l walltime=01:00:00
    #PBS -j oe
    #PBS -m abe

    # Qsub template for UCAR CHEYENNE
    # Scheduler: PBS

    # This writes a scheduler.json file into your home directory
    # You can then connect with the following Python code
    # >>> from dask.distributed import Client
    # >>> client = Client(scheduler_file='~/scheduler.json')

    rm -f scheduler.json
    mpirun --np 12 dask-mpi \
        --nthreads 6 \
        --memory-limit 24e9 \
        --interface ib0

This script asks for two nodes with 36 cores each. It breaks up each
node into 6 MPI processes, each of which gets 6 cores and 24GB of RAM
each. You can tweak the numbers above if you like, but you'll have to
match some constraints in the PBS directives on the top and the
``mpirun`` keywords on the bottom.

Submit this script to run on the cluster with ``qsub``

::

    qsub dask.sh

And track its progress with ``qstat``

::

    $ qstat -u $USER

    chadmin1:
                                                                Req'd  Req'd   Elap
    Job ID          Username Queue    Jobname    SessID NDS TSK Memory Time  S Time
    --------------- -------- -------- ---------- ------ --- --- ------ ----- - -----
    1681778.chadmin username regular  sample      27872   2 144    --  00:20 R 00:01

When this job runs it places a ``scheduler.json`` file in your home
directory. This contains the necessary information to connect to this
cluster from anywhere in the network. We'll do that now briefly from the
login node. In the next section we'll set up a Jupyter notebook server
on your allocation.

::

    $ ipython

.. code:: python

    from dask.distributed import Client
    client = Client(scheduler_file='scheduler.json')
    client

.. code:: python

    Out[3]: <Client: scheduler='tcp://10.148.0.92:8786' processes=11 cores=66>

Launch and connect to Jupyter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

From your same session on the login node, run the following code:

.. code:: python

    from dask.distributed import Client
    client = Client(scheduler_file='scheduler.json')

    import socket
    host = client.run_on_scheduler(socket.gethostname)

    def start_jlab(dask_scheduler):
        import subprocess
        proc = subprocess.Popen(['jupyter', 'lab', '--ip', host, '--no-browser'])
        dask_scheduler.jlab_proc = proc

    client.run_on_scheduler(start_jlab)

    print("ssh -N -L 8888:%s:8888  -L 8787:%s:8787 cheyenne.ucar.edu" % (host, host))

This should print out a statement like the following:

::

    ssh -N -L 8787:r13i2n1:8787 -L 8888:r13i2n1:8888 -l username cheyenne.ucar.edu

You can run this command from your personal computer (not the terminal
logged into Cheyenne) to set up SSH-tunnels that will allow you to log
into web servers running on your allocation. Afterwards, you should be
able to open the following links in your web browser on your computer:

-  Jupyter Lab: http://localhost:8888
-  Dask dashboard: http://localhost:8787/status

The SSH tunnels will route these into the correct machine in your
cluster allocation.

**Dynamic Deployment**


The job scheduler that manages the cluster is not intended for
interactive work like what we do with Jupyter notebooks. When we ask for
a modestly large deployment (like five machines) it may wait for hours
to find an appropriate time slot to deploy our job. This can be
inconvenient because our human schedules may not match up well with the
cluster's job scheduler.

However we seem to be able to get much faster response from the job
scheduler if we launch many single-machine jobs. This allows us to get
larger allocations faster (often immediately).

We can do this by making our deployment process a little bit more
complex by splitting it into two jobs:

1. One job that launches a scheduler and a few workers on one machine
2. Another job that only launches workers on one machine

Write these two scripts to your home directory:

**Main script**


::

    #!/bin/bash
    #PBS -N dask
    #PBS -q economy
    #PBS -A UCLB0022
    #PBS -l select=1:ncpus=36:mpiprocs=6
    #PBS -l walltime=00:30:00
    #PBS -j oe
    #PBS -m abe

    # Writes ~/scheduler.json file in home directory
    # Connect with
    # >>> from dask.distributed import Client
    # >>> client = Client(scheduler_file='~/scheduler.json')

    rm -f scheduler.json
    mpirun --np 6 dask-mpi --nthreads 6 \
        --memory-limit 22e9 \
        --interface ib0 \
        --local-directory $TMPDIR

**Add one worker script**


::

    #!/bin/bash
    #PBS -N dask-workers
    #PBS -q economy
    #PBS -A UCLB0022
    #PBS -l select=1:ncpus=36:mpiprocs=6
    #PBS -l walltime=00:30:00
    #PBS -j oe
    #PBS -m abe

    mpirun --np 6 dask-mpi --nthreads 6 \
        --memory-limit 22e9 \
        --interface ib0 \
        --no-scheduler \
        --local-directory $TMPDIR

And then run the main one once

::

    qsub main.sh

And the second one a few times

::

    qsub add-one-worker.sh
    qsub add-one-worker.sh
    qsub add-one-worker.sh
    qsub add-one-worker.sh

You can run this more times during your session to increase your
allocation dynamically. You can also kill these jobs independently to
contract your allocation dynamically and save compute time.

Further Reading
---------------

We have not attempted to provide a comprehensive tutorial on how to use Pangeo,
Dask, or Jupyter on HPC systems. This is because each HPC system is uniquely
configured. Instead we have provided two generalizable workflows for deploying
Pangeo. Below we provide a few useful links that will be useful for further
customization of these tools.

 * `Deploying Dask on HPC <http://dask.pydata.org/en/latest/setup/hpc.html>`__
 * `Configuring and Deploying Jupyter Servers <http://jupyter-notebook.readthedocs.io/en/stable/index.html>`__

.. _conda: https://conda.io/docs/
.. _Jupyter: https://jupyter.org/
.. _Dask: https://dask.pydata.org/
.. _Cheyenne: https://www2.cisl.ucar.edu/resources/computational-systems/cheyenne
.. _dask-jobqueue: http://dask-jobqueue.readthedocs.io
