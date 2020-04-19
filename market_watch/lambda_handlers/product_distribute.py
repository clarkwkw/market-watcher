import logging
from ..transport import (
    MessageQueueImpl,
    DatabaseTransportImpl,
    DatabaseTransport,
    MessageQueue
)
from .response import OK_RESPONSE
from ..config import construct_config_from_env
from ..utils import configure_logger
from ..models import ProductStatus
from ..setup import create_mongo_client

configure_logger()
logger = logging.getLogger(__name__)


def _distribute_products(
    db_transport: DatabaseTransport,
    message_queue: MessageQueue,
):
    products = db_transport.get_all_subscribed_products()
    logging.info(f"Retrieved {len(products)} products.")
    products = [p for p in products if p.status != ProductStatus.NOT_FOUND]
    logging.info(f"Remaining {len(products)} products after "
                 "filitering out previously not found ones.")
    message_queue.enqueue(products)
    logging.info(f"Enqueued.")


def distribute_products_handler(event, context, config=None):
    if config is None:
        config = construct_config_from_env()

    db_transport = DatabaseTransportImpl(
        create_mongo_client(config["mongo_uri"]),
        config["mongo_db_name"]
    )
    message_queue = MessageQueueImpl(
        config,
        "Market-Watch-Product-Distribute"
    )
    _distribute_products(db_transport, message_queue)
    return OK_RESPONSE
