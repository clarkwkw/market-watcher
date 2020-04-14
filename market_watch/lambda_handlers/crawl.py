import logging
from ..transport import (
    HTTPTransportImpl,
    DatabaseTransportImpl,
    MessageQueueImpl
)
from ..crawlers import all_crawlers
from ..models import ProductStatus
from .response import OK_RESPONSE
from ..config import construct_config_from_env
from ..utils import configure_logger

configure_logger()
logger = logging.getLogger(__name__)


def crawl_products_handler(event, context, config=None):
    if config is None:
        config = construct_config_from_env()

    db_transport = DatabaseTransportImpl(
        config["mongo_uri"],
        config["mongo_db_name"]
    )
    http_transport = HTTPTransportImpl()
    message_queue = MessageQueueImpl(
        config,
        "Market-Watch-Product-Notify"
    )
    crawlers = {}
    for cls in all_crawlers:
        crawlers[cls.platform] = cls(http_transport)

    product_refs = MessageQueueImpl.deserialize(event)
    logging.info(f"Assigned {len(product_refs)} products.")
    products = db_transport.get_products_by_refs(
        MessageQueueImpl.deserialize(event),
        return_default_if_not_found=True
    )
    logging.info(f"Retrieved {len(products)} products from database.")
    products_to_notify = []
    updated_products = []
    for p in products:
        updated = crawlers[p.platform].get_product(p.id)
        if p.status != updated.status:
            # preserve original name if blocked marketplace
            updated.name = updated.name if len(updated.name) else p.name
            updated_products.append(updated)
            if updated.status == ProductStatus.AVAILABLE \
                    or updated.status == ProductStatus.NOT_FOUND:
                products_to_notify.append(updated)

    logging.info(f"Updated {len(updated_products)} products.")
    logging.info(f"Going to notify {len(products_to_notify)} products.")
    db_transport.save_products(updated_products)
    message_queue.enqueue(products_to_notify)
    return OK_RESPONSE
