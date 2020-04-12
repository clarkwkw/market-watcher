import abc


class HTTPTransport(abc.ABC):
    @abc.abstractmethod
    def get(self, url: str, encoding: str = 'UTF-8') -> str:
        pass
