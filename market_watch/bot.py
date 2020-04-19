import telegram
import telegram.ext
from typing import List, Mapping
from .models import User, ProductRef, ProductStatus
from .transport import DatabaseTransport
from .translator import Translator, MessageID
from .exceptions import MWException
from .crawlers import all_crawlers_map
from . import utils

NON_SPACE_INPUT = "[^\\s]+"
PRODUCT_SUBSCIBE_REGEX = f"^\\s*/{NON_SPACE_INPUT}\\s+(.*)"


def handle_excpetion(func):
    def wrapped(
        bot_client: 'TelegramBotClient',
        tg_update: telegram.Update,
        tg_context: telegram.ext.CallbackContext
    ):
        try:
            return func(bot_client, tg_update, tg_context)
        except MWException as e:
            bot_client.send_message(
                tg_context.bot,
                tg_update.message.chat.id,
                e.exception_message,
                **e.exception_message_args
            )
    return wrapped


class TelegramBotClient:
    def __init__(
        self,
        database: DatabaseTransport,
        translator: Translator
    ):
        self.database = database
        self.translator = translator

    def _get_or_create_user(self, id: str) -> User:
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
            self.translator.translate(message_id, **kwargs),
            parse_mode=telegram.ParseMode.HTML
        )

    def send_messages(
        self,
        tg_bot: telegram.Bot,
        chat_id: str,
        messages: Mapping[MessageID, dict]
    ):
        message_strs = [
            self.translator.translate(id, **kwargs)
            for id, kwargs in messages.items()
        ]
        tg_bot.send_message(
            chat_id,
            "".join(message_strs),
            parse_mode=telegram.ParseMode.HTML
        )

    def create_user(
        self,
        tg_update: telegram.Update,
        tg_context: telegram.ext.CallbackContext
    ):
        user = self._get_or_create_user(tg_update.message.chat.id)
        self.send_message(tg_context.bot, user.chat_id, MessageID.HELLO)

    @handle_excpetion
    def subscibe_product(
        self,
        tg_update: telegram.Update,
        tg_context: telegram.ext.CallbackContext
    ):
        print("hello")
        user = self._get_or_create_user(tg_update.message.chat.id)
        product_refs = utils.parse_product_list_input(
            tg_context.matches[0].group(1)
        )
        n_subscribed = 0
        for pr in product_refs:
            if pr not in user.subscribed:
                n_subscribed += 1
                user.subscribed.append(pr)
        self.database.save_user(user)
        self.send_message(tg_context.bot, user.chat_id,
                          MessageID.PRODUCT_SUBSCRIBED,
                          n_subscribed=n_subscribed)

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
            messages = []
            messages.append((
                MessageID.PRODUCT_NOTIFY_HEADER, {}
            ))
            for product_refs in user.subscribed:
                if product_refs not in products:
                    continue
                updated_product = products[product_refs]
                if updated_product.status == ProductStatus.NOT_FOUND\
                        or updated_product.status == ProductStatus.UNKNOWN:
                    messages.append((
                        MessageID.PRODUCT_NOTIFY_NOT_FOUND,
                        {
                            "platform": updated_product.platform.value,
                            "id": updated_product.id
                        }
                    ))
                else:
                    url = all_crawlers_map[updated_product.platform]\
                        .get_product_url(updated_product.id)
                    messages.append((
                        MessageID.PRODUCT_NOTIFY_UPDATED,
                        {
                            "url": url,
                            "platform": updated_product.platform.value,
                            "name": updated_product.name,
                            "status": updated_product.status.value
                        }
                    ))
            messages.append((MessageID.PRODUCT_NOTIFY_FOOTER, {}))
            self.send_messages(tg_bot, user.chat_id, messages)
