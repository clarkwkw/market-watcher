import logging
from ..setup_bot import create_tg_bot_client
from ..translator import Translator
from ..transport import DatabaseTransportImpl, MessageQueueImpl
from .response import OK_RESPONSE
from ..config import construct_config_from_env
from ..utils import configure_logger

configure_logger()
logger = logging.getLogger(__name__)


def product_update_handler(event, context, config=None):
    if config is None:
        config = construct_config_from_env()

    database = DatabaseTransportImpl(
        config["mongo_uri"],
        config["mongo_db_name"]
    )
    client, updater = create_tg_bot_client(
        config["tg_token"], database, Translator()
    )
    product_refs = MessageQueueImpl.deserialize(event)

    logger.info(f"Received {len(product_refs)} products to notify.")
    client.notify_status_update(updater.bot, product_refs)
    logger.info("Notified.")

    return OK_RESPONSE
