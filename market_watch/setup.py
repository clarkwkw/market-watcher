import re
import ssl
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler
)
import pymongo
from .bot import TelegramBotClient
from .transport import DatabaseTransport
from .translator import Translator


def create_tg_bot_client(
    token: str,
    database: DatabaseTransport,
    translator: Translator
):
    updater = create_tg_updater(token)
    client = TelegramBotClient(database, translator)
    updater.dispatcher.add_handler(CommandHandler(
        "start",
        client.create_user
    ))
    updater.dispatcher.add_handler(CommandHandler(
        "list",
        client.list_product
    ))
    updater.dispatcher.add_handler(MessageHandler(
        Filters.regex(re.compile(r"^\s*/subscribe([\s\n].*)?$", re.DOTALL)),
        client.subscibe_product
    ))
    updater.dispatcher.add_handler(CallbackQueryHandler(
        client.unsubscribe,
        pattern=Filters.regex(re.compile(r"^/unsubscribe.*$", re.DOTALL)),
    ))
    return client, updater


def create_tg_updater(token: str):
    return Updater(
        token,
        request_kwargs={'read_timeout': 10, 'connect_timeout': 10},
        use_context=True
    )


def create_mongo_client(uri: str):
    return pymongo.MongoClient(
        uri,
        ssl_cert_reqs=ssl.CERT_NONE
    )
