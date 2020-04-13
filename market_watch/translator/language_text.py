from .message_id import MessageID
from .language import Language

EN = {
    MessageID.ERROR: "Error",
    MessageID.HELLO:  "Welcome!",
    MessageID.INVALID_PRODUCT_LIST_FORMAT: "Invalid format. Format: /subscribe [platform_1] [product_1] [platform_2] [product_2]...",
    MessageID.INVALID_PRODUCT_PLATFORMS: "Invalid platform: {platforms}",
    MessageID.PRODUCT_SUBSCRIBED: "Subscribed to these products",
    MessageID.PRODUCT_NOTIFY_HEADER: "Product updated:\n",
    MessageID.PRODUCT_NOTIFY_UPDATED: "- <a href='{url}'>{platform}: {name}</a>: {status}\n",
    MessageID.PRODUCT_NOTIFY_NOT_FOUND: "- {platform}-{id}: Not found\n",
    MessageID.PRODUCT_NOTIFY_FOOTER: ""
}

LANGUAGES = {
    Language.EN: EN
}
