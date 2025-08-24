if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

from logging import getLogger
from traceback import format_exception

from cogs.character_tracking import CharacterTrackingCog
from cogs.dbcache_refresh_hooks import DatabaseCacheCog
from cogs.gm_cmds import GMCommandsCog
from database.cache import DatabaseCache
from database.db_utils import ensure_guild_exists
from disnake import ApplicationCommandInteraction, Guild, Intents
from disnake.ext.commands import InteractionBot
from environment_init_vars import OWNER_IDS, TEST_GUILDS

logger = getLogger(__name__)


class LegendLoreBot(InteractionBot):
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

    self.add_cog(CharacterTrackingCog(self))
    self.add_cog(DatabaseCacheCog(self))
    self.add_cog(GMCommandsCog(self))

  async def on_ready(self):
    self.database = DatabaseCache()
    await self.database.refresh_cache()
    print(f"Logged on as {self.user}!")

  async def on_guild_join(self, guild: Guild):
    await ensure_guild_exists(guild)

  async def on_slash_command_error(self, interaction: ApplicationCommandInteraction, exception: Exception):
    exc_type, exc_val, exc_tb = type(exception), exception, exception.__traceback__
    logger.error(f"Error occurred in slash command {interaction.application_command}", exc_info=(exc_type, exc_val, exc_tb))
    await interaction.send(
      f"""An error occurred while processing your command.
      Please contact AetherBreaker and share the following traceback
      Traceback:
      ```py
      {"".join(format_exception(exc_type, exc_val, exc_tb))}
      ```"""
    )
