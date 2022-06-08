import logging

from .settings import get_app_settings

# configure settings object for global settings.
settings = get_app_settings()

# initialize logger, its level and format.
log_format = "%(asctime)s - %(levelname)s - %(message)s - %(filename)s - %(lineno)d"
log_level = logging.INFO
if settings.debug:
    log_level = logging.DEBUG
logging.basicConfig(format=log_format, level=log_level)
log = logging.getLogger(__name__)