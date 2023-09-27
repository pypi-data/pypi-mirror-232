from asbool import asbool
from loguru import logger
from stela import env

from coraline.config import CoralConfig
from coraline.field import KeyField, TTLField
from coraline.model import CoralModel
from coraline.types import BillingMode, HashType

__version__ = "0.2.2"

__all__ = [
    "CoralModel",
    "KeyField",
    "BillingMode",
    "HashType",
    "CoralConfig",
    "TTLField",
]

if asbool(env.get_or_default("CORALINE_SHOW_LOGS", True)):
    logger.enable("coraline")
else:
    logger.disable("coraline")
