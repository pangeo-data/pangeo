.. _catalog:

Pangeo Data Catalog
===================

These datasets are directly accessible from the Google Cloud Pangeo deployment:
`pangeo.pydata.org <http://pangeo.pydata.org>`_.

.. raw:: html

    <table class="data-catalog table table-striped large">
    {% for name in catalog.walk() %}
      {% set entry = catalog[name] %}

      <tr>
        <td>
          <div id="{{ name }}">
          <ul class="list-inline">
            <li><a href="#{{ name }}"><strong>{{ name }}</strong></a></li><br>
            <li>{{ entry.description }}</li><br>
            <li><em>Format: {{ entry.describe_open()['plugin'] }}</em></li>
            <li><em>Container: {{ entry.container }}</em></li><br>
            <li><em>Location: {{ entry.urlpath }}</em></li>
            <li>
            <pre>import intake
    catalog_url = 'https://github.com/pangeo-data/pangeo/raw/master/gce/catalog.yaml'
    {{ name }} = intake.Catalog(catalog_url).{{ name }}.to_dask()</pre>
            </li>
          </ul>
          </div>
        </td>
      </tr>
    {% endfor %}
    </table>

