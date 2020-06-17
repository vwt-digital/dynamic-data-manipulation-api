from google.cloud import datastore
from openapi_server.abstractdatabase import DatabaseInterface


class DatastoreDatabase(DatabaseInterface):

    def __init__(self):
        self.db_client = datastore.Client()

    def get_single(self, unique_id, kind, keys):
        """Returns an entity as a dict

        :param unique_id: A unique identifier
        :type unique_id: str | int
        :param kind: Database kind of entity
        :type kind: str
        :param keys: List of entity keys
        :type kind: list

        :rtype: dict
        """

        entity_key = self.db_client.key(kind, unique_id)
        entity = self.db_client.get(entity_key)

        if entity is not None:
            return create_response(keys, entity)

        return None

    def put_single(self, unique_id, body, kind, keys):
        """Updates an entity

        :param unique_id: A unique identifier
        :type unique_id: str | int
        :param body:
        :type body: dict
        :param kind: Database kind of entity
        :type kind: str
        :param keys: List of entity keys
        :type kind: list

        :rtype: str
        """

        entity_key = self.db_client.key(kind, unique_id)
        entity = self.db_client.get(entity_key)

        if entity is not None:
            entity.update(create_entity_object(keys, body, 'put'))
            self.db_client.put(entity)
            return unique_id

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

        return entity.key.id_or_name

    def get_multiple(self, kind, keys):
        """Returns all entities as a list of dicts

        :param kind: Database kind of entity
        :type kind: str
        :param keys: List of entity keys
        :type kind: list

        :rtype: array
        """

        query = self.db_client.query(kind=kind)
        entities = list(query.fetch())

        if entities:
            return create_response(keys, entities)

        return None


def create_entity_object(keys, entity, method):
    entity_to_return = {}
    for key in keys:
        if key == 'id':
            entity_to_return[key] = entity.key.id_or_name
        else:
            if method == 'get':
                entity_to_return[key] = entity.get(key, None)
            elif key in entity:
                entity_to_return[key] = entity[key]

    return entity_to_return


def create_response(keys, data):
    if type(data) == list:
        return_object = {}
        for key in keys:
            if type(keys[key]) == dict:
                return_object[key] = [create_entity_object(keys[key], entity, 'get') for entity in data]

        return return_object

    return create_entity_object(keys, data, 'get')
