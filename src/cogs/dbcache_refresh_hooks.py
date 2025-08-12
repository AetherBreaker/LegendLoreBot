if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

from asyncio import sleep
from logging import getLogger
from typing import TYPE_CHECKING

from disnake.ext.commands import Cog
from disnake.ext.tasks import loop
from environment_init_vars import SETTINGS

if TYPE_CHECKING:
  from bot_base import SwallowBot

logger = getLogger(__name__)


class DatabaseCacheCog(Cog):
  def __init__(self, bot: "SwallowBot") -> None:
    self.bot = bot
    self.refresh_cache_task.start()
    self.write_changes_task.start()

  def cog_unload(self) -> None:
    """
    Ensure all active database write threads finish joining before unloading the cog.
    """
    ...
    # TODO

  @loop(seconds=SETTINGS.database_refresh_interval)
  async def refresh_cache_task(self) -> None:
    """
    Periodically refresh the database cache.
    """
    await self.bot.database.refresh_cache()
    # TODO

  @refresh_cache_task.before_loop
  async def before_refresh_cache(self) -> None:
    """
    Wait until the bot is ready before starting the cache refresh task.
    """
    await self.bot.wait_until_ready()
    await sleep(SETTINGS.database_refresh_interval)

  @loop(seconds=SETTINGS.database_write_interval)
  async def write_changes_task(self) -> None:
    """
    Periodically write changes to the database.
    """
    await self.bot.database.submit_queued_writes_to_pool()

  @write_changes_task.before_loop
  async def before_write_changes(self) -> None:
    """
    Wait until the bot is ready before starting the write changes task.
    """
    await self.bot.wait_until_ready()
    await sleep(SETTINGS.database_write_interval)


def setup(bot: "SwallowBot"):
  bot.add_cog(DatabaseCacheCog(bot))
  print("DatabaseCacheCog loaded.")
