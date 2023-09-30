import logging
from dataclasses import dataclass
import os

from deepaix.common.datetime import get_today
from deepaix.common.utils import setup_dir_for_file_path


STD_FORMATTER = logging.Formatter(
    '%(levelname)s %(name)s - "%(pathname)s", line %(lineno)d, in %(module)s - %(funcName)s \n  %(message)s'
)
FILE_FORMATTER = logging.Formatter(
    '%(asctime)s - %(levelname)s %(name)s - "%(pathname)s", line %(lineno)d, in %(module)s - %(funcName)s \n  %(message)s'
)


class ColoredFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[36m",
        "INFO": "\033[32m",
        "WARN": "\033[33m",
        "WARNING": "\033[33m",
        "ERROR": "\033[31m",
        "CRITICAL": "\033[31m\033[1m",
        "RESET": "\033[0m",
    }

    def format(self, record):
        log_message = super().format(record)
        log_level = record.levelname

        if log_level in self.COLORS:
            colored_message = f"{self.COLORS[log_level]}{record.levelname} -{self.COLORS['RESET']} '{record.pathname}', line {record.lineno}, in {record.module} - {record.funcName} \n  {log_message}"
            return colored_message
        else:
            return '%(levelname)s - "%(pathname)s", line %(lineno)d, in %(module)s - %(funcName)s \n  %(message)s'


class FlushingFileHandler(logging.FileHandler):
    def emit(self, record):
        super().emit(record)
        self.flush()


@dataclass
class StreamHandlerConfig:
    stream_handler: logging.StreamHandler
    logging_level: logging.INFO | logging.DEBUG | logging.ERROR
    formatter: logging.Formatter


def use_logger(name):
    logger = logging.getLogger(name)

    log_level = logging.INFO

    logger.setLevel(log_level)

    [info_log_file_path, error_log_file_path] = [
        setup_log_file(level) for level in ["info", "error"]
    ]

    std_sh_config = StreamHandlerConfig(
        logging.StreamHandler(), log_level, ColoredFormatter()
    )
    info_file_sh_config = StreamHandlerConfig(
        FlushingFileHandler(info_log_file_path), log_level, FILE_FORMATTER
    )
    error_file_sh_config = StreamHandlerConfig(
        FlushingFileHandler(error_log_file_path), logging.ERROR, FILE_FORMATTER
    )

    for sh_config in [std_sh_config, info_file_sh_config, error_file_sh_config]:
        sh = sh_config.stream_handler
        sh.setLevel(sh_config.logging_level)
        sh.setFormatter(sh_config.formatter)

        logger.addHandler(sh)

    return logger


def setup_log_file(level: str):
    if "ENV" not in os.environ:
        raise Exception("ENV is not set: please set ENV in os.environ")

    env = os.environ.get("ENV")
    log_base_dir = os.environ.get("LOG_BASE_DIR", ".log")

    today_str = get_today()

    log_file_path = f"{log_base_dir}/{env}-{today_str}-{level}.log"
    setup_dir_for_file_path(log_file_path)
    return log_file_path
