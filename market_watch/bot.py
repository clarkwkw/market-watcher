import math
import telegram
import telegram.ext
from typing import List, Dict, Tuple, Any, Optional
from .models import User, ProductRef, ProductStatus, Platform
from .transport import DatabaseTransport
from .translator import Translator, MessageID
from .exceptions import MWException, InvalidInputException
from .crawlers import all_crawlers_map
from . import utils

NON_SPACE_INPUT = "[^\\s]+"
PRODUCT_SUBSCIBE_REGEX = f"^\\s*/{NON_SPACE_INPUT}\\s+(.*)"
SUBSCRIBED_LIST_PAGE_SIZE = 5
SUBSCRIBED_LIST_NEIGHBOR_PAGES = 2
Message = Tuple[MessageID, Dict[str, Any]]
Messages = List[Message]
Keyboard = List[List[Tuple[Message, str]]]


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

    def _convert_messages_to_str(
        self,
        messages: Messages
    ) -> str:
        message_strs = [
            self.translator.translate(id, **kwargs)
            for id, kwargs in messages
        ]
        return "".join(message_strs)

    def _convert_keyboard_to_tg_keyboard(
        self,
        keyboard: Keyboard
    ) -> telegram.InlineKeyboardMarkup:
        tg_rows = []
        for row in keyboard:
            tg_row = []
            for (message_id, kwargs), callback_data in row:
                tg_row.append(telegram.InlineKeyboardButton(
                    self.translator.translate(message_id, **kwargs),
                    callback_data=callback_data
                ))
            tg_rows.append(tg_row)
        return telegram.InlineKeyboardMarkup(tg_rows)

    def send_messages(
            self,
            tg_bot: telegram.Bot,
            chat_id: str,
            messages: Messages,
            keyboard: Optional[Keyboard] = None
    ):

        tg_bot.send_message(
            chat_id,
            self._convert_messages_to_str(messages),
            parse_mode=telegram.ParseMode.HTML,
            reply_markup=self._convert_keyboard_to_tg_keyboard(keyboard)
            if keyboard is not None else None
        )

    def update_with_messages(
        self,
        tg_bot: telegram.Bot,
        chat_id: str,
        message_id: str,
        messages: Messages,
        keyboard: Optional[Keyboard] = None
    ):
        tg_bot.edit_message_text(
            self._convert_messages_to_str(messages),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=self._convert_keyboard_to_tg_keyboard(keyboard)
            if keyboard is not None else None
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
            messages: Messages = []
            messages.append((
                MessageID.PRODUCT_NOTIFY_HEADER, {}
            ))
            for product_ref in user.subscribed:
                if product_ref not in products:
                    continue
                updated_product = products[product_ref]
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

    @handle_excpetion
    def unsubscribe(
        self,
        tg_update: telegram.Update,
        tg_context: telegram.ext.CallbackContext
    ):
        user = self._get_or_create_user(
            tg_update.callback_query.message.chat_id
        )

        command, raw_platform, raw_id = tg_context.data.split(" ")
        if command != "/unsubscribe":
            return

        if not Platform.is_valid(raw_platform):
            raise InvalidInputException(
                MessageID.INVALID_PRODUCT_PLATFORMS,
                {"platforms": raw_platform}
            )
        product_ref = ProductRef(Platform(raw_platform), raw_id)
        try:
            subscribed_index = user.subscribed.index(product_ref)
        except ValueError:
            raise InvalidInputException(MessageID.NOT_SUBSCRIBED)
        user.subscribed.pop(subscribed_index)
        self.database.save_user(user)
        tg_update.callback_query.answer(
            self.translator.translate(MessageID.UNSUBSCRIBED)
        )
        messages, keyboard = self._generate_subscribed_list_and_navigations(
            user, subscribed_index//SUBSCRIBED_LIST_PAGE_SIZE
        )
        self.update_with_messages(
            tg_context.bot,
            user.chat_id,
            tg_update.callback_query.message.message_id,
            messages,
            keyboard=keyboard
        )

    @handle_excpetion
    def list_product(
        self,
        tg_update: telegram.Update,
        tg_context: telegram.ext.CallbackContext
    ):
        user = self._get_or_create_user(tg_update.message.chat.id)
        args = tg_context.args
        offset = 0
        if len(args) == 1:
            try:
                offset = int(args[0])
            except Exception:
                pass
        messages, keyboard = self._generate_subscribed_list_and_navigations(
            user, offset
        )
        self.send_messages(
            tg_context.bot,
            user.chat_id,
            messages,
            keyboard=keyboard
        )

    def _generate_subscribed_list_and_navigations(
        self,
        user: User,
        offset: int
    ) -> Tuple[Messages, Optional[Keyboard]]:
        st_index = offset*SUBSCRIBED_LIST_PAGE_SIZE
        if st_index >= len(user.subscribed):
            st_index = 0
        ed_index = min(
            st_index + SUBSCRIBED_LIST_PAGE_SIZE,
            len(user.subscribed)
        )
        products = self.database.get_products_by_refs(
            user.subscribed[st_index:ed_index]
        )
        if len(products) == 0:
            return [(MessageID.PRODUCT_LIST_EMPTY, {})], None
        messages: Messages = [(MessageID.PRODUCT_LIST_HEADER, {})]
        for i, p in enumerate(products):
            messages.append((
                MessageID.PRODUCT_LIST_ITEM,
                {
                    "i": i + 1,
                    "url": all_crawlers_map[p.platform].get_product_url(p.id),
                    "platform": p.platform,
                    "name": p.name,
                    "status": p.status.value
                }
            ))
        keyboard: Keyboard = [[], []]
        n_pages = math.ceil(len(user.subscribed)/SUBSCRIBED_LIST_PAGE_SIZE)
        if offset != 0:
            keyboard[0].append((
                (MessageID.BUTTON_FIRST, {}),
                f"/list 0"
            ))
        for i in range(
            max(offset-SUBSCRIBED_LIST_NEIGHBOR_PAGES, 0),
            min(offset+SUBSCRIBED_LIST_NEIGHBOR_PAGES+1, n_pages)
        ):
            keyboard[0].append((
                (
                    MessageID.INTEGER if i != offset else
                    MessageID.INTEGER_WITH_BRACKETS,
                    {"value": i+1}
                ),
                f"/list {i}"
            ))
        if offset != n_pages - 1:
            keyboard[0].append((
                (MessageID.BUTTON_LAST, {}),
                f"/list {n_pages - 1}"
            ))
        for i, p in enumerate(products):
            keyboard[1].append((
                (MessageID.BUTTON_REMOVE, {"id": i+1}),
                f"/unsubscribe {p.platform} {p.id}"
            ))
        return messages, keyboard
