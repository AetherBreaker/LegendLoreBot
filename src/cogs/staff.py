if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

from logging import getLogger
from typing import TYPE_CHECKING, Literal

from disnake import ApplicationCommandInteraction, GuildCommandInteraction
from disnake.ext.commands import Cog, Param, slash_command
from pydantic import ValidationError
from validation.models.database import CharacterDBEntryModel

logger = getLogger(__name__)


if TYPE_CHECKING:
  from bot_base import SwallowBot


class StaffCommands(Cog):
  def __init__(self, bot: "SwallowBot"):
    self.bot = bot
    self._last_member = None

  @slash_command()
  async def staff(self, _: GuildCommandInteraction): ...

  @staff.sub_command_group()
  async def characters(self, _: GuildCommandInteraction): ...

  @characters.sub_command()
  async def add(
    self,
    inter: GuildCommandInteraction,
    character_name: str,
    sheetlink: str,
    level_rate: Literal["medium", "slow"] = Param(choices=["medium", "slow"], default="medium"),
  ):
    try:
      new_entry = CharacterDBEntryModel(
        user_id=inter.author.id,
        guild_id=inter.guild_id,
        character_name=character_name,
        sheet_link=sheetlink,  # type: ignore
        level_rate=level_rate,
      )

    except ValidationError as e:
      logger.error(f"Failed to add character: {e}")
      await inter.send(f"Failed to add character.\n {e}")
      return

    await self.bot.database.characters.append_row(new_entry)

    await inter.send(
      f"Successfully added character: {new_entry.character_name}\n"
      f"Sheet Link: {new_entry.sheet_link}\n"
      f"Character UID: {new_entry.character_uid}\n"
      f"User ID: {new_entry.user_id}\n"
      f"Guild ID: {new_entry.guild_id}\n"
    )

  @staff.sub_command_group()
  async def coins(self, _: GuildCommandInteraction): ...

  ...

  @staff.sub_command_group()
  async def servercoins(self, _: GuildCommandInteraction): ...

  ...


def setup(bot: "SwallowBot"):
  bot.add_cog(StaffCommands(bot))
  print("StaffCommands loaded.")
