if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

from logging import getLogger

from bot_base import SwallowBot
from disnake import ApplicationCommandInteraction
from disnake.ext.commands import Cog, slash_command

logger = getLogger(__name__)


class StaffCommands(Cog):
  def __init__(self, bot):
    self.bot = bot
    self._last_member = None

  @slash_command()
  async def staff(self, _: ApplicationCommandInteraction): ...

  @staff.sub_command_group()
  async def characters(self, _: ApplicationCommandInteraction): ...

  ...

  @staff.sub_command_group()
  async def coins(self, _: ApplicationCommandInteraction): ...

  ...

  @staff.sub_command_group()
  async def servercoins(self, _: ApplicationCommandInteraction): ...

  ...


def setup(bot: SwallowBot):
  bot.add_cog(StaffCommands(bot))
  print("StaffCommands loaded.")
