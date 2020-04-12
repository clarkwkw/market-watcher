import json
import telegram
from ..setup_bot import create_tg_bot_client, create_tg_updater
from ..transport import DatabaseTransportImpl
from ..translator import Translator
from .response import OK_RESPONSE, ERROR_RESPONSE


def telegram_message_handler(event, context):
    with open("config/config.json", "r") as f:
        config = json.load(f)
    database = DatabaseTransportImpl(
        config["mongo_uri"],
        config["mongo_db_name"]
    )
    client, updater = create_tg_bot_client(
        config["tg_token"], database, Translator()
    )
    if event.get('httpMethod') == 'POST' and event.get('body'):

        update = telegram.Update.de_json(json.loads(event.get('body')), client)

        updater.dispatcher.process_update(update)

        return OK_RESPONSE

    return ERROR_RESPONSE


def telegram_webhook_configuration_handler(event, context):
    with open("config/config.json", "r") as f:
        config = json.load(f)
    _, updater = create_tg_updater(config["tg_token"])
    url = 'https://{}/{}/'.format(
        event.get('headers').get('Host'),
        event.get('requestContext').get('stage'),
    )
    webhook = updater.bot.set_webhook(url)

    if webhook:
        return OK_RESPONSE

    return ERROR_RESPONSE
