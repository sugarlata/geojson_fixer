=============
GeoJSON Fixer
=============


.. image:: https://img.shields.io/pypi/v/geojson_fixer.svg
        :target: https://pypi.python.org/pypi/geojson_fixer

.. image:: https://img.shields.io/travis/sugarlata/geojson_fixer.svg
        :target: https://travis-ci.com/sugarlata/geojson_fixer

.. image:: https://readthedocs.org/projects/geojson-fixer/badge/?version=latest
        :target: https://geojson-fixer.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


.. image:: https://pyup.io/repos/github/sugarlata/geojson_fixer/shield.svg
     :target: https://pyup.io/repos/github/sugarlata/geojson_fixer/
     :alt: Updates



Package to fix minor GeoJSON schema violations


* Free software: MIT license
* Documentation: https://geojson-fixer.readthedocs.io.


Features
--------

* Removes objects that don't confirm to GeoJSON standards (in collections too)
* Polygons with 3 nodes, change to 4 nodes using linear interpolation between two of the nodes.


To Do
-----

* Write tests

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
