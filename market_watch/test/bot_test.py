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
        bot_client.send_messages = MagicMock()
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
        bot_client.send_messages.assert_called_once_with(
            telegram_bot,
            chat_id,
            [(MessageID.HELLO, {})]
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
        bot_client.send_messages.assert_called_once_with(
            telegram_bot,
            chat_id,
            [(
                MessageID.PRODUCT_SUBSCRIBED,
                {"n_subscribed": 3}
            )]
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
        bot_client.send_messages.assert_called_once_with(
            telegram_bot,
            chat_id,
            [(
                MessageID.PRODUCT_SUBSCRIBED,
                {"n_subscribed": 2}  # Excluded 1 subscribed product
            )]
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
        bot_client.send_messages.assert_called_once_with(
            telegram_bot,
            chat_id,
            [(
                MessageID.INVALID_PRODUCT_PLATFORMS,
                {"platforms": "INVALID_PLATFORM"}
            )]
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
        bot_client.send_messages.assert_called_once_with(
            telegram_bot,
            chat_id,
            [(MessageID.INVALID_PRODUCT_LIST_FORMAT, {})]
        )

    def create_notify_status_update_mocks(self, users, products_to_notify):
        telegram_bot = MagicMock(spec=telegram.Bot)
        database_transport = MagicMock(spec=DatabaseTransportImpl)
        database_transport.get_subscribed_users.return_value = users
        database_transport.get_products_by_refs.return_value = products_to_notify  # noqa: E501

        bot_client = TelegramBotClient(database_transport, None)
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

    def create_list_product_mocks(self, user):
        telegram_bot = MagicMock(spec=telegram.Bot)
        database_transport = MagicMock(spec=DatabaseTransportImpl)
        database_transport.get_user.return_value = user
        tg_update = MagicMock()
        tg_context = MagicMock()
        tg_context.bot = telegram_bot
        bot_client = TelegramBotClient(database_transport, None)
        bot_client.send_messages = MagicMock()
        bot_client.update_with_messages = MagicMock()
        bot_client.answer_query = MagicMock()
        return (
            telegram_bot,
            database_transport,
            tg_update,
            tg_context,
            bot_client
        )

    def test_list_products_from_command(self):
        pr_1 = ProductRef(Platform.AMAZON_JP, "p1")
        p1 = Product(pr_1)
        p1.name = "Product 1"
        pr_2 = ProductRef(Platform.AMAZON_JP, "p2")
        p2 = Product(pr_2)
        p2.name = "Product 2"
        pr_3 = ProductRef(Platform.AMAZON_JP, "p3")
        p3 = Product(pr_3)
        p3.name = "Product 3"
        user = User("chat_id", subscribed=[pr_1, pr_2, pr_3])
        (
            telegram_bot,
            database_transport,
            tg_update,
            tg_context,
            bot_client
        ) = self.create_list_product_mocks(user)
        database_transport.get_products_by_refs.return_value = [p1, p2, p3]
        tg_update.message.chat.id = "chat_id"
        bot_client.list_product(tg_update, tg_context)

        database_transport.get_products_by_refs.assert_called_once_with(
            [pr_1, pr_2, pr_3],
            return_default_if_not_found=True
        )
        bot_client.send_messages.assert_called_once_with(
            telegram_bot,
            "chat_id",
            [
                (MessageID.PRODUCT_LIST_HEADER, {}),
                (
                    MessageID.PRODUCT_LIST_ITEM,
                    {
                        "i": 1,
                        "url": ANY,
                        "platform": Platform.AMAZON_JP.value,
                        "name": "Product 1",
                        "status": ProductStatus.UNKNOWN.value
                    },
                ),
                (
                    MessageID.PRODUCT_LIST_ITEM,
                    {
                        "i": 2,
                        "url": ANY,
                        "platform": Platform.AMAZON_JP.value,
                        "name": "Product 2",
                        "status": ProductStatus.UNKNOWN.value
                    }
                ),
                (
                    MessageID.PRODUCT_LIST_ITEM,
                    {
                        "i": 3,
                        "url": ANY,
                        "platform": Platform.AMAZON_JP.value,
                        "name": "Product 3",
                        "status": ProductStatus.UNKNOWN.value
                    }
                )
            ],
            keyboard=[
                [
                    (
                        (
                            MessageID.INTEGER_WITH_BRACKETS,
                            {"value": 1}
                        ),
                        "/list 0"
                    )
                ],
                [
                    (
                        (
                            MessageID.BUTTON_REMOVE,
                            {"id": 1}
                        ),
                        "/unsubscribe AMAZON_JP p1"
                    ),
                    (
                        (
                            MessageID.BUTTON_REMOVE,
                            {"id": 2}
                        ),
                        "/unsubscribe AMAZON_JP p2"
                    ),
                    (
                        (
                            MessageID.BUTTON_REMOVE,
                            {"id": 3}
                        ),
                        "/unsubscribe AMAZON_JP p3"
                    )
                ]
            ]
        )

    def test_list_products_from_command_empty(self):
        user = User("chat_id", subscribed=[])
        (
            telegram_bot,
            database_transport,
            tg_update,
            tg_context,
            bot_client
        ) = self.create_list_product_mocks(user)
        database_transport.get_products_by_refs.return_value = []
        tg_update.message.chat.id = "chat_id"
        bot_client.list_product(tg_update, tg_context)

        database_transport.get_products_by_refs.assert_called_once_with(
            [],
            return_default_if_not_found=True
        )
        bot_client.send_messages.assert_called_once_with(
            telegram_bot,
            "chat_id",
            [(MessageID.PRODUCT_LIST_EMPTY, {})],
            keyboard=None
        )

    def test_list_products_from_button(self):
        prs = [ProductRef(Platform.AMAZON_JP, f"p{i+1}") for i in range(13)]
        ps = [Product(pr) for pr in prs]
        for i, p in enumerate(ps):
            p.name = f"Product {i+1}"
        prs_to_show = prs[10:]
        ps_to_show = ps[10:]
        user = User("chat_id", subscribed=prs)
        (
            telegram_bot,
            database_transport,
            tg_update,
            tg_context,
            bot_client
        ) = self.create_list_product_mocks(user)
        database_transport.get_products_by_refs.return_value = ps_to_show
        tg_update.message = None
        tg_update.callback_query.message.chat_id = "chat_id"
        tg_update.callback_query.message.message_id = "message_id"
        tg_update.callback_query.data = "/list 2"
        bot_client.list_product(tg_update, tg_context)

        database_transport.get_products_by_refs.assert_called_once_with(
            prs_to_show,
            return_default_if_not_found=True
        )
        bot_client.update_with_messages.assert_called_once_with(
            telegram_bot,
            "chat_id",
            "message_id",
            [
                (MessageID.PRODUCT_LIST_HEADER, {}),
                (
                    MessageID.PRODUCT_LIST_ITEM,
                    {
                        "i": 1,
                        "url": ANY,
                        "platform": Platform.AMAZON_JP.value,
                        "name": "Product 11",
                        "status": ProductStatus.UNKNOWN.value
                    },
                ),
                (
                    MessageID.PRODUCT_LIST_ITEM,
                    {
                        "i": 2,
                        "url": ANY,
                        "platform": Platform.AMAZON_JP.value,
                        "name": "Product 12",
                        "status": ProductStatus.UNKNOWN.value
                    }
                ),
                (
                    MessageID.PRODUCT_LIST_ITEM,
                    {
                        "i": 3,
                        "url": ANY,
                        "platform": Platform.AMAZON_JP.value,
                        "name": "Product 13",
                        "status": ProductStatus.UNKNOWN.value
                    }
                )
            ],
            keyboard=[
                [
                    (
                        (MessageID.BUTTON_FIRST, {}),
                        "/list 0"
                    ),
                    (
                        (
                            MessageID.INTEGER,
                            {"value": 1}
                        ),
                        "/list 0"
                    ),
                    (
                        (
                            MessageID.INTEGER,
                            {"value": 2}
                        ),
                        "/list 1"
                    ),
                    (
                        (
                            MessageID.INTEGER_WITH_BRACKETS,
                            {"value": 3}
                        ),
                        "/list 2"
                    )
                ],
                [
                    (
                        (
                            MessageID.BUTTON_REMOVE,
                            {"id": 1}
                        ),
                        "/unsubscribe AMAZON_JP p11"
                    ),
                    (
                        (
                            MessageID.BUTTON_REMOVE,
                            {"id": 2}
                        ),
                        "/unsubscribe AMAZON_JP p12"
                    ),
                    (
                        (
                            MessageID.BUTTON_REMOVE,
                            {"id": 3}
                        ),
                        "/unsubscribe AMAZON_JP p13"
                    )
                ]
            ]
        )

    def test_unsubscribe_product_fail(self):
        user = User("chat_id", subscribed=[])
        (
            telegram_bot,
            database_transport,
            tg_update,
            tg_context,
            bot_client
        ) = self.create_list_product_mocks(user)
        tg_update.message = None
        tg_update.callback_query.message.chat_id = "chat_id"
        tg_update.callback_query.message.message_id = "message_id"
        tg_update.callback_query.data = "/unsubscribe AMAZON_JP p1"
        bot_client.unsubscribe(tg_update, tg_context)
        bot_client.send_messages.assert_called_once_with(
            telegram_bot,
            "chat_id",
            [(MessageID.NOT_SUBSCRIBED, {})]
        )

    def test_unsubscribe_products_from_button(self):
        prs = [ProductRef(Platform.AMAZON_JP, f"p{i+1}") for i in range(13)]
        ps = [Product(pr) for pr in prs]
        for i, p in enumerate(ps):
            p.name = f"Product {i+1}"
        user = User("chat_id", subscribed=prs)
        (
            telegram_bot,
            database_transport,
            tg_update,
            tg_context,
            bot_client
        ) = self.create_list_product_mocks(user)
        # telegram update for unsubscribing product
        tg_update.message = None
        tg_update.callback_query.id = "query_id"
        tg_update.callback_query.message.chat_id = "chat_id"
        tg_update.callback_query.message.message_id = "message_id"
        tg_update.callback_query.data = "/unsubscribe AMAZON_JP p11"
        remaining_prs = [pr for pr in prs if pr.id != "p11"]
        remaining_ps = [p for p in ps if p.id != "p11"]

        # products to list after unsubscribing
        database_transport.get_products_by_refs.return_value = remaining_ps[10:]  # noqa: E501

        bot_client.unsubscribe(tg_update, tg_context)
        database_transport.save_user.assert_called_once_with(UserMatcher(
            User("chat_id", subscribed=remaining_prs)
        ))
        bot_client.answer_query.assert_called_once_with(
            telegram_bot,
            "query_id",
            MessageID.UNSUBSCRIBED
        )
        bot_client.update_with_messages.assert_called_once_with(
            telegram_bot,
            "chat_id",
            "message_id",
            [
                (MessageID.PRODUCT_LIST_HEADER, {}),
                (
                    MessageID.PRODUCT_LIST_ITEM,
                    {
                        "i": 1,
                        "url": ANY,
                        "platform": Platform.AMAZON_JP.value,
                        "name": "Product 12",
                        "status": ProductStatus.UNKNOWN.value
                    },
                ),
                (
                    MessageID.PRODUCT_LIST_ITEM,
                    {
                        "i": 2,
                        "url": ANY,
                        "platform": Platform.AMAZON_JP.value,
                        "name": "Product 13",
                        "status": ProductStatus.UNKNOWN.value
                    }
                )
            ],
            keyboard=[
                [
                    (
                        (MessageID.BUTTON_FIRST, {}),
                        "/list 0"
                    ),
                    (
                        (
                            MessageID.INTEGER,
                            {"value": 1}
                        ),
                        "/list 0"
                    ),
                    (
                        (
                            MessageID.INTEGER,
                            {"value": 2}
                        ),
                        "/list 1"
                    ),
                    (
                        (
                            MessageID.INTEGER_WITH_BRACKETS,
                            {"value": 3}
                        ),
                        "/list 2"
                    )
                ],
                [
                    (
                        (
                            MessageID.BUTTON_REMOVE,
                            {"id": 1}
                        ),
                        "/unsubscribe AMAZON_JP p12"
                    ),
                    (
                        (
                            MessageID.BUTTON_REMOVE,
                            {"id": 2}
                        ),
                        "/unsubscribe AMAZON_JP p13"
                    )
                ]
            ]
        )
