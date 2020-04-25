import logging
import random
from time import sleep
from ..transport import (
    HTTPTransportImpl,
    DatabaseTransportImpl,
    MessageQueueImpl,
    HTTPTransport,
    DatabaseTransport,
    MessageQueue
)
from ..crawlers import all_crawlers
from ..models import ProductStatus, ProductRef
from .response import OK_RESPONSE
from ..config import construct_config_from_env
from ..setup import create_mongo_client
from ..utils import configure_logger
from typing import List

configure_logger()
logger = logging.getLogger(__name__)


def _crawl_products(
    db_transport: DatabaseTransport,
    http_transport: HTTPTransport,
    message_queue: MessageQueue,
    product_refs: List[ProductRef]
):
    crawlers = {}
    for cls in all_crawlers:
        crawlers[cls.platform] = cls(http_transport)

    logging.info(f"Assigned {len(product_refs)} products.")
    products = db_transport.get_products_by_refs(
        product_refs,
        return_default_if_not_found=True
    )
    logging.info(f"Retrieved {len(products)} products from database.")
    product_refs_to_notify = []
    updated_products = []
    for p in products:
        sleep(random.uniform(1, 2.5))
        updated = crawlers[p.platform].get_product(p.id)
        if updated.status != ProductStatus.UNKNOWN\
                and p.status != updated.status:
            # preserve original name if blocked marketplace
            updated.name = updated.name if len(updated.name) else p.name
            updated_products.append(updated)
            if updated.status == ProductStatus.AVAILABLE \
                    or updated.status == ProductStatus.NOT_FOUND:
                product_refs_to_notify.append(updated.product_ref)

    logging.info(f"Updated {len(updated_products)} products.")
    logging.info(f"Going to notify {len(product_refs_to_notify)} products.")
    db_transport.save_products(updated_products)
    message_queue.enqueue(product_refs_to_notify)


def crawl_products_handler(event, context, config=None):
    if config is None:
        config = construct_config_from_env()

    db_transport = DatabaseTransportImpl(
        create_mongo_client(config["mongo_uri"]),
        config["mongo_db_name"]
    )
    http_transport = HTTPTransportImpl()
    message_queue = MessageQueueImpl(
        config,
        "Market-Watch-Product-Notify"
    )

    _crawl_products(db_transport, http_transport, message_queue)
    return OK_RESPONSE
