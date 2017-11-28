Getting Started with Dask on Cheyenne
=====================================

This documents how to set up an environment to run XArray on Cheyenne.
In particular it covers the following:

1. Install conda and creating an environment
2. Configure Jupyter
3. Launch Dask with a job scheduler
4. Launch a Jupyter server for your job
5. Connect to Jupyter and the Dask dashboard from your personal computer

This document assumes that you already have an account on Cheyenne, and
are comfortable using the command line. There is a
`screencast <https://www.youtube.com/watch?v=7i5m78DSr34&feature=youtu.be>`__
of this page.

You should log into Cheyenne now.

Installing a software environment
---------------------------------

After you have logged into Cheyenne, download and install Miniconda:

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
        python=3.6 dask distributed xarray jupyterlab mpi4py

Activate this environment

::

    source activate pangeo

Your prompt should now look like this:

::

    (pangeo) mrocklin@cheyenne5:~>

And if you ask where your Python command lives, it should direct you to
somewhere in your home directory:

::

    (pangeo) mrocklin@cheyenne5:~> which python
    /glade/u/home/mrocklin/miniconda3/envs/pangeo/bin/python

Configure Jupyter
-----------------

(If you don't plan to use Jupyter notebooks then you can safely skip
this section.)

Jupyter notebook servers include a password for security. We're going to
setup a password for ourselves. First we generate the Jupyter config
file

::

    jupyter notebook --generate-config

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
hashed password that encodes the same information, but is safe to
include in a publicly accessible config file. I entered "password" (do
not do this) and go the following output:

.. code:: python

    Out[1]: 'sha1:69a76df803b9:99ca27341563cd85ba4e78684128e1f4ad2d8d0d'

Copy that string into your ``jupyter_notebook_config.py`` config file

::

    c.NotebookApp.password = u'sha1:69a76df803b9:99ca27341563cd85ba4e78684128e1f4ad2d8d0d'

Great. We're done with that.

Launch Dask with a script
-------------------------

.. note::

   The following scripts and proceedures have been packed into a convenient wrapper
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
       ssh -N -L 8877:r7i3n13:8877 -L 8878:r7i3n13:8787 username@cheyenne.ucar.edu
       Then open the following URLs:
           Jupyter lab: http://localhost:8877
           Dask dashboard: http://localhost:8878

   It may be ncessessary to modify the included scripts to use different PBS
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
    #PBS -l select=2:ncpus=72:mpiprocs=6:ompthreads=6
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
    mpirun --np 12 dask-mpi --nthreads 6 --memory-limit 24e9 --interface ib0

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
    1681778.chadmin mrocklin regular  sample      27872   2 144    --  00:20 R 00:01

When this job runs it places a ``scheduler.json`` file in your home
directory. This contains the necessaary information to connect to this
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
-----------------------------

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

    print("ssh -N -L 8787:%s:8787 -L 8888:%s:8888 cheyenne.ucar.edu" % (host, host))

This should print out a statement like the following:

::

    ssh -N -L 8787:r13i2n1:8787 -L 8888:r13i2n1:8888 -l mrocklin cheyenne.ucar.edu

You can run this command from your personal computer (not the terminal
logged into Cheyenne) to set up SSH-tunnels that will allow you to log
into web servers running on your allocation. Afterwards, you should be
able to open the following links in your web browser on your computer:

-  Jupyter Lab: http://localhost:8888
-  Dask dashboard: http://localhost:8787/status

The SSH tunnels will route these into the correct machine in your
cluster allocation.

Open a notebook and perform a simple computation
------------------------------------------------

From the `Jupyter Lab webpage <http://localhost:8888>`__ you can create
and manage work in notebooks. You can download a `basic starter
notebook <https://gist.github.com/mrocklin/99e1c9b72eaebe6df5d146ac427261d1#file-cheyenne_xarray_dask_example-ipynb>`__
that loads some data, connects to the cluster, and then does some basic
analysis to your home directory using ``wget``

::

    wget https://gist.githubusercontent.com/mrocklin/99e1c9b72eaebe6df5d146ac427261d1/raw/9387d577bffdf690b5527e9835354ee659089e23/cheyenne_xarray_dask_example.ipynb

From the `Dask dashboard <http://localhost:8787>`__ you can track the
cluster's progress as you do your work.

Dynamic Deployment
------------------

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

Main script
^^^^^^^^^^^

::

    #!/bin/bash
    #PBS -N dask
    #PBS -q economy
    #PBS -A UCLB0022
    #PBS -l select=1:ncpus=36:mpiprocs=6:ompthreads=6
    #PBS -l walltime=00:30:00
    #PBS -j oe
    #PBS -m abe

    # Writes ~/scheduler.json file in home directory
    # Connect with
    # >>> from dask.distributed import Client
    # >>> client = Client(scheduler_file='~/scheduler.json')

    rm -f scheduler.json
    mpirun --np 6 dask-mpi --nthreads 6 --memory-limit 22e9 --interface ib0 --local-directory /glade/scratch/$USER

Add one worker script
^^^^^^^^^^^^^^^^^^^^^

::

    #!/bin/bash
    #PBS -N dask-workers
    #PBS -q economy
    #PBS -A UCLB0022
    #PBS -l select=1:ncpus=36:mpiprocs=6:ompthreads=6
    #PBS -l walltime=00:30:00
    #PBS -j oe
    #PBS -m abe

    mpirun --np 6 dask-mpi --nthreads 6 --memory-limit 22e9 --interface ib0 --no-scheduler --local-directory /glade/scratch/$USER

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
