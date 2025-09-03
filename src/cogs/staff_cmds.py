if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

from logging import getLogger
from typing import TYPE_CHECKING, Literal, Optional

from database.cache import DatabaseGuildsColumns
from disnake import GuildCommandInteraction
from disnake.abc import GuildChannel
from disnake.ext.commands import Cog, Param, contexts, default_member_permissions, install_types, slash_command
from validation.models.db_entries import GuildChannelEphemSettings

from cogs.cog_utils import run_ephemerally

if TYPE_CHECKING:
  from bot_base import LegendLoreBot


logger = getLogger(__name__)


class StaffCommandsCog(Cog):
  def __init__(self, bot: "LegendLoreBot"):
    self.bot = bot

  @slash_command()
  @default_member_permissions(manage_channels=True)
  @contexts(guild=True)
  @install_types(guild=True)
  async def staff(self, inter: GuildCommandInteraction): ...

  @staff.sub_command_group()
  async def silence_cmds(self, inter: GuildCommandInteraction): ...

  @silence_cmds.sub_command()
  async def server_default(
    self,
    inter: GuildCommandInteraction,
    option: Optional[Literal["ephemeral", "normal"]] = Param(choices=["ephemeral", "normal"], default=None),
  ):
    """
    Sets whether the bot will default all channels to have ephemeral messages or normal messages

    Parameters
    ----------
    option: Sets the default message type for all channels.
    """
    run_ephemeral = await run_ephemerally(self.bot, inter)

    ta, guild_setting = await self.bot.database.guilds.read_value(inter.guild_id, DatabaseGuildsColumns.channel_ephem_default, validate=True)

    match option:
      case "ephemeral":
        setting = True
      case "normal":
        setting = False
      case None:
        setting = not guild_setting

    await self.bot.database.guilds.write_value(inter.guild_id, DatabaseGuildsColumns.channel_ephem_default, setting, ta=ta)

    await inter.send(f"Silent execution mode default has been set to {'ephemeral' if setting else 'normal'}.", ephemeral=run_ephemeral)

  @silence_cmds.sub_command()
  async def toggle(
    self,
    inter: GuildCommandInteraction,
    channel: Optional[GuildChannel] = None,  # type: ignore
    option: Optional[Literal["ephemeral", "normal", "unset"]] = Param(choices=["ephemeral", "normal", "unset"], default=None),
  ):
    run_ephemeral = await run_ephemerally(self.bot, inter)

    channel: GuildChannel = inter.channel if channel is None else channel  # type: ignore

    ta, guild_ephem_channel_settings = await self.bot.database.guilds.read_value(
      inter.guild_id, DatabaseGuildsColumns.channel_ephem_settings, validate=True
    )
    guild_ephem_channel_settings: GuildChannelEphemSettings

    # if setting is None, we flip whatever value already exists.
    # If no value exists for this channel, we set it to the opposite of the guild default
    match option:
      case "ephemeral":
        setting = True
      case "normal":
        setting = False
      case "unset":
        setting = None
      case _:
        setting = not (
          guild_ephem_channel_settings.root[channel.id]
          if channel.id in guild_ephem_channel_settings.root
          else await self.bot.database.guilds.read_value(inter.guild_id, DatabaseGuildsColumns.channel_ephem_default)
        )

    if setting is None:
      if channel.id in guild_ephem_channel_settings.root:
        guild_ephem_channel_settings.root.pop(channel.id)
      await inter.send(f"Channel {channel.jump_url} has been unset.", ephemeral=run_ephemeral)
    else:
      guild_ephem_channel_settings.root[channel.id] = setting
      await inter.send(
        f"Channel {channel.jump_url} has been set to {('ephemeral' if setting else 'normal') if option is None else option}.", ephemeral=run_ephemeral
      )

    await self.bot.database.guilds.write_value(
      inter.guild_id,
      DatabaseGuildsColumns.channel_ephem_settings,
      ta.validate_python(guild_ephem_channel_settings),
      ta=ta,
    )


def setup(bot: "LegendLoreBot"):
  bot.add_cog(StaffCommandsCog(bot))
  print("StaffCommandsCog loaded.")
