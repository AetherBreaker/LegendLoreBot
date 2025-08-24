if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

from functools import partial
from logging import getLogger
from typing import TYPE_CHECKING, Literal, Optional

from database.cache import DatabaseGuildsColumns
from disnake import GuildCommandInteraction, SlashCommand
from disnake.abc import GuildChannel
from disnake.ext.commands import Cog, Param, slash_command
from validation.models.db_entries import GuildChannelEphemSettings

if TYPE_CHECKING:
  from bot_base import LegendLoreBot


logger = getLogger(__name__)


class StaffCommandsCog(Cog):
  def __init__(self, bot: "LegendLoreBot"):
    self.bot = bot

  @slash_command()
  async def staff(self, inter: GuildCommandInteraction): ...

  async def silence_commands_default(
    self,
    inter: GuildCommandInteraction,
    option: Literal["whitelist", "blacklist"] = Param(choices=["ephemeral", "normal"], default="ephemeral"),
  ):
    """
    Sets whether the bot will default all channels to have ephemeral messages (ephemeral) or default all channels to have normal messages (normal).

    option: Sets the default message type for all channels.
    """

  @staff.sub_command()
  async def channel_silence_cmds(
    self,
    inter: GuildCommandInteraction,
    channel: Optional[GuildChannel] = None,
    option: Optional[Literal["ephemeral", "normal", "unset"]] = Param(choices=["ephemeral", "normal", "unset"], default=None),
  ):
    channel_id = inter.channel.id if channel is None else channel.id

    ta, guild_ephem_channel_settings = await self.bot.database.guilds.read_value(
      inter.guild_id, DatabaseGuildsColumns.channel_ephem_settings, validate=True
    )
    guild_ephem_channel_settings: GuildChannelEphemSettings

    # if setting is None, we flip whatever value already exists.
    # If no value exists for this channel, we set it to the opposite of the guild default
    if option is not None and option != "unset":
      setting = option == "ephemeral"

    elif option is None:
      setting_to_flip = (
        guild_ephem_channel_settings.root[channel_id]
        if channel_id in guild_ephem_channel_settings.root
        else await self.bot.database.guilds.read_value(inter.guild_id, DatabaseGuildsColumns.channel_ephem_default)
      )
      setting = not setting_to_flip

    else:
      setting = option

    if setting == "unset":
      if channel_id in guild_ephem_channel_settings.root:
        guild_ephem_channel_settings.root.pop(channel_id)
    else:
      guild_ephem_channel_settings.root[channel_id] = setting

    await self.bot.database.guilds.write_value(
      inter.guild_id,
      DatabaseGuildsColumns.channel_ephem_settings,
      ta.validate_python(guild_ephem_channel_settings),
      ta=ta,
    )

    await inter.send(f"Channel {channel_id} has been set to {option}.")


def setup(bot: "LegendLoreBot"):
  bot.add_cog(StaffCommandsCog(bot))
  print("StaffCommandsCog loaded.")
