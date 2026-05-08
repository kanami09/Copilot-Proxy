from mitmproxy import log
from loguru import logger


class ProxyLogger:
    def log(self, entry: log.LogEntry):
        match entry.level:
            case "debug":
                logger.debug(entry.msg)
            case "info":
                logger.info(entry.msg)
            case "warn":
                logger.warning(entry.msg)
            case "error":
                logger.error(entry.msg)
            case _:
                logger.info(entry.msg)
