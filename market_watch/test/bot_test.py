import unittest
from unittest.mock import MagicMock, ANY, call
import telegram
from ..bot import TelegramBotClient
from ..transport import DatabaseTransportImpl
from ..translator import MessageID
from ..models import User, ProductRef, Platform, Product, ProductStatus
from .matchers import UserMatcher


class TestProduct(unittest.TestCase):
    def test_get_or_create_user_get_case(self):
        chat_id = "chat_id"
        database_transport = MagicMock(spec=DatabaseTransportImpl)
        database_transport.get_user.return_value = None
        bot = TelegramBotClient(database_transport, None)
        user = bot._get_or_create_user(chat_id)
        self.assertEqual(user.chat_id, chat_id)
        database_transport.get_user.assert_called_once_with(chat_id)
        database_transport.save_user.assert_called_once_with(user)

    def test_get_or_create_user_create_case(self):
        chat_id = "chat_id"
        database_transport = MagicMock(spec=DatabaseTransportImpl)
        database_transport.get_user.return_value = User(chat_id, "doc_id")
        bot = TelegramBotClient(database_transport, None)
        user = bot._get_or_create_user(chat_id)
        self.assertEqual(user.chat_id, chat_id)
        database_transport.get_user.assert_called_once_with(chat_id)

    def create_user_command_handler_mocks(self, chat_id, user=None):
        telegram_bot = MagicMock(spec=telegram.Bot)
        database_transport = MagicMock(spec=DatabaseTransportImpl)
        database_transport.get_user.return_value = user
        tg_update = MagicMock()
        tg_update.message.chat.id = chat_id
        tg_context = MagicMock()
        tg_context.bot = telegram_bot
        bot_client = TelegramBotClient(database_transport, None)
        bot_client.send_message = MagicMock()
        return (
            telegram_bot,
            database_transport,
            tg_update,
            tg_context,
            bot_client
        )

    def test_create_user_handler(self):
        chat_id = "chat_id"
        (
            telegram_bot,
            database_transport,
            tg_update,
            tg_context,
            bot_client
        ) = self.create_user_command_handler_mocks(chat_id)

        bot_client.create_user(tg_update, tg_context)
        database_transport.get_user.assert_called_once_with(chat_id)
        bot_client.send_message.assert_called_once_with(
            telegram_bot,
            chat_id,
            MessageID.HELLO
        )

    def test_subscibe_product_no_duplicate(self):
        chat_id = "chat_id"
        doc_id = "doc_id"
        user = User(chat_id, doc_id=doc_id)
        (
            telegram_bot,
            database_transport,
            tg_update,
            tg_context,
            bot_client
        ) = self.create_user_command_handler_mocks(chat_id, user=user)
        product_ids = ["product_id_1", "product_id_2", "product_id_3"]
        tg_context.matches[0].group.return_value = (
            "\n"
            f"AMAZON_JP {product_ids[0]}\n"
            f"AMAZON_JP {product_ids[1]}\n"
            f"AMAZON_JP {product_ids[2]}\n"
        )
        bot_client.subscibe_product(tg_update, tg_context)
        database_transport.save_user.assert_called_once_with(UserMatcher(User(
            chat_id,
            doc_id=doc_id,
            subscribed=[
                ProductRef(Platform.AMAZON_JP, product_ids[0]),
                ProductRef(Platform.AMAZON_JP, product_ids[1]),
                ProductRef(Platform.AMAZON_JP, product_ids[2]),
            ]
        )))
        bot_client.send_message.assert_called_once_with(
            telegram_bot,
            chat_id,
            MessageID.PRODUCT_SUBSCRIBED,
            n_subscribed=3
        )

    def test_subscibe_product_with_duplicate(self):
        chat_id = "chat_id"
        doc_id = "doc_id"
        user = User(
            chat_id,
            doc_id=doc_id,
            subscribed=[
                ProductRef(Platform.AMAZON_JP, "product_id_1")
            ]
        )
        (
            telegram_bot,
            database_transport,
            tg_update,
            tg_context,
            bot_client
        ) = self.create_user_command_handler_mocks(chat_id, user=user)
        product_ids = ["product_id_1", "product_id_2", "product_id_3"]
        tg_context.matches[0].group.return_value = (
            "\n"
            f"AMAZON_JP {product_ids[0]}\n"
            f"AMAZON_JP {product_ids[1]}\n"
            f"AMAZON_JP {product_ids[2]}\n"
        )
        bot_client.subscibe_product(tg_update, tg_context)
        database_transport.save_user.assert_called_once_with(UserMatcher(User(
            chat_id,
            doc_id=doc_id,
            subscribed=[
                ProductRef(Platform.AMAZON_JP, product_ids[0]),
                ProductRef(Platform.AMAZON_JP, product_ids[1]),
                ProductRef(Platform.AMAZON_JP, product_ids[2]),
            ]
        )))
        bot_client.send_message.assert_called_once_with(
            telegram_bot,
            chat_id,
            MessageID.PRODUCT_SUBSCRIBED,
            n_subscribed=2  # Excluded 1 subscribed product
        )

    def test_subscibe_product_with_invalid_platform(self):
        chat_id = "chat_id"
        doc_id = "doc_id"
        user = User(
            chat_id,
            doc_id=doc_id,
        )
        (
            telegram_bot,
            database_transport,
            tg_update,
            tg_context,
            bot_client
        ) = self.create_user_command_handler_mocks(chat_id, user=user)
        tg_context.matches[0].group.return_value = (
            "\n"
            "INVALID_PLATFORM product_id_1\n"
        )
        bot_client.subscibe_product(tg_update, tg_context)
        database_transport.save_user.assert_not_called()
        bot_client.send_message.assert_called_once_with(
            telegram_bot,
            chat_id,
            MessageID.INVALID_PRODUCT_PLATFORMS,
            platforms="INVALID_PLATFORM"
        )

    def test_subscibe_product_with_invalid_format(self):
        chat_id = "chat_id"
        doc_id = "doc_id"
        user = User(
            chat_id,
            doc_id=doc_id,
        )
        (
            telegram_bot,
            database_transport,
            tg_update,
            tg_context,
            bot_client
        ) = self.create_user_command_handler_mocks(chat_id, user=user)
        tg_context.matches[0].group.return_value = (
            "\n"
            "AMAZON_JP product_id_1\n"
            "AMAZON_JPproduct_id_2\n"
        )
        bot_client.subscibe_product(tg_update, tg_context)
        database_transport.save_user.assert_not_called()
        bot_client.send_message.assert_called_once_with(
            telegram_bot,
            chat_id,
            MessageID.INVALID_PRODUCT_LIST_FORMAT
        )

    def create_notify_status_update_mocks(self, users, products_to_notify):
        telegram_bot = MagicMock(spec=telegram.Bot)
        database_transport = MagicMock(spec=DatabaseTransportImpl)
        database_transport.get_subscribed_users.return_value = users
        database_transport.get_products_by_refs.return_value = products_to_notify  # noqa: E501

        bot_client = TelegramBotClient(database_transport, None)
        bot_client.send_message = MagicMock()
        bot_client.send_messages = MagicMock()
        return (
            telegram_bot,
            database_transport,
            bot_client
        )

    def test_notify_status_update(self):
        pr_1 = ProductRef(Platform.AMAZON_JP, "pr_1")
        pr_2 = ProductRef(Platform.AMAZON_JP, "pr_2")
        pr_3 = ProductRef(Platform.AMAZON_JP, "pr_3")
        p_1 = Product(pr_1)
        p_1.name = "Product 1"
        p_1.status = ProductStatus.AVAILABLE
        p_3 = Product(pr_3)
        p_3.status = ProductStatus.NOT_FOUND

        user_1 = User("chat_1", "user_doc_1", subscribed=[pr_1, pr_2])
        user_2 = User("chat_2", "user_doc_2", subscribed=[pr_1, pr_3])
        (
            telegram_bot,
            database_transport,
            bot_client
        ) = self.create_notify_status_update_mocks(
            [user_1, user_2],
            [p_1, p_3]
        )

        bot_client.notify_status_update(telegram_bot, [pr_1, pr_3])
        database_transport.get_subscribed_users.assert_called_once_with(
            [pr_1, pr_3]
        )
        database_transport.get_products_by_refs.assert_called_once_with(
            [pr_1, pr_3]
        )
        self.assertEqual(len(bot_client.send_messages.mock_calls), 2)
        self.assertEqual(
            bot_client.send_messages.mock_calls[0],
            call(
                telegram_bot,
                "chat_1",
                [
                    (MessageID.PRODUCT_NOTIFY_HEADER, {}),
                    (MessageID.PRODUCT_NOTIFY_UPDATED, {
                        "url": ANY,
                        "platform": Platform.AMAZON_JP.value,
                        "name": "Product 1",
                        "status": ProductStatus.AVAILABLE.value
                    }),
                    (MessageID.PRODUCT_NOTIFY_FOOTER, {}),
                ]
            )
        )
        self.assertEqual(
            bot_client.send_messages.mock_calls[1],
            call(
                telegram_bot,
                "chat_2",
                [
                    (MessageID.PRODUCT_NOTIFY_HEADER, {}),
                    (MessageID.PRODUCT_NOTIFY_UPDATED, {
                        "url": ANY,
                        "platform": Platform.AMAZON_JP.value,
                        "name": "Product 1",
                        "status": ProductStatus.AVAILABLE.value
                    }),
                    (MessageID.PRODUCT_NOTIFY_NOT_FOUND, {
                        "url": ANY,
                        "platform": Platform.AMAZON_JP.value,
                        "id": "pr_3"
                    }),
                    (MessageID.PRODUCT_NOTIFY_FOOTER, {}),
                ]
            )
        )
