import unittest
from unittest.mock import MagicMock
import telegram
from ...models import ProductRef, Platform
from ...bot import TelegramBotClient
from ...lambda_handlers.product_update import _handle_product_update


class TestProductUpdate(unittest.TestCase):
    def test_product_update(self):
        pr_1 = ProductRef(Platform.AMAZON_JP, "pr_1")
        pr_2 = ProductRef(Platform.AMAZON_JP, "pr_2")
        pr_3 = ProductRef(Platform.AMAZON_JP, "pr_3")

        bot_client = MagicMock(spec=TelegramBotClient)
        telegram_bot = MagicMock(spec=telegram.Bot)

        _handle_product_update(bot_client, telegram_bot, [pr_1, pr_2, pr_3])

        bot_client.notify_status_update.assert_called_once_with(
            telegram_bot,
            [pr_1, pr_2, pr_3]
        )
