.. _deployments:

Deployments
===========

This is a catalog of pangeo deployments that we know about. If you have deployed
something like pangeo on either a HPC or cloud computing system,
`please let us know <https://github.com/pangeo-data/pangeo/issues/232>`__.

For more information on how pangeo is deployed on these systems, checkout our
`setup guides <setup_guides/index.html>`_.

Cloud Computing Deployments
---------------------------
.. raw:: html

    <table class="table table-striped large">
    {% for deployment in deployments %}

      {% if deployment.kind  == 'cloud' %}
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
            <!-- <br> -->
            <li><em>Platform: {{ deployment.platform }}</em></li>
            <!-- <br> -->
            <li><em>Dask Deployment: {{ deployment.dask }}</em></li>
            <!-- <br> -->
            <li><em>Jupyter Deployment: {{ deployment.jupyter }}</em></li>
            <!-- <br> -->
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
            <!-- <br> -->
            <li><em>Platform: {{ deployment.platform }}</em></li>
            <!-- <br> -->
            <li><em>Dask Deployment: {{ deployment.dask }}</em></li>
            <!-- <br> -->
            <li><em>Jupyter Deployment: {{ deployment.jupyter }}</em></li>
            <!-- <br> -->
          {% for tag in deployment.tags %}
            <mark>{{ tag }}</mark>
          {% endfor %}
          </td>
        </tr>
        {% endif %}
      {% endfor %}
    </table>
