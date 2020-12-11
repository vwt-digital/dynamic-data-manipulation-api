# flake8: noqa

import operator

from abc import ABC, abstractmethod
from flask import g
from functools import reduce


class DatabaseInterface(ABC):

    @abstractmethod
    def process_audit_logging(self, old_data, new_data):
        pass

    @abstractmethod
    def get_single(self, id, kind, db_keys, res_keys):
        pass

    @abstractmethod
    def put_single(self, id, body, kind, db_keys, res_keys):
        pass

    @abstractmethod
    def post_single(self, body, kind, db_keys, res_keys):
        pass

    @abstractmethod
    def get_multiple(self, kind, db_keys, res_keys, filters):
        pass

    @abstractmethod
    def get_multiple_page(self, kind, db_keys, res_keys, filters, page_cursor, page_size, page_action):
        pass


class EntityParser:

    def __init__(self):
        pass

    def parse(self, keys, entity, method, entity_id):
        if not isinstance(entity, dict):
            entity = entity.to_dict()

        if method == 'get':
            return self.create_object(keys, entity, entity_id, False)
        else:
            new_object = self.create_object(keys, entity, entity_id, True)
            return self.create_update_object(keys, new_object)

    def create_object(self, keys, entity, entity_id, value_bound):
        entity_to_return = {}
        for key in keys:
            if key == '_target':
                continue

            if key == g.db_table_id:
                entity_to_return[key] = entity_id
                continue

            if isinstance(keys[key], dict) and '_properties' in keys[key]:
                nested_object = self.create_object(keys[key]['_properties'], entity, entity_id, value_bound)
                if nested_object:
                    entity_to_return[key] = nested_object
            else:
                try:
                    if value_bound:
                        entity_to_return[key] = entity.get(key)
                    else:
                        entity_to_return[key] = get_from_dict(entity, keys[key].get('_target', key))
                except (KeyError, AttributeError, TypeError):
                    if value_bound and not keys[key].get('required', False):
                        continue

                    entity_to_return[key] = None

            if value_bound and keys[key].get('required', False) and not entity.get(key, None):
                raise ValueError(f"Property '{key}' is required")

        return entity_to_return

    def create_update_object(self, keys, entity):
        target_keys = self.flatten(d=keys, sep='.')

        entity_to_return = {}
        for key in target_keys:
            try:
                value = get_from_dict(entity, key.split('.'))
            except (KeyError, AttributeError, TypeError):
                continue
            else:
                entity_to_return = self.create_nested_object(target_keys[key], value, entity_to_return)

        return entity_to_return

    def create_nested_object(self, key_list, value, object):
        key = key_list[0]
        if len(key_list) > 1:
            if key not in object:
                object[key] = {}

            object[key] = self.create_nested_object(key_list[1:], value, object[key])
        else:
            object[key] = value

        return object

    def flatten(self, d, parent_key='', sep='_'):
        items = []
        for k, v in d.items():
            new_key = parent_key + sep + k if parent_key else k
            if isinstance(v, dict) and '_properties' in v:
                items.extend(self.flatten(v['_properties'], new_key, sep=sep).items())
            else:
                items.append((new_key, v['_target']))
        return dict(items)


class ForcedFilters:

    def __init__(self):
        pass

    def validate(self, filters, entity):
        """Validates if the entity can be accessed based on the forced filters

        :param filters: A list of forced filters
        :type filters: list
        :param entity: The entity
        :type entity: dict | None
        """

        if filters:
            if not entity:
                raise ValueError("The requested entity has no value")

            for item in filters:
                map_list = item['field'].split('.')

                if item['value'] == '_UPN':
                    self.compare_from_dict(g.user, entity, map_list)
                elif item['value'] == '_IP':
                    self.compare_from_dict(g.ip, entity, map_list)
                elif item['value'] == '_NOT_EXISTING':
                    self.value_not_existing(entity, map_list)
                else:
                    self.compare_from_dict(item['value'], entity, map_list)

    @staticmethod
    def compare_from_dict(value, data_dict, map_list):
        """Returns an error if value not same as mapping value"""
        try:
            if not value == get_from_dict(data_dict, map_list):
                raise AttributeError
        except (KeyError, AttributeError, TypeError):
            raise PermissionError("Unauthorized request")

    @staticmethod
    def value_not_existing(data_dict, map_list):
        """Returns an error if mapping exists in dict"""
        try:
            get_from_dict(data_dict, map_list)
        except (KeyError, AttributeError, TypeError):
            pass
        else:
            raise PermissionError("Unauthorized request")


def get_from_dict(data_dict, map_list):
    """Returns a dictionary based on a mapping"""
    return reduce(operator.getitem, map_list, data_dict)
