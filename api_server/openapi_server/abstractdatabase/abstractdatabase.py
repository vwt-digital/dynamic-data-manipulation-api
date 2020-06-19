from abc import ABC, abstractmethod


class DatabaseInterface(ABC):

    @abstractmethod
    def process_audit_logging(self, old_data, new_data):
        pass

    @abstractmethod
    def get_single(self, id, kind, keys):
        pass

    @abstractmethod
    def put_single(self, id, body, kind, keys):
        pass

    @abstractmethod
    def post_single(self, body, kind, keys):
        pass

    @abstractmethod
    def get_multiple(self, kind, keys):
        pass
