import unittest
from unittest.mock import MagicMock
from parameterized import parameterized
from ...crawlers import AmazonJPCrawler
from ...transport import HTTPTransportImpl
from ...models import ProductStatus, Platform


class TestAmazonJPCrawler(unittest.TestCase):
    def create_http_transport_mock(self, product_html_path: str) -> MagicMock:
        output_html = ""
        with open(product_html_path, "r") as f:
            output_html = "\n".join(f.readlines())
        transport = HTTPTransportImpl()
        transport.get = MagicMock(return_value=output_html)
        return transport

    @parameterized.expand(
        [
            # HTML Path, Dummy ID, Expected name, Expected status
            [
                "market_watch/test/assets/amazon_jp_available.htm",
                "testcase available",
                "失敗図鑑 すごい人ほどダメだった!",
                ProductStatus.AVAILABLE
            ],
            [
                "market_watch/test/assets/amazon_jp_not_available.htm",
                "testcase unavilable",
                "ネクスケア マスク プロ仕様 ふつうサイズ 100枚 ケース売り NM5",
                ProductStatus.UNAVAILABLE
            ],
            [
                "market_watch/test/assets/amazon_jp_not_found.htm",
                "testcase not found",
                "",
                ProductStatus.NOT_FOUND
            ],
            [
                "market_watch/test/assets/amazon_jp_reservable.htm",
                "testcase reservable",
                "Nintendo Switch Lite ターコイズ",
                ProductStatus.AVAILABLE
            ],
        ]
    )
    def test_get_product(
        self,
        html_path: str,
        product_id: str,
        expected_name: str,
        expected_status: ProductStatus
    ):
        with self.subTest(msg=product_id):
            http_transport = self.create_http_transport_mock(html_path)
            crawler = AmazonJPCrawler(http_transport)
            product = crawler.get_product(product_id)
            self.assertEqual(product.platform, Platform.AMAZON_JP)
            self.assertEqual(product.id, product_id)
            self.assertEqual(product.name, expected_name)
            self.assertEqual(product.status, expected_status)
            http_transport.get.assert_called_once()
