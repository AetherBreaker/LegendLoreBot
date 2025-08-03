if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

from bot_base import SwallowBot
from disnake import Intents
from environment_init_vars import SETTINGS

if __name__ == "__main__":
  client = SwallowBot()
  client.run(SETTINGS.token)
