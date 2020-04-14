import logging
from ..transport import MessageQueueImpl, DatabaseTransportImpl
from .response import OK_RESPONSE
from ..config import construct_config_from_env
from ..utils import configure_logger

configure_logger()
logger = logging.getLogger(__name__)


def distribute_products_handler(event, context, config=None):
    if config is None:
        config = construct_config_from_env()

    db_transport = DatabaseTransportImpl(
        config["mongo_uri"],
        config["mongo_db_name"]
    )
    message_queue = MessageQueueImpl(
        config,
        "Market-Watch-Product-Distribute"
    )
    products = db_transport.get_all_subscribed_products()
    logging.info(f"Retrieved {len(products)} products.")
    message_queue.enqueue(products)
    logging.info(f"Enqueued.")
    return OK_RESPONSE
