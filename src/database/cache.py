from asyncio import sleep

from bot_base import SwallowBot
from disnake.ext.commands import Cog
from disnake.ext.tasks import loop
from environment_init_vars import SETTINGS
from typing_custom.abc import SingletonType


class DatabaseCache(metaclass=SingletonType):
  def __init__(self) -> None: ...

  async def refresh_cache(self) -> None: ...


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
