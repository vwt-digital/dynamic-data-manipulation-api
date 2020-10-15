import config
import copy
import datetime
import json

from flask import current_app, request
from google.cloud import datastore
from openapi_server.abstractdatabase import DatabaseInterface


class DatastoreDatabase(DatabaseInterface):

    def __init__(self):
        self.db_client = datastore.Client()

    def process_audit_logging(self, old_data, new_data):
        if hasattr(config, 'AUDIT_LOGS_NAME') and config.AUDIT_LOGS_NAME != "":
            changed = []
            for attribute in list(set(old_data) | set(new_data)):
                if attribute not in old_data:
                    changed.append({attribute: {"new": new_data[attribute]}})
                elif attribute not in new_data:
                    changed.append({attribute: {"old": old_data[attribute], "new": None}})
                elif old_data[attribute] != new_data[attribute]:
                    changed.append({attribute: {"old": old_data[attribute], "new": new_data[attribute]}})

            if changed:
                key = self.db_client.key(config.AUDIT_LOGS_NAME)
                entity = datastore.Entity(key=key)
                entity.update(
                    {
                        "attributes_changed": json.dumps(changed),
                        "table_id": new_data.key.id_or_name,
                        "table_name": current_app.db_table_name,
                        "timestamp": datetime.datetime.utcnow().isoformat(timespec="seconds") + 'Z',
                        "user": current_app.user if current_app.user is not None else request.remote_addr,
                    }
                )
                self.db_client.put(entity)

    def get_single(self, id, kind, keys):
        """Returns an entity as a dict

        :param id: A unique identifier
        :type id: str | int
        :param kind: Database kind of entity
        :type kind: str
        :param keys: List of entity keys
        :type kind: list

        :rtype: dict
        """

        entity_key = self.db_client.key(kind, id)
        entity = self.db_client.get(entity_key)

        if entity is not None:
            return create_response(keys, entity)

        return None

    def put_single(self, id, body, kind, keys):
        """Updates an entity

        :param id: A unique identifier
        :type id: str | int
        :param body:
        :type body: dict
        :param kind: Database kind of entity
        :type kind: str
        :param keys: List of entity keys
        :type kind: list

        :rtype: str
        """

        entity_key = self.db_client.key(kind, id)
        entity = self.db_client.get(entity_key)

        if entity is not None:
            old_entity = copy.deepcopy(entity)
            entity.update(create_entity_object(keys, body, 'put'))
            self.db_client.put(entity)

            self.process_audit_logging(old_data=old_entity, new_data=entity)
            return id

        return None

    def post_single(self, body, kind, keys):
        """Creates an entity

        :param body:
        :type body: dict
        :param kind: Database kind of entity
        :type kind: str
        :param keys: List of entity keys
        :type kind: list

        :rtype: str
        """

        entity_key = self.db_client.key(kind)
        entity = datastore.Entity(key=entity_key)

        entity.update(create_entity_object(keys, body, 'post'))
        self.db_client.put(entity)

        self.process_audit_logging(old_data={}, new_data=entity)

        return entity.key.id_or_name

    def get_multiple(self, kind, keys, filters):
        """Returns all entities as a list of dicts

        :param kind: Database kind of entity
        :type kind: str
        :param keys: List of entity keys
        :type kind: list
        :param filters: List of query filters
        :type kind: list

        :rtype: array
        """

        query = self.create_db_query(kind, filters)
        entities = list(query.fetch())

        if entities:
            return create_response(keys, entities)

        return None

    def get_multiple_page(self, kind, keys, filters, page_cursor, page_size, page_action):
        """Returns all entities

        :param kind: Database kind of entity
        :type kind: str
        :param keys: List of entity keys
        :type kind: list
        :param filters: List of query filters
        :type kind: list
        :param page_cursor: The cursor for retrieve a specific page
        :type page_cursor: str
        :param page_size: The numbers of items within a page
        :type page_size: int
        :param page_action: Selector to get next or previous page based on the cursor
        :type page_action: str

        :rtype: dict
        """

        if 'results' not in keys or len(keys['results']) <= 0:
            raise ValueError("Key 'results' is not within response schema")

        query_params = {
            'limit': page_size
        }

        if page_cursor:
            query_params['start_cursor'] = page_cursor

        query = self.create_db_query(kind, filters)

        # When the previous page is requested and the latest cursor from the original query is used
        # to get results in reverse.
        if page_action == 'prev':
            query.order = ['__key__']
        else:
            query.order = ['-__key__']

        query_iter = query.fetch(**query_params)  # Execute query
        current_page = next(query_iter.pages)  # Setting current iterator page
        db_data = list(current_page)  # Set page results list

        response = {
            'results': keys['results']
        }

        # Return results
        if db_data:
            response = create_response(response, db_data)

            if page_action == 'prev':
                if current_app.db_table_id:
                    response['results'] = sorted(
                        response['results'], key=lambda i: i[current_app.db_table_id], reverse=True)
                next_cursor = page_cursor  # Grab current cursor for next page
            else:
                next_cursor = query_iter.next_page_token.decode() if \
                    query_iter.next_page_token else None  # Grab new cursor for next page
        else:
            response['results'] = []
            next_cursor = None

        # Create response object
        response['status'] = 'success'
        response['page_size'] = page_size
        response['next_page'] = next_cursor

        return response

    def create_db_query(self, kind, filters):
        query = self.db_client.query(kind=kind)

        if filters:
            args = request.args.to_dict()

            for filter in filters:
                if filter['name'] in args:
                    filter_datatype = filter['schema']['format'] if \
                        filter['schema'].get('format') else filter['schema']['type']
                    filter_value = data_type_validator(args[filter['name']], filter_datatype)

                    if not filter_value:
                        raise ValueError(
                            f"Value '{args[filter['name']]}' for query param '{filter['name']}' is "
                            + f"not of type '{filter_datatype}'")

                    query = query.add_filter(filter['field'], filter['comparison'], filter_value)

        return query


def data_type_validator(value, type):
    try:
        if not type:
            return value
        if type == 'integer' or type == 'number':
            value = int(value)
        if type == 'boolean':
            value = bool(value)
        if type == 'datetime':
            value = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
        if type == 'date':
            value = datetime.strptime(value, "%Y-%m-%d")
    except Exception:
        pass
        return None
    else:
        return value


def create_entity_object(keys, entity, method):
    entity_to_return = {}
    for key in keys:
        if key == current_app.db_table_id:
            entity_to_return[key] = entity.key.id_or_name
        else:
            if method == 'get':
                entity_to_return[key] = entity.get(key, None)
            elif key in entity:
                entity_to_return[key] = entity[key]

        if keys[key].get('required', False) and method != 'get' and not entity.get(key, None):
            raise ValueError(f"Property '{key}' is required")

    return entity_to_return


def create_response(keys, data):
    if type(data) == list:
        return_object = {}
        for key in keys:
            if type(keys[key]) == dict:
                return_object[key] = [create_entity_object(keys[key], entity, 'get') for entity in data]

        return return_object

    return create_entity_object(keys, data, 'get')
