import unittest
from unittest.mock import MagicMock
from ...transport import DatabaseTransport, MessageQueue
from ...models import ProductRef, Product, Platform, ProductStatus
from ...lambda_handlers.product_distribute import _distribute_products


class TestProductDistribute(unittest.TestCase):
    def test_product_distribute_handler(self):
        pr_1 = ProductRef(Platform.AMAZON_JP, "pr_1")
        pr_2 = ProductRef(Platform.AMAZON_JP, "pr_2")
        pr_3 = ProductRef(Platform.AMAZON_JP, "pr_3")
        p_1 = Product(pr_1)
        p_2 = Product(pr_2)
        p_2.status = ProductStatus.NOT_FOUND
        p_3 = Product(pr_3)

        db_transport = MagicMock(spec=DatabaseTransport)
        db_transport.get_all_subscribed_products.return_value = [p_1, p_2, p_3]
        message_queue = MagicMock(spec=MessageQueue)

        _distribute_products(db_transport, message_queue)

        message_queue.enqueue.assert_called_once_with([p_1, p_3])
