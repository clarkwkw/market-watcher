from bs4 import BeautifulSoup
import logging
from .crawler_base import CrawlerBase
from ..models import Product, Platform, ProductStatus, ProductRef
from ..transport import HTTPTransport
from ..utils import configure_logger


configure_logger()
logger = logging.getLogger(__name__)

PRODUCT_URL_BASE = "https://www.amazon.co.jp/dp/{product_id}/"
PRODUCT_UNAVAILABLE_TEXTS = ["在庫切れ", "取り扱いできません"]
PRODUCT_AVAILABLE_TEXT = "在庫あり"
PRODUCT_RESERVABLE_TEXT = "出品者からお求めいただけます"
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
            logging.info(f"availability text: {availability_div.text}")
            product_name_span = soup.find(id='productTitle')
            if product_name_span is not None:
                product.name = product_name_span.text.strip()

            for unavailable_text in PRODUCT_UNAVAILABLE_TEXTS:
                if unavailable_text in availability_div.text:
                    product.status = ProductStatus.UNAVAILABLE

            if PRODUCT_AVAILABLE_TEXT in availability_div.text or\
                    PRODUCT_RESERVABLE_TEXT in availability_div.text:
                product.status = ProductStatus.AVAILABLE
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
