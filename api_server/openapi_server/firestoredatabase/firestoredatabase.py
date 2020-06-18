import types

from google.cloud import firestore
from openapi_server.abstractdatabase import DatabaseInterface


class FirestoreDatabase(DatabaseInterface):

    def __init__(self):
        self.db_client = firestore.Client()

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

        doc_ref = self.db_client.collection(kind).document(unique_id)
        doc = doc_ref.get()

        if doc.exists:
            return create_response(keys, doc)

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

        doc_ref = self.db_client.collection(kind).document(unique_id)
        doc = doc_ref.get()

        if doc.exists:
            doc_ref.update(create_entity_object(keys, body, 'put'))
            return doc.id

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

        doc_ref = self.db_client.collection(kind).document()
        doc_ref.set(create_entity_object(keys, body, 'post'))

        return doc_ref.id

    def get_multiple(self, kind, keys):
        """Returns all entities as a list of dicts

        :param kind: Database kind of entity
        :type kind: str
        :param keys: List of entity keys
        :type kind: list

        :rtype: array
        """

        users_ref = self.db_client.collection(kind)
        docs = users_ref.stream()

        if docs:
            return create_response(keys, docs)

        return None


def create_entity_object(keys, entity, method):
    entity_to_return = {}
    for key in keys:
        if key == 'id':
            entity_to_return[key] = entity.id
        else:
            if method == 'get':
                entity_to_return[key] = entity.get(key)
            elif key in entity:
                entity_to_return[key] = entity.get(key)

    return entity_to_return


def create_response(keys, data):
    if isinstance(data, types.GeneratorType):
        return_object = {}
        for key in keys:
            if type(keys[key]) == dict:
                return_object[key] = [create_entity_object(keys[key], entity, 'get') for entity in data]

        return return_object

    return create_entity_object(keys, data, 'get')
