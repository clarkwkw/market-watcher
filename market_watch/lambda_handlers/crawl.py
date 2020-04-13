from ..transport import (
    HTTPTransportImpl,
    DatabaseTransportImpl,
    MessageQueueImpl
)
from ..crawlers import all_crawlers
from ..models import ProductStatus
from .response import OK_RESPONSE
from ..config import construct_config_from_env


def crawl_products_handler(event, context, config=None):
    if config is None:
        config = construct_config_from_env()

    db_transport = DatabaseTransportImpl(
        config["mongo_uri"],
        config["mongo_db_name"]
    )
    http_transport = HTTPTransportImpl()
    message_queue = MessageQueueImpl(config["sqs"])
    crawlers = {}
    for cls in all_crawlers:
        crawlers[cls.platform] = cls(http_transport)

    products = db_transport.get_all_subscribed_products()
    products_to_notify = []
    updated_products = []
    for p in products:
        updated = crawlers[p.platform].get_product(p.id)
        updated_products.append(updated)
        if p.status != updated.status:
            updated_products.append(updated)
            if updated.status == ProductStatus.AVAILABLE \
                    or updated.status == ProductStatus.NOT_FOUND:
                products_to_notify.append(updated)
    db_transport.save_products(updated_products)
    message_queue.notify_updates(products_to_notify)
    return OK_RESPONSE
