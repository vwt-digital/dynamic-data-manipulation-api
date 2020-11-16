import config
import copy
import datetime

from flask import g, request
from google.cloud import datastore
from openapi_server.abstractdatabase import DatabaseInterface, EntityParser, ForcedFilters


class DatastoreDatabase(DatabaseInterface):

    def __init__(self):
        self.db_client = datastore.Client()

    def process_audit_logging(self, old_data, new_data):
        if hasattr(config, 'AUDIT_LOGS_NAME') and config.AUDIT_LOGS_NAME != "":
            changed = {}
            for attribute in list(set(old_data) | set(new_data)):
                if attribute not in old_data:
                    changed[attribute] = {"new": new_data[attribute]}
                elif attribute not in new_data:
                    changed[attribute] = {"old": old_data[attribute], "new": None}
                elif old_data[attribute] != new_data[attribute]:
                    changed[attribute] = {"old": old_data[attribute], "new": new_data[attribute]}

            if changed:
                key = self.db_client.key(config.AUDIT_LOGS_NAME)
                entity = datastore.Entity(key=key)
                entity.update(
                    {
                        "attributes_changed": changed,
                        "table_id": new_data.key.id_or_name,
                        "table_name": g.db_table_name,
                        "timestamp": datetime.datetime.utcnow().isoformat(timespec="seconds") + 'Z',
                        "user": g.user if g.user is not None else request.remote_addr,
                    }
                )
                self.db_client.put(entity)

    def get_single(self, id, kind, db_keys, res_keys):
        """Returns an entity as a dict

        :param id: A unique identifier
        :type id: str | int
        :param kind: Database kind of entity
        :type kind: str
        :param db_keys: List of keys for database entity
        :type kind: list
        :param res_keys: List of keys for response entity
        :type kind: list

        :rtype: dict
        """

        entity_key = self.db_client.key(kind, id)
        entity = self.db_client.get(entity_key)

        if entity is not None:
            ForcedFilters().validate(filters=g.forced_filters, entity=entity)

            return create_response(res_keys, entity)

        return None

    def put_single(self, id, body, kind, db_keys, res_keys):
        """Updates an entity

        :param id: A unique identifier
        :type id: str | int
        :param body:
        :type body: dict
        :param kind: Database kind of entity
        :type kind: str
        :param db_keys: List of keys for database entity
        :type kind: list
        :param res_keys: List of keys for response entity
        :type kind: list

        :rtype: str
        """

        entity_key = self.db_client.key(kind, id)
        entity = self.db_client.get(entity_key)

        if entity is not None:
            ForcedFilters().validate(filters=g.forced_filters, entity=entity)

            old_entity = copy.deepcopy(entity)
            entity.update(EntityParser().parse(db_keys, body, 'put', id))
            self.db_client.put(entity)

            self.process_audit_logging(old_data=old_entity, new_data=entity)
            return create_response(res_keys, entity)

        return None

    def post_single(self, body, kind, db_keys, res_keys):
        """Creates an entity

        :param body:
        :type body: dict
        :param kind: Database kind of entity
        :type kind: str
        :param db_keys: List of keys for database entity
        :type kind: list
        :param res_keys: List of keys for response entity
        :type kind: list

        :rtype: str
        """

        entity_key = self.db_client.key(kind)
        entity = datastore.Entity(key=entity_key)

        entity.update(EntityParser().parse(db_keys, body, 'post', entity.key.id_or_name))
        self.db_client.put(entity)

        self.process_audit_logging(old_data={}, new_data=entity)

        return create_response(res_keys, entity)

    def get_multiple(self, kind, db_keys, res_keys, filters):
        """Returns all entities as a list of dicts

        :param kind: Database kind of entity
        :type kind: str
        :param db_keys: List of keys for database entity
        :type kind: list
        :param res_keys: List of keys for response entity
        :type kind: list
        :param filters: List of query filters
        :type kind: list

        :rtype: array
        """

        query = self.create_db_query(kind, filters)
        entities = list(query.fetch())

        if entities:
            return create_response(res_keys, entities)

        return None

    def get_multiple_page(self, kind, db_keys, res_keys, filters, page_cursor, page_size, page_action):
        """Returns all entities

        :param kind: Database kind of entity
        :type kind: str
        :param db_keys: List of keys for database entity
        :type kind: list
        :param res_keys: List of keys for response entity
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

        if 'results' not in res_keys or len(res_keys['results']) <= 0:
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
            'results': res_keys['results']
        }

        # Return results
        if db_data:
            response = create_response(response, db_data)

            if page_action == 'prev':
                if g.db_table_id:
                    response['results'] = sorted(
                        response['results'], key=lambda i: i[g.db_table_id], reverse=True)
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
                if filter['name'] == '_FORCED_FILTER':
                    if filter['value'] == "_UPN":
                        filter_value = g.user
                    elif filter['value'] == "_IP":
                        filter_value = g.ip
                    else:
                        filter_value = filter['value']

                    query = query.add_filter(filter['field'], filter['comparison'], filter_value)
                elif filter['name'] in args:
                    filter_datatype = filter['schema']['format'] if \
                        filter['schema'].get('format') else filter['schema']['type']
                    filter_value = data_type_validator(args[filter['name']], filter_datatype)

                    if not filter_value:
                        raise ValueError(
                            f"Value '{args[filter['name']]}' for query param '{filter['name']}' is "
                            f"not of type '{filter_datatype}'")

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
        if type == 'date-time':
            value = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
        if type == 'date':
            value = datetime.strptime(value, "%Y-%m-%d")
    except Exception:
        pass
        return None
    else:
        return value


def create_response(keys, data):
    if type(data) == list:
        return_object = {}
        for key in keys:
            if type(keys[key]) == dict:
                return_object[key] = [
                    EntityParser().parse(keys[key], entity, 'get', entity.key.id_or_name) for entity in data]

        return return_object

    return EntityParser().parse(keys, data, 'get', data.key.id_or_name)
