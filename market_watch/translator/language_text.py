from .message_id import MessageID
from .language import Language

EN = {
    MessageID.ERROR: "Error",
    MessageID.HELLO:  "Welcome!",
    MessageID.INVALID_PRODUCT_LIST_FORMAT: "Invalid format. Format: /subscribe [platform_1] [product_1] [platform_2] [product_2]...",
    MessageID.INVALID_PRODUCT_PLATFORMS: "Invalid platform: {platforms}",
    MessageID.PRODUCT_SUBSCRIBED: "Subscribed to {n_subscribed} products (excluded duplicates)",
    MessageID.PRODUCT_NOTIFY_HEADER: "Product updated:\n",
    MessageID.PRODUCT_NOTIFY_UPDATED: "- <a href='{url}'>{platform}: {name}</a>: {status}\n",
    MessageID.PRODUCT_LIST_HEADER: "You have subscribed to:\n\n",
    MessageID.PRODUCT_LIST_ITEM: "[{i}] <a href='{url}'>{platform}: {name}</a>: {status}\n\n",
    MessageID.PRODUCT_LIST_EMPTY: "You haven't subscribed to any product",
    MessageID.PRODUCT_NOTIFY_NOT_FOUND: "- {platform}-{id}: Not found\n",
    MessageID.PRODUCT_NOTIFY_FOOTER: "",
    MessageID.INTEGER: "{value:d}",
    MessageID.BUTTON_FIRST: "|<",
    MessageID.BUTTON_LAST: ">|",
    MessageID.BUTTON_REMOVE: "❌ {id}",
    MessageID.NOT_SUBSCRIBED: "You haven't subscribed to the product",
    MessageID.UNSUBSCRIBED: "Successfully unsubscribed"
}

LANGUAGES = {
    Language.EN: EN
}
