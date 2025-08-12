if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

from logging import getLogger

from cogs.character import CharacterTracking
from cogs.dbcache_refresh_hooks import DatabaseCacheCog
from cogs.staff import StaffCommands
from database.cache import DatabaseCache
from disnake import Intents
from disnake.ext.commands import Bot
from environment_init_vars import OWNER_IDS, TEST_GUILDS

logger = getLogger(__name__)


class SwallowBot(Bot):
  database: DatabaseCache

  def __init__(self, *args, **kwargs):
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

    self.add_cog(CharacterTracking(self))
    self.add_cog(DatabaseCacheCog(self))
    self.add_cog(StaffCommands(self))

  async def on_ready(self):
    self.database = DatabaseCache()
    await self.database._refresh_cache()
    print(f"Logged on as {self.user}!")
