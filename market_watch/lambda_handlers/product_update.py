import logging
import telegram
from typing import List
from ..bot import TelegramBotClient
from ..models import ProductRef
from ..setup import create_tg_bot_client
from ..translator import Translator
from ..transport import DatabaseTransportImpl, MessageQueueImpl
from .response import OK_RESPONSE
from ..config import construct_config_from_env
from ..setup import create_mongo_client
from ..utils import configure_logger

configure_logger()
logger = logging.getLogger(__name__)


def _handle_product_update(
    bot_client: TelegramBotClient,
    telegram_bot: telegram.Bot,
    product_refs: List[ProductRef]
):

    logger.info(f"Received {len(product_refs)} products to notify.")
    bot_client.notify_status_update(telegram_bot, product_refs)
    logger.info("Notified.")


def product_update_handler(event, context, config=None):
    if config is None:
        config = construct_config_from_env()

    database = DatabaseTransportImpl(
        create_mongo_client(config["mongo_uri"]),
        config["mongo_db_name"]
    )
    client, updater = create_tg_bot_client(
        config["tg_token"], database, Translator()
    )

    _handle_product_update(
        client,
        updater.bot,
        MessageQueueImpl.deserialize(event)
    )

    return OK_RESPONSE
