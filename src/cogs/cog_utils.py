from typing import TYPE_CHECKING

from disnake import ApplicationCommandInteraction
from validation.models.db_entries import GuildDBEntryModel

if TYPE_CHECKING:
  from bot_base import LegendLoreBot


async def run_ephemerally(bot: "LegendLoreBot", inter: ApplicationCommandInteraction) -> bool:
  if inter.guild_id is None:
    return False

  guild_settings: GuildDBEntryModel = await bot.database.guilds.read_typed_row(inter.guild_id)

  return guild_settings.channel_ephem_settings.root.get(inter.channel.id, guild_settings.channel_ephem_default)
