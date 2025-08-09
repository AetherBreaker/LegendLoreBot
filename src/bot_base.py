if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

from logging import getLogger

import cogs
from database.cache import DatabaseCache
from disnake import Intents
from disnake.ext.commands import Bot
from environment_init_vars import OWNER_IDS, TEST_GUILDS

logger = getLogger(__name__)


class SwallowBot(Bot):
  database: DatabaseCache

  def __init__(self, *args, **kwargs):
    self.load_extensions(cogs.__name__)

    intents = Intents.default()
    intents.message_content = True
    super().__init__(
      *args,
      **kwargs,
      intents=intents,
      owner_ids=OWNER_IDS,
      test_guilds=TEST_GUILDS,
      reload=bool(__debug__),
    )

  async def on_ready(self):
    self.database = DatabaseCache()
    print(f"Logged on as {self.user}!")
