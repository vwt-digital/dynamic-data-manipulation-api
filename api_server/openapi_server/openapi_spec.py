import yaml
import re
import operator

from functools import reduce

OPENAPI_PATH = "openapi_server/openapi/openapi.yaml"


def get_specification():
    with open(OPENAPI_PATH, 'r') as openapi:
        spec = yaml.safe_load(openapi.read())

    return spec


def get_from_dict(data_dict, map_list):
    return reduce(operator.getitem, map_list, data_dict)


def get_route_reference(route_method, request_method):
    if request_method in ['get'] and 'responses' in route_method:
        for code in ['200', '201', '202', '203', '204']:
            if code in route_method['responses']:
                try:
                    route_scheme_ref = get_from_dict(
                        route_method['responses'][code], ['content', 'application/json', 'schema', '$ref'])
                except KeyError:
                    pass
                else:
                    return route_scheme_ref
    elif request_method in ['put', 'post', 'patch'] and 'requestBody' in route_method:
        try:
            route_scheme_ref = get_from_dict(
                route_method['requestBody'], ['content', 'application/json', 'schema', '$ref'])
        except KeyError:
            pass
        else:
            return route_scheme_ref
    return None


def get_schema_properties(specification, reference):
    if reference and re.search(r"(?:#/)(.+)", reference):
        reference_list = reference.replace('#/', '').split('/')
        reference_list.append('properties')

        try:
            properties = get_from_dict(specification, reference_list)
        except KeyError:
            pass
        else:
            for field in properties:
                if properties[field]['type'] in ['array', 'dict']:
                    for key in properties[field]:
                        if type(properties[field][key]) == dict and '$ref' in properties[field][key]:
                            properties[field] = get_schema_properties(specification, properties[field][key]['$ref'])
                            break
                else:
                    properties[field] = properties[field]['type']

            return properties
    return None


def get_route_schema(request, spec, path_schema):
    if path_schema:
        request_method = str(request.method).lower()
        route_reference = get_route_reference(path_schema.get(request_method, None), request_method)
        route_properties = get_schema_properties(spec, route_reference)

        if route_properties and len(route_properties) > 0:
            return route_properties

    return None


def transform_url_rule(url_rule):
    new_url_rule = str(url_rule).replace('int:', '')
    new_url_rule = str(new_url_rule).translate(str.maketrans('<>', '{}'))

    return new_url_rule


def get_database_info(request):
    spec = get_specification()
    path_schema = spec.get('paths', {}).get(transform_url_rule(request.url_rule), None)

    return path_schema.get('x-db-table-name', None) if path_schema else None, get_route_schema(
        request, spec, path_schema)
