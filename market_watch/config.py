import os


def construct_config_from_env() -> dict:
    return {
        "mongo_uri":        os.environ["MARKET_WATCH_MONGO_URI"],
        "mongo_db_name":    os.environ["MARKET_WATCH_MONGO_DB_NAME"],
        "tg_token":         os.environ["MARKET_WATCH_TG_TOKEN"],
        "within_lambda":    bool(os.environ["MARKET_WATCH_WITHIN_LAMBDA"]),
        "sqs": {
            "region_name":  os.environ.get("MARKET_WATCH_SQS_REGION_NAME", ""),
            "access_key":   os.environ.get("MARKET_WATCH_SQS_ACCESS_KEY", ""),
            "secret_key":   os.environ.get("MARKET_WATCH_SQS_SECRET_KEY", ""),
            "queue_name":   os.environ.get("MARKET_WATCH_SQS_QUEUE_NAME", ""),
        }
    }
