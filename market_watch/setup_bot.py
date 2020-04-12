import re
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from .bot import TelegramBot
from .transport import DatabaseTransport
from .translator import Translator


def create_tg_bot(
    token: str,
    database: DatabaseTransport,
    translator: Translator
):
    updater = Updater(
        token,
        request_kwargs={'read_timeout': 10, 'connect_timeout': 10},
        use_context=True
    )
    bot = TelegramBot(database, translator)
    updater.dispatcher.add_handler(CommandHandler(
        "start",
        bot.create_user
    ))
    updater.dispatcher.add_handler(MessageHandler(
        Filters.regex(re.compile(r"^\s*/subscribe(\s.*)?$")),
        bot.subscibe_product
    ))
    return bot, updater
