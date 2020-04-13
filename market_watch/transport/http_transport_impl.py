import requests
from .http_transport_base import HTTPTransport


headers = {

    #"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",  # noqa: E501
    # "Accept-Encoding": "gzip, deflate, sdch, br",
    # "Accept-Language": "en-US,en;q=0.8",
    # "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
    "User-Agent": "Mozilla/5.0"
}


class HTTPTransportImpl(HTTPTransport):
    def get(self, url: str, encoding: str = 'UTF-8') -> str:
        res = requests.get(url, headers=headers)
        res.encoding = 'UTF-8'
        return res.text
