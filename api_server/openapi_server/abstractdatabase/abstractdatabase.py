from abc import ABC, abstractmethod


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


class DatabaseInterface(ABC):

    @abstractmethod
    def get_single(self, unique_id, kind, keys):
        pass

    @abstractmethod
    def put_single(self, unique_id, body, kind, keys):
        pass

    @abstractmethod
    def post_single(self, body, kind, keys):
        pass

    @abstractmethod
    def get_multiple(self, kind, keys):
        pass
