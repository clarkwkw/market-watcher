import os


def construct_config_from_env() -> dict:
    return {
        "mongo_uri":        os.environ["MARKET_WATCH_MONGO_URI"].strip('"'),
        "mongo_db_name":    os.environ["MARKET_WATCH_MONGO_DB_NAME"].strip('"'),
        "tg_token":         os.environ["MARKET_WATCH_TG_TOKEN"].strip('"'),
        "within_lambda":    bool(os.environ["MARKET_WATCH_WITHIN_LAMBDA"].strip('"'),),
        "sqs": {
            "region_name":  os.environ["MARKET_WATCH_SQS_REGION_NAME"].strip('"'),
            "access_key":   os.environ.get("MARKET_WATCH_SQS_ACCESS_KEY", "").strip('"'),
            "secret_key":   os.environ.get("MARKET_WATCH_SQS_SECRET_KEY", "").strip('"'),
            "queue_url":   os.environ.get("MARKET_WATCH_SQS_QUEUE_URL", "").strip('"'),
        }
    }
