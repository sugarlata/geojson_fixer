=====
Usage
=====

To use GeoJSON Fixer in a project::

    import geojson_fixer

geojson_fixer has one function:: fix_geojson


This function will remove objects that do not conform
to GeoJSON schema unless the error is a three point polygon,
in which it will create another point using linear interpolation.
