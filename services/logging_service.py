import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from core.credentials import redact


class SafeFormatter(logging.Formatter):
    def format(self, record):
        return redact(super().format(record))


def configure_logging(path):
    logger = logging.getLogger('desktop')
    if not logger.handlers:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        handler = RotatingFileHandler(path, maxBytes=1024 * 1024, backupCount=3, encoding='utf-8')
        handler.setFormatter(SafeFormatter('%(asctime)s %(levelname)s %(message)s'))
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
    return logger
