import os
from logging.config import dictConfig
from logram.handlers import Telegram
import os
from dotenv import load_dotenv

load_dotenv()


Telegram.token = os.getenv("TELEGRAM_TOKEN")
Telegram.chat_id = os.getenv("TELEGRAM_CHAT_ID")

log_file_path = os.path.abspath(os.path.join(".", os.pardir)) + "/logs/log"
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[%(levelname)s] [%(asctime)s] [%(module)s] [line:%(lineno)d] %(message)s"
        },
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": log_file_path,
            "formatter": "verbose",
            "encoding": "UTF-8",
        },
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "telegram": {
            "level": "WARNING",
            "class": "logram.handlers.Telegram",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO", "propagate": True},
        "offices": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "indicators": {
            "handlers": ["console", "telegram", "file"],
            "level": "INFO",
            "propagate": True,
        },
        "qinspect": {"handlers": ["console"], "level": "INFO", "propagate": True,},
    },
}

dictConfig(LOGGING)


TIMESTREAM_DATABASE = "coinmove"
TIMESTREAM_DATABASE_TEST = "coinmove_test"
TIMESTREAM_TABLE = "technical_data"
TIMESTREAM_TABLE_TEST = "technical_data_test"
