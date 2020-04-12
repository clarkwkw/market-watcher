from bs4 import BeautifulSoup
from .crawler_base import CrawlerBase
from ..models import Product, Platform, ProductStatus, ProductRef
from ..transport import HTTPTransport


PRODUCT_URL_BASE = "https://www.amazon.co.jp/dp/{product_id}/"
PRODUCT_UNAVAILABLE_TEXT = "在庫切れ"
PRODUCT_AVAILABLE_TEXT = "在庫あり"
NOT_FOUND_LINK = "/ref=cs_404_logo"


class AmazonJPCrawler(CrawlerBase):
    platform = Platform.AMAZON_JP

    def __init__(self, transport: HTTPTransport):
        self.transport = transport

    def get_product(self, id: str) -> Product:
        res = self.transport.get(AmazonJPCrawler.get_product_url(id))
        soup = BeautifulSoup(res, 'html.parser')
        availability_div = soup.find(id='availability')
        product = Product(ProductRef(self.platform, id))

        if availability_div is not None:
            product_name_span = soup.find(id='productTitle')
            if product_name_span is not None:
                product.name = product_name_span.text.strip()
            if PRODUCT_UNAVAILABLE_TEXT in availability_div.text:
                product.status = ProductStatus.UNAVAILABLE
            elif PRODUCT_AVAILABLE_TEXT in availability_div.text:
                product.status = ProductStatus.AVAILABLE
            else:
                product.status = ProductStatus.UNKNOWN
        else:
            links = soup.find_all('a')
            for link in links:
                if link.get("href") == NOT_FOUND_LINK:
                    product.status = ProductStatus.NOT_FOUND
                    break
        return product

    @classmethod
    def get_product_url(cls, id: str) -> str:
        return PRODUCT_URL_BASE.format(product_id=id)
