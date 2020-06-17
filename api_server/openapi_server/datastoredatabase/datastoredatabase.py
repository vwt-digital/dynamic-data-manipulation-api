from google.cloud import datastore
from openapi_server.abstractdatabase import DatabaseInterface, create_entity_object, create_response


class DatastoreDatabase(DatabaseInterface):

    def __init__(self):
        self.db_client = datastore.Client()

    def get_single(self, unique_id, kind, keys):
        """Returns an entity as a dict

        :param unique_id: A unique identifier
        :type unique_id: str
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
        :type unique_id: str
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
