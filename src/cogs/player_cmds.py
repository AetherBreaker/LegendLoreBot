if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

from logging import getLogger
from typing import TYPE_CHECKING

from disnake import ApplicationCommandInteraction
from disnake.ext.commands import Cog, contexts, install_types, slash_command

from cogs.gm_cmds import DatabaseUsersColumns

logger = getLogger(__name__)


if TYPE_CHECKING:
  from bot_base import LegendLoreBot


class PlayerCommandsCog(Cog):
  def __init__(self, bot: "LegendLoreBot"):
    self.bot = bot

  @slash_command()
  @contexts(guild=True, bot_dm=True, private_channel=True)
  @install_types(guild=True, user=True)
  async def bal(self, inter: ApplicationCommandInteraction):
    """Check your balance."""
    # TODO Account for usage in DMs vs guilds
    user_id = inter.author.id
    guild_id = inter.guild_id or 0

    balance = await self.bot.database.users.read_value((user_id, guild_id), DatabaseUsersColumns.server_money)
    if balance is None:
      balance = 0

    # TODO Make this shit prettier
    await inter.send(f"Your balance is {balance} BC.", ephemeral=True)


def setup(bot: "LegendLoreBot"):
  bot.add_cog(PlayerCommandsCog(bot))
  print("PlayerCommandsCog loaded.")
