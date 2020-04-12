import json
import telegram
from ..setup_bot import create_tg_bot
from ..transport import DatabaseTransportImpl
from ..translator import Translator
from .response import OK_RESPONSE, ERROR_RESPONSE


def telegram_handler(event, context):
    with open("config/config.json", "r") as f:
        config = json.load(f)
    database = DatabaseTransportImpl(
        config["mongo_uri"],
        config["mongo_db_name"]
    )
    bot, updater = create_tg_bot(config["tg_token"], database, Translator())
    if event.get('httpMethod') == 'POST' and event.get('body'):

        update = telegram.Update.de_json(json.loads(event.get('body')), bot)

        updater.dispatcher.process_update(update)

        return OK_RESPONSE

    return ERROR_RESPONSE
