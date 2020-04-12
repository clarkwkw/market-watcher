import re
import telegram
from typing import List
from .models import User, ProductRef, ProductStatus
from .transport import DatabaseTransport
from .translator import Translator, MessageID
from .exceptions import InvalidInputException
from .crawlers import all_crawlers_map
from . import utils

NON_SPACE_INPUT = "[^\\s]+"
PRODUCT_SUBSCIBE_REGEX = f"^\\s*/{NON_SPACE_INPUT}\\s+(.*)$"


class TelegramBot:
    def __init__(
        self,
        database: DatabaseTransport,
        translator: Translator
    ):
        self.database = database
        self.translator = translator

    def get_or_create_user(self, id: str) -> User:
        user = self.database.get_user(id)
        if user is None:
            user = User(id)
            self.database.save_user(user)
        return user

    def send_message(
        self,
        tg_bot: telegram.Bot,
        chat_id: str,
        message_id: MessageID,
        **kwargs
    ):
        tg_bot.send_message(
            chat_id,
            self.translator.translate(message_id, **kwargs)
        )

    def send_message_str(
        self,
        tg_bot: telegram.Bot,
        chat_id: str,
        message: str
    ):
        tg_bot.send_message(chat_id, message)

    def create_user(
        self,
        tg_update: telegram.Update,
        tg_context: telegram.ext.CallbackContext
    ):
        user = self.get_or_create_user(tg_update.message.chat.id)
        self.send_message(tg_context.bot, user.chat_id, MessageID.HELLO)

    def subscibe_product(
        self,
        tg_update: telegram.Update,
        tg_context: telegram.ext.CallbackContext
    ):
        user = self.get_or_create_user(tg_update.message.chat.id)
        match = re.match(PRODUCT_SUBSCIBE_REGEX, tg_update.message.text)
        if match is None:
            raise InvalidInputException(MessageID.INVALID_PRODUCT_LIST_FORMAT)
        product_refs = utils.parse_product_list_input(match.group(1))
        for pr in product_refs:
            if pr not in user.subscribed:
                user.subscribed.append(pr)
        self.database.save_user(user)
        self.send_message(tg_context.bot, user.chat_id,
                          MessageID.PRODUCT_SUBSCRIBED)

    def notify_status_update(
        self,
        tg_bot: telegram.Bot,
        product_refs: List[ProductRef]
    ):
        subscribed_users = self.database.get_subscribed_users(product_refs)
        products = {
            p.product_ref: p for p in
            self.database.get_products_by_refs(product_refs)
        }
        for user in subscribed_users:
            message = self.translator.translate(
                MessageID.PRODUCT_NOTIFY_HEADER
            )
            for product_refs in user.subscribed:
                if product_refs not in products:
                    continue
                updated_product = products[product_refs]
                if updated_product.status == ProductStatus.NOT_FOUND:
                    message += self.translator.translate(
                        MessageID.PRODUCT_NOTIFY_NOT_FOUND,
                        platform=updated_product.product_ref.platform.value,
                        id=updated_product.id
                    )
                else:
                    url = all_crawlers_map[updated_product.platform]\
                        .get_product_url(updated_product.id)
                    message += self.translator.translate(
                        MessageID.PRODUCT_NOTIFY_UPDATED,
                        url=url,
                        platform=updated_product.platform,
                        name=updated_product.name,
                        status=updated_product.status
                    )
            message += self.translator.translate(
                MessageID.PRODUCT_NOTIFY_FOOTER
            )
            print(message)
            self.send_message(tg_bot, user.chat_id, message)
