if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

from logging import getLogger
from typing import Optional

from autocomplete.command_autocompleters import autocomp_charname
from bot_base import SwallowBot
from disnake import ApplicationCommandInteraction, Member, User
from disnake.ext.commands import Cog, Param, message_command, slash_command, user_command

logger = getLogger(__name__)


class CharacterTracking(Cog):
  def __init__(self, bot):
    self.bot = bot
    self._last_member = None

  @slash_command()
  async def characters(self, _: ApplicationCommandInteraction): ...

  @characters.sub_command()
  async def status(
    self,
    inter: ApplicationCommandInteraction,
    character_name: str = Param(autocomplete=autocomp_charname),
  ): ...


def setup(bot: SwallowBot):
  bot.add_cog(CharacterTracking(bot))
  print("CharacterTracking loaded.")
