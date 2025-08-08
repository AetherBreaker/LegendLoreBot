if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

from logging import getLogger

from bot_base import SwallowBot
from environment_init_vars import SETTINGS

logger = getLogger(__name__)

if __name__ == "__main__":
  client = SwallowBot()
  client.run(SETTINGS.token)
