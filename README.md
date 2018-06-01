[![Build Status](https://travis-ci.org/pangeo-data/pangeo.svg?branch=master)](https://travis-ci.org/pangeo-data/pangeo)
[![Gitter chat](https://badges.gitter.im/pangeo-data/Lobby.svg)](https://gitter.im/pangeo-data/Lobby)

Pangeo Data
===========
A community effort for big data geoscience

## Motivation

There are several building crises facing the Atmosphere / Ocean / Land / Climate (AOC) science community:

- Big Data: datasets are growing too rapidly and legacy software tools for scientific analysis can't handle them. This is a major obstacle to scientific progress.
- Technology Gap:  a growing gap between the technological sophistication of industry solutions (high) and scientific software (low).
- Reproducibility: a fragmentation of software tools and environments renders most AOC research effectively unreproducible and prone to failure.

We believe these challenges can all be addressed through a unified effort.

## Mission Statement

Our mission is to cultivate an ecosystem in which the next generation of open-source analysis tools for ocean, atmosphere and climate science can be developed, distributed, and sustained. These tools must be scalable in order to meet the current and future challenges of big data, and these solutions should leverage the existing expertise outside of the AOC community.

## Vision

We envision a collection of related but independent open-source packages that meet specific scientific needs within the AOC fields. These packages will follow modern best practices for software development, including:

- hosting on GitHub,
- testing,
- coverage,
- continuous integration,
- comprehensive documentation, and
- a welcoming and inclusive development culture.

As much as possible, we will build on top of existing solutions and leverage expertise from the broader technology world, including industry.

The Python Data Stack:

![The State of the Stack](https://github.com/pangeo-data/pangeo/raw/master/docs/_static/stack.png "The State of the Stack")
(Source:  [Jake VanderPlas](https://staff.washington.edu/jakevdp/),
  ["The State of the Stack,"](https://speakerdeck.com/jakevdp/the-state-of-the-stack-scipy-2015-keynote) SciPy Keynote (SciPy 2017).)


In practice, the "python data" software stack (see above) currently provides the most stable and powerful foundation layer for our desired tools. In particular the xarray and dask projects provide a mechanism to easily build scalability into scientific analysis.  Our vision of future AOC software involves the adoption of these common software layers, and a clear communication between developers to define project scope and dependency that eliminates redundancy and fragmentation.


## Get Involved
The scientific culture in the AOC community must be tied to, and evolve from, the community's software culture.  Hence, we depend upon contributions from the entire community, both scientific and industrial.  

We encourage everyone to get involved by:

- contributing to the goals and vision of the organization,
- contributing to the design documents of the proposed software,
- contributing to the software, via issues and pull requests, and/or
- using the software for your scientific analysis and letting us know about your experiences (e.g., contributing to examples)

For now, community discussion is happening on the [GitHub issues page](https://github.com/pangeo-data/pangeo/issues) or on the
[pangeo google group](https://groups.google.com/forum/#!forum/pangeo).
This is an open group, and we invite anyone interested to join.

************
