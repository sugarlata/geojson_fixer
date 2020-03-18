"""Main module."""

# Originally sourced from https://github.com/JasonSanford/geojsonlint.com
import pdb
import math
import validictory
from geojson_rewind import rewind

from errors import GeoJSONValidationException
from schemas import point, multipoint, linestring, multilinestring, polygon, multipolygon, geometrycollection, feature, featurecollection


def fix_geojson(test_geojson):

    geojson_types = {
        'Point': point,
        'MultiPoint': multipoint,
        'LineString': linestring,
        'MultiLineString': multilinestring,
        'Polygon': polygon,
        'MultiPolygon': multipolygon,
        'GeometryCollection': geometrycollection,
        'Feature': feature,
        'FeatureCollection': featurecollection,
    }

    if not test_geojson['type'] in geojson_types:
        raise GeoJSONValidationException('"%s" is not a valid GeoJSON type.' % test_geojson['type'], 'not_valid_type')

    if test_geojson['type'] in ('Feature', 'FeatureCollection', 'GeometryCollection'):
        #
        # These are special cases that every JSON schema library
        # I've tried doesn't seem to handle properly.
        #
        return_geojson = _validate_special_case(test_geojson)

    else:
        try:
            validictory.validate(test_geojson, geojson_types[test_geojson['type']])
            return_geojson = test_geojson

        except validictory.validator.ValidationError as error:
            return_geojson = _fix_element(test_geojson, error.orig_message)

    if test_geojson['type'] == 'Polygon':
        # First and last coordinates must be coincident
        _validate_polygon(return_geojson)
        return_geojson = rewind(return_geojson)
        return_geojson = _fix_element(return_geojson, 'test_rhr')

    return return_geojson


def _validate_special_case(test_geojson):

    if test_geojson['type'] == 'Feature':
        return _validate_feature_ish_thing(test_geojson)

    elif test_geojson['type'] == 'FeatureCollection':
        if 'features' not in test_geojson:
            raise GeoJSONValidationException('A FeatureCollection must have a "features" property.', 'missing_features')
        elif not isinstance(test_geojson['features'], (list, tuple,)):
            raise GeoJSONValidationException('A FeatureCollection\'s "features" property must be an array.', 'features_not_array')
        
        features_array = []
        for feature in test_geojson['features']:
            return_feature = _validate_feature_ish_thing(feature)
            if return_feature is not None:
                features_array.append(return_feature)

        test_geojson['features'] = features_array
        return test_geojson

    elif test_geojson['type'] == 'GeometryCollection':
        if 'geometries' not in test_geojson:
            raise GeoJSONValidationException('A GeometryCollection must have a "geometries" property.', 'missing_geometries')
        elif not isinstance(test_geojson['geometries'], (list, tuple,)):
            raise GeoJSONValidationException('A GeometryCollection\'s "geometries" property must be an array.', 'geometries_not_array')
        
        geometries_array = []
        for geometry in test_geojson['geometries']:
            if geometry is not None:
                return_geometry = fix_geojson(geometry)
                if return_geometry is not None:
                    geometries_array.append(return_geometry)

        test_geojson['geometries'] = geometries_array
        return test_geojson


def _validate_polygon(polygon):
    for ring in polygon['coordinates']:
        if ring[0] != ring[-1]:
            raise GeoJSONValidationException('A Polygon\'s first and last points must be equivalent.', 'polygon_not_closed')


def _validate_feature_ish_thing(test_geojson):
    if 'geometry' not in test_geojson:
        raise GeoJSONValidationException('A Feature must have a "geometry" property.', 'missing_geometry')
    if 'properties' not in test_geojson:
        raise GeoJSONValidationException('A Feature must have a "properties" property.', 'missing_properties')
    if 'type' not in test_geojson:
        raise GeoJSONValidationException('A Feature must have a "type" property.', 'missing_type')
    
    if test_geojson['geometry'] is not None:
        test_feature = test_geojson['geometry']
        return_feature = fix_geojson(test_feature)
        if return_feature is None:
            test_geojson['geometry'] = {}
            return test_geojson
        else:
            test_geojson['geometry'] = return_feature
            return test_geojson


def _fix_element(fix_geojson, issue):

    if issue == 'must have length greater than or equal to 4':
        # If there are two points or less, return empty
        if len([1 for x in fix_geojson['coordinates'] if len(x) < 3]) != 0:
            return None
        else:
            return _add_polygon_coord(fix_geojson)

    if issue == 'test_rhr':
        # Should already be rewound. If not then have to return None
        return _test_rhr(fix_geojson)

    # pdb.set_trace()


def _add_polygon_coord(fix_geojson):

    # Create point between 1 and 2 using linear interpolation
    finished_coordinates = []
    for coordinates in fix_geojson['coordinates']:
        if len(coordinates) == 3:
            x1, y1 = coordinates[0]
            x2, y2 = coordinates[1]
            xn = round((float(x1) + float(x2)) / 2.0, 6)
            yn = round((float(y1) + float(y2)) / 2.0, 6)
            finished_coordinates.append([coordinates[0], [xn, yn], coordinates[1], coordinates[2]])
        else:
            finished_coordinates.append(coordinates)
    
    fix_geojson['coordinates'] = finished_coordinates
    return fix_geojson


def _test_rhr(fix_geojson):

    # pdb.set_trace()

    if fix_geojson['type'] == 'Polygon':
        if _is_poly_rhr(fix_geojson['coordinates']):
            return fix_geojson
        else:
            return None
    elif fix_geojson['type'] == 'MultiPolygon':
        if False in [_is_poly_rhr(x) for x in fix_geojson['coordinates']]:
            return None
        else:
            return fix_geojson
    

        
    # pdb.set_trace()


def rad(x):
    return x * math.pi / 180.0



def _is_ring_clockwise(coords):
    area = 0
    if len(coords) > 2:
        for i in range(0, len(coords) - 1):
            p1 = coords[i]
            p2 = coords[i+1]
            area += rad(p2[0] - p1[0]) * (2 + math.sin(rad(p1[1])) + math.sin(rad(p2[1])))

    return area >= 0



def _is_poly_rhr(coords):
    if coords and len(coords) > 0:

        if _is_ring_clockwise(coords[0]):
            return False


        interior_coords = coords[1:]
        if False in [_is_ring_clockwise(x) for x in interior_coords]:
            return False
        
    return True
