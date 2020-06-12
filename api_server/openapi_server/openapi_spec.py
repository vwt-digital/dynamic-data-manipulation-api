import yaml


def get_specification():
    with open('openapi_server/openapi/openapi.yaml', 'r') as openapi:
        spec = yaml.safe_load(openapi.read())

    return spec


def get_database_info(request):
    route = str(request.url_rule).translate(str.maketrans('<>', '{}'))
    spec = get_specification()

    if route in spec.get('paths'):
        return spec['paths'][route].get('x-database-name', None)

    return None
