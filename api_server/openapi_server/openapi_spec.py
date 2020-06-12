import yaml
import re
import operator

from functools import reduce


def get_specification():
    with open('openapi_server/openapi/openapi.yaml', 'r') as openapi:
        spec = yaml.safe_load(openapi.read())

    return spec


def get_route_reference(route_method):
    if 'responses' in route_method:
        for code in ['200', '201', '202', '203', '204']:
            if code in route_method['responses']:
                try:
                    route_scheme_ref = get_from_dict(
                        route_method['responses'][code], ['content', 'application/json', 'schema', '$ref'])
                except KeyError:
                    pass
                else:
                    return route_scheme_ref
    return None


def get_schema_properties(specification, route_method):
    reference = get_route_reference(route_method)

    if reference and re.search(r"(?:#/)(.+)", reference):
        reference_list = reference.replace('#/', '').split('/')
        reference_list.append('properties')

        try:
            route_schema_properties = get_from_dict(specification, reference_list)
        except KeyError:
            pass
        else:
            return route_schema_properties
    return None


def get_from_dict(data_dict, map_list):
    return reduce(operator.getitem, map_list, data_dict)


class RouteInfo:
    def __init__(self, request):
        self.spec = get_specification()
        self.request = request
        self.req_route = str(request.url_rule).translate(str.maketrans('<>', '{}'))
        self.path_schema = self.spec['paths'].get(self.req_route, None)

    def get_info(self):
        return self.path_schema.get('x-database-name', None) if self.path_schema else None,\
               self.get_route_schema()

    def get_route_schema(self):  # TODO: Create properties for schema referencing other schema
        if self.path_schema:
            route_method = self.path_schema.get(str(self.request.method).lower(), None)
            route_schema = get_schema_properties(self.spec, route_method)

            if len(route_schema) > 0:
                return route_schema

        return None
