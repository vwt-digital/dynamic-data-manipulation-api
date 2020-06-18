import config
import logging
import datetime
import json
import types

from flask import current_app, request
from google.cloud import firestore
from openapi_server.abstractdatabase import DatabaseInterface


class FirestoreDatabase(DatabaseInterface):

    def __init__(self):
        self.db_client = firestore.Client()

    def process_audit_logging(self, old_data, new_data, entity_id):
        if hasattr(config, 'AUDIT_LOGS_NAME') and config.AUDIT_LOGS_NAME != "":
            try:
                old_data = old_data.to_dict() if type(old_data) != dict else old_data
                new_data = new_data.to_dict() if type(new_data) != dict else new_data

                changed = []
                for attribute in list(set(old_data) | set(new_data)):
                    if attribute not in old_data:
                        changed.append({attribute: {"new": new_data[attribute]}})
                    elif attribute not in new_data:
                        changed.append({attribute: {"old": old_data[attribute], "new": None}})
                    elif old_data[attribute] != new_data[attribute]:
                        changed.append({attribute: {"old": old_data[attribute], "new": new_data[attribute]}})

                if changed:
                    doc_ref = self.db_client.collection(config.AUDIT_LOGS_NAME).document()
                    doc_ref.set({
                        "attributes_changed": json.dumps(changed),
                        "entity_id": entity_id,
                        "table_name": current_app.db_table_name,
                        "timestamp": datetime.datetime.utcnow().isoformat(timespec="seconds") + 'Z',
                        "user": current_app.user if current_app.user is not None else request.remote_addr
                    })
            except Exception as e:
                logging.error(f"An exception occurred when audit logging changes for entity '{entity_id}': {str(e)}")
                pass

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
            new_doc = create_entity_object(keys, body, 'put')
            print(new_doc)

            doc_ref.update(new_doc)

            self.process_audit_logging(old_data=doc, new_data=doc_ref.get(), entity_id=doc_ref.id)
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

        self.process_audit_logging(old_data={}, new_data=doc_ref.get(), entity_id=doc_ref.id)

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
