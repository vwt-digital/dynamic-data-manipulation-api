import yaml
import re
import operator

from functools import reduce

OPENAPI_PATH = "openapi_server/openapi/openapi.yaml"


def get_from_dict(data_dict, map_list):
    """Returns a dictionary based on a mapping"""
    return reduce(operator.getitem, map_list, data_dict)


def get_specification():
    """Returns the OpenAPI specification as JSON"""
    with open(OPENAPI_PATH, 'r') as openapi:
        spec = yaml.safe_load(openapi.read())

    return spec


def transform_url_rule(url_rule):
    """Returns the path from the current request"""
    new_url_rule = str(url_rule).replace('int:', '')
    new_url_rule = str(new_url_rule).translate(str.maketrans('<>', '{}'))

    return new_url_rule


def get_path_schema_reference(path_object, request_method):
    """Returns the schema-reference from the current path item object"""
    if request_method in ['get'] and 'responses' in path_object:
        for code in ['200', '201', '202', '203', '204']:
            if code in path_object['responses']:
                try:
                    route_scheme_ref = get_from_dict(
                        path_object['responses'][code], ['content', 'application/json', 'schema', '$ref'])
                except KeyError:
                    pass
                else:
                    return route_scheme_ref
    elif request_method in ['put', 'post', 'patch'] and 'requestBody' in path_object:
        try:
            route_scheme_ref = get_from_dict(
                path_object['requestBody'], ['content', 'application/json', 'schema', '$ref'])
        except KeyError:
            pass
        else:
            return route_scheme_ref
    return None


def get_schema(spec, reference):
    """Returns the schema object based on a reference"""
    if reference and re.search(r"(?:#/)(.+)", reference):
        reference_list = reference.replace('#/', '').split('/')

        try:
            route_schema = get_from_dict(spec, reference_list)
        except KeyError:
            pass
        else:
            return route_schema

    return None


def get_schema_properties(spec, schema):
    """Returns all properties as {name: type} from a schema"""
    properties = schema.get('properties', {})

    for field in properties:
        if properties[field]['type'] in ['array', 'dict']:
            for key in properties[field]:
                if type(properties[field][key]) == dict and '$ref' in properties[field][key]:
                    nested_schema = get_schema(spec, properties[field][key]['$ref'])
                    properties[field] = get_schema_properties(spec, nested_schema)
                    break
        else:
            properties[field] = properties[field]['type']

    return properties if len(properties) > 0 else None


def get_database_info(request):
    """Returns the 'Database table name' and 'Database keys'"""
    db_table_name = None
    db_keys = None

    spec = get_specification()
    request_method = str(request.method).lower()
    path_object = spec.get('paths', {}).get(transform_url_rule(request.url_rule), None)

    if path_object:
        db_table_name = path_object.get('x-db-table-name', None)
        path_item_object = path_object.get(request_method, None)

        if path_item_object:
            path_schema_reference = get_path_schema_reference(path_item_object, request_method)
            path_schema = get_schema(spec, path_schema_reference)
            db_keys = get_schema_properties(spec, path_schema)

    return db_table_name, db_keys
