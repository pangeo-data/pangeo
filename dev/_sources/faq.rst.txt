.. _FAQ:

Frequently Asked Questions
==========================

#. *What is Pangeo?*

   Pangeo is first and foremost a :ref:`community of people <collaborators>`
   working collaboratively to develop software and infrastructure to enable
   Big Data geoscience research.

   Some of the products produced by this commmunity include interconnected
   :ref:`software package <packages>` and :ref:`deployments <deployments>` of
   this software in cloud and high-performance-computing environments. Such
   a deployment is sometimes referred to as a *Pangeo Environment*.

#. *What is Big Data?*

   There is a lot of hype around the buzzword "Big Data" today. Some people may
   associate Big Data with specific software platforms (e.g. Hadoop, spark),
   while, for others, "big data" means specific machine learning techniques.
   A more useful and general definition can be found on
   `wikipedia <https://en.wikipedia.org/wiki/Big_data>`_:

     Big data is data sets that are so voluminous and complex that traditional
     data processing application software are inadequate to deal with them.

   By this definition, a great many datasets we regularly confront in Earth
   science are big data.

   A good threshold for when data becomes difficult to deal with is when the
   volume of data exceeds your computer's RAM. Most modern laptops have between
   2 and 16 GB of RAM. High-end workstations and servers can have 1 TB (1000 GB)
   or RAM or more. If the dataset you are trying to analyze can't fit in you
   computer's memory, some special care is required to carry out the analysis.
   Data that can't fit in RAM but can fit on your hard drive is sometimes called
   "medium data."

   The next threshold of difficulty is when the data can't fit on your hard
   drive. Most modern laptops have between 100 GB and 4 TB of storage space on
   the hard drive. If you can't fit your dataset on your internal hard drive,
   you can buy an external hard drive. However, at that point you might consider
   using a high-end server, HPC system, or cloud-based storage for your dataset.
   Once you have many TB of data to analyze, you are definitely in the realm of
   Big Data.

   Some widely used datasets in geoscience exceed a PB. These datasets present
   an extreme challenge, a challenge that the Pangeo project aims to solve.


#. *Why are you doing this?*

   The Pangeo project is driven first and foremost by active geoscience
   researchers who are facing the challenges of Big Data in their daily work.
   These researchers came together to solve these challenges collaboratively,
   hoping that this collaborative approach will be more effective in the
   long run than each small group developing their own solutions. The end goal
   is to work more efficiently and to make scientific discoveries that would
   otherwise be impossible without the Pangeo environment.

#. *Why don't you just use X?*

   (Where X = {Hadoop, Spark, HDFS, SciDB, etc. etc.})

   Many excellent Big Data platforms and tools already exist. But the
   collaborators in the Pangeo project have concluded that none of these has
   sufficient flexibility to handle the diversity and complexity of real-world
   :ref:`use-cases`. Instead, we have converged on the :ref:`packages`
   Xarray and Dask to provide the foundational data models and execution engine
   for our science. We know these tools work for us because many scientists are
   already using them in day-to-day research. Pangeo aims to make them better
   and more capable.

#. *Why don't you use MATLAB?*

   Pangeo is committed to building on open source tools. In addition to
   promoting reproducibility and transparency, only the open source ecosystem
   has the modularity and collaborative structure required to achieve our goals.

#. *Why don't you use Julia or R?*

   We would like Pangeo to evolve into a multi-language platform, including
   support for Julia, R, and other programming languages used for data science.
   Because Pangeo uses Jupyter to provide interactive computing, this is
   already possible today; Jupyter can be configured to run Kernels in many
   different languages (see
   `Jupyter docs on Kernels <http://jupyter.readthedocs.io/en/latest/projects/kernels.html>`_).
   These kernels can be configured to run on any of the
   Pangeo :ref:`Deployments`. However, the higher-level features of the Pangeo
   platform, in particular, parallel execution with Dask, are limited to
   Python at the moment. If you would like to work on enabling multi-language
   support, please engage with us via the `Pangeo GitHub issue tracker`_.

#. *Can I use Pangeo for X?*

   Yes! Our goal is to point you towards the building blocks to create your
   own Pangeo, whatever that means for you. If you want to create up a custom
   Pangeo environment, start by consulting the :ref:`setup-guides`. If you
   want help or want to discuss customization options, reach out via the
   `Pangeo GitHub issue tracker`_.


.. _Pangeo GitHub issue tracker: https://github.com/pangeo-data/pangeo/issues
