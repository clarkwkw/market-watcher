import json
from ..setup_bot import create_tg_bot_client
from ..translator import Translator
from ..transport import DatabaseTransportImpl, MessageQueueImpl
from .response import OK_RESPONSE


def product_update_handler(event, context):
    with open("config/config.json", "r") as f:
        config = json.load(f)

    database = DatabaseTransportImpl(
        config["mongo_uri"],
        config["mongo_db_name"]
    )
    client, updater = create_tg_bot_client(
        config["tg_token"], database, Translator()
    )

    client.notify_status_update(
        updater.bot, MessageQueueImpl.parse_sqs_notification(event)
    )

    return OK_RESPONSE
