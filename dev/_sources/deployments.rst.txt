.. _deployments:

Deployments
===========

This is a list of Pangeo deployments either provided by us for development and
demonstration purpose, or other platforms that we know about. If you have 
deployed something like pangeo on either a HPC or cloud computing system,
please let us know via an issue or Pull Request through 
`github <https://github.com/pangeo-data/pangeo/>`_.

For more information on how pangeo is deployed on these systems, checkout our
`setup guides <setup_guides/index.html>`_.

Pangeo provided Cloud Deployments
---------------------------------

Test, development and Binder hubs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Those are deployments managed by Pangeo collaborators and open to everyone,
usually by Pangeo github organization public membership for the standard
Jupyterhubs, and with no restriction for Binder hubs. All of them rely
on `dask-kubernetes <https://kubernetes.dask.org>`_ for (auto)scaling.

.. raw:: html

    <table class="table table-striped large">
    {% for deployment in deployments %}

      {% if deployment.kind  == 'pangeo_cloud' %}
        <tr>
          <td>
            <ul class="list-inline">
              <li><strong>{{ deployment.name}}</strong></li>
              {% if deployment.link %}
              <li>
                  <a class="icon" href="{{ deployment.link }}">
                      <span class="fa-stack fa-lg">
                        <i class="fa fa-external-link fa-stack-1x"></i>
                      </span>
                  </a>
              </li>
              {% endif %}
            </ul>
            <li><em>Description: {{ deployment.description }}</em></li>
            <li><em>Cloud provider: {{ deployment.platform }}</em></li>
            <li><em>Jupyter Deployment: {{ deployment.jupyter }}</em></li>
            <li><em>Access: {{ deployment.access }}</em></li>
          {% for tag in deployment.tags %}
            <mark>{{ tag }}</mark>
          {% endfor %}
          </td>
        </tr>
        {% endif %}
      {% endfor %}
    </table>

Domain specific deployments
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Those are designed specifically for domain use cases and communities, 
allowing to customize both infrastructure and software environment
toward a particular need. If you're interested in one of this deployment,
please contact one of its responsible.

All deployments here use standard Jupyterhub and dask-kubernetes.

.. raw:: html

    <table class="table table-striped large">
    {% for deployment in deployments %}

      {% if deployment.kind  == 'domain_cloud' %}
        <tr>
          <td>
            <ul class="list-inline">
              <li><strong>{{ deployment.name}}</strong></li>
              {% if deployment.link %}
              <li>
                  <a class="icon" href="{{ deployment.link }}">
                      <span class="fa-stack fa-lg">
                        <i class="fa fa-external-link fa-stack-1x"></i>
                      </span>
                  </a>
              </li>
              {% endif %}
            </ul>
            <li><em>Description: {{ deployment.description }}</em></li>
            <li><em>Cloud provider: {{ deployment.platform }}</em></li>
            <li><em>Access: {{ deployment.access }}</em></li>
          {% for tag in deployment.tags %}
            <mark>{{ tag }}</mark>
          {% endfor %}
          </td>
        </tr>
        {% endif %}
      {% endfor %}
    </table>

Other Cloud deployments
-----------------------

.. raw:: html

    <table class="table table-striped large">
    {% for deployment in deployments %}

      {% if deployment.kind  == 'other_cloud' %}
        <tr>
          <td>
            <ul class="list-inline">
              <li><strong>{{ deployment.name}}</strong></li>
              {% if deployment.link %}
              <li>
                  <a class="icon" href="{{ deployment.link }}">
                      <span class="fa-stack fa-lg">
                        <i class="fa fa-external-link fa-stack-1x"></i>
                      </span>
                  </a>
              </li>
              {% endif %}
            </ul>
            <li><em>Description: {{ deployment.description }}</em></li>
            <li><em>Cloud provider: {{ deployment.platform }}</em></li>
            <li><em>Dask Deployment: {{ deployment.dask }}</em></li>
            <li><em>Jupyter Deployment: {{ deployment.jupyter }}</em></li>
          {% for tag in deployment.tags %}
            <mark>{{ tag }}</mark>
          {% endfor %}
          </td>
        </tr>
        {% endif %}
      {% endfor %}
    </table>


High Performance Computing Deployments
--------------------------------------
.. raw:: html

    <table class="table table-striped large">
    {% for deployment in deployments %}

      {% if deployment.kind  == 'hpc' %}
        <tr>
          <td>
            <ul class="list-inline">
              <li><strong>{{ deployment.name}}</strong></li>
              {% if deployment.link %}
              <li>
                  <a class="icon" href="{{ deployment.link }}">
                      <span class="fa-stack fa-lg">
                        <i class="fa fa-external-link fa-stack-1x"></i>
                      </span>
                  </a>
              </li>
              {% endif %}
            </ul>
            <li><em>Description: {{ deployment.description }}</em></li>
            <li><em>Platform: {{ deployment.platform }}</em></li>
            <li><em>Dask Deployment: {{ deployment.dask }}</em></li>
            <li><em>Jupyter Deployment: {{ deployment.jupyter }}</em></li>
          {% for tag in deployment.tags %}
            <mark>{{ tag }}</mark>
          {% endfor %}
          </td>
        </tr>
        {% endif %}
      {% endfor %}
    </table>
