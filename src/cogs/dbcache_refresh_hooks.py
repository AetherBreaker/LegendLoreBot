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
    ...
    # TODO

  @refresh_cache_task.before_loop
  async def before_refresh_cache(self) -> None:
    """
    Wait until the bot is ready before starting the cache refresh task.
    """
    await self.bot.wait_until_ready()
    await sleep(SETTINGS.database_refresh_interval)
