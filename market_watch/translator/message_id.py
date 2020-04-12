import enum


class MessageID(enum.Enum):
    HELLO = 0
    ERROR = 1
    INVALID_PRODUCT_LIST_FORMAT = 2
    INVALID_PRODUCT_PLATFORMS = 3
    PRODUCT_SUBSCRIBED = 4
    PRODUCT_NOTIFY_HEADER = 5
    PRODUCT_NOTIFY_UPDATED = 6
    PRODUCT_NOTIFY_NOT_FOUND = 7
    PRODUCT_NOTIFY_FOOTER = 8
