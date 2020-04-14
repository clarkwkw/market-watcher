import logging
import re
from typing import List
from .models import ProductRef, Platform
from .exceptions import InvalidInputException
from .translator import MessageID


SEPARATOR = re.compile(r"[\s\n]+")


def parse_product_list_input(input: str) -> List[ProductRef]:
    tokens = SEPARATOR.split(input.strip())
    if len(tokens) % 2 != 0:
        raise InvalidInputException(MessageID.INVALID_PRODUCT_LIST_FORMAT)

    product_refs = []
    for i in range(0, len(tokens), 2):
        platform = tokens[i].upper()
        product_id = tokens[i+1]
        if not Platform.is_valid(platform):
            raise InvalidInputException(
                MessageID.INVALID_PRODUCT_PLATFORMS,
                message_args={
                    "platforms": platform
                }
            )
        product_refs.append(ProductRef(platform, product_id))
    return product_refs


def configure_logger():
    root = logging.getLogger()
    if root.handlers:
        for handler in root.handlers:
            root.removeHandler(handler)
    logging.basicConfig(
        format='%(levelname)s - %(message)s',
        level=logging.INFO
    )
