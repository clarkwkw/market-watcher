import unittest
from unittest.mock import MagicMock, patch
from ...transport import DatabaseTransport, MessageQueue
from ...models import ProductRef, Product, Platform, ProductStatus
from ...lambda_handlers.crawl import _crawl_products


class TestCrawl(unittest.TestCase):
    def test_crawl_handler(self):
        pr_1 = ProductRef(Platform.AMAZON_JP, "pr_1")
        p_1 = Product(pr_1)
        p_1.status = ProductStatus.UNKNOWN

        p_1_updated = Product(pr_1)
        p_1_updated.name = "Product 1"
        p_1_updated.status = ProductStatus.AVAILABLE

        pr_2 = ProductRef(Platform.AMAZON_JP, "pr_2")
        p_2 = Product(pr_2)
        p_2.status = ProductStatus.UNKNOWN

        p_2_updated = Product(pr_2)
        p_2_updated.status = ProductStatus.NOT_FOUND

        pr_3 = ProductRef(Platform.AMAZON_JP, "pr_3")
        p_3 = Product(pr_3)
        p_3.status = ProductStatus.UNKNOWN

        p_3_updated = Product(pr_3)
        p_3_updated.status = ProductStatus.UNKNOWN

        db_transport = MagicMock(spec=DatabaseTransport)
        db_transport.get_products_by_refs.return_value = [p_1, p_2, p_3]
        message_queue = MagicMock(spec=MessageQueue)
        with patch(
            "market_watch.crawlers.AmazonJPCrawler.get_product",
            side_effect=[p_1_updated, p_2_updated, p_3_updated]
        ):
            _crawl_products(
                db_transport,
                None,
                message_queue,
                [pr_1, pr_2, pr_3]
            )
            db_transport.get_products_by_refs.assert_called_once_with(
                [pr_1, pr_2, pr_3],
                return_default_if_not_found=True
            )
            db_transport.save_products.assert_called_once_with(
                [p_1_updated, p_2_updated]
            )
            message_queue.enqueue.assert_called_once_with(
                [p_1_updated, p_2_updated]
            )
