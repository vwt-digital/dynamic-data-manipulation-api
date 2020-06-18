from abc import ABC, abstractmethod


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
