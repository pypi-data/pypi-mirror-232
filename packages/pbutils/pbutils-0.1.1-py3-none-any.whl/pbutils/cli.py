import enum
import logging
import sys

import click
from loguru import logger

from pbutils.enum_choice import EnumChoice
from pbutils.html2md import html2md
from pbutils.pb2html import pb2html


@enum.unique
class LogLevel(enum.Enum):
    debug = logging.DEBUG
    info = logging.INFO
    warning = logging.WARNING
    error = logging.ERROR
    critical = logging.CRITICAL


def _setup_logger(log_level: LogLevel) -> None:
    logger.configure(handlers=[{"sink": sys.stdout, "level": log_level.value}])


@click.command()
@click.option("--log-level", type=EnumChoice(LogLevel), default=LogLevel.info.name)
def cli(log_level: LogLevel) -> None:
    _setup_logger(log_level=log_level)
    print(html2md(pb2html()))
