if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

from logging import getLogger
from typing import TYPE_CHECKING, Literal

from database.db_utils import ensure_user_exists
from disnake import GuildCommandInteraction, User
from disnake.ext.commands import Cog, Param, slash_command
from pydantic import ValidationError
from validation.models.db_entries import CharacterDBEntryModel

logger = getLogger(__name__)


if TYPE_CHECKING:
  from bot_base import LegendLoreBot


class GMCommandsCog(Cog):
  def __init__(self, bot: "LegendLoreBot"):
    self.bot = bot

  @slash_command()
  async def gm(self, _: GuildCommandInteraction): ...

  @gm.sub_command_group()
  async def characters(self, _: GuildCommandInteraction): ...

  @characters.sub_command()
  async def add(
    self,
    inter: GuildCommandInteraction,
    player: User,
    character_name: str,
    sheetlink: str,
    level_rate: Literal["medium", "slow"] = Param(choices=["medium", "slow"], default="medium"),
  ):
    # first we must check if the user exists in the database before we can add their character
    await ensure_user_exists(player, inter.guild)

    try:
      new_entry = CharacterDBEntryModel(
        user_id=player.id,
        guild_id=inter.guild_id,
        character_name=character_name,
        sheet_link=sheetlink,  # type: ignore
        level_rate=level_rate,
      )

    except ValidationError as e:
      # TODO make errors explain why it failed
      logger.error(f"Failed to add character: {e}")
      await inter.send(f"Failed to add character.\n {e}")
      raise e

    if await self.bot.database.characters.check_exists(new_entry.character_uid):
      await inter.send(f"Character with UID {new_entry.character_uid} already exists.")
      raise ValueError("Character already exists")

    await self.bot.database.characters.append_row(new_entry)

    await inter.send(
      f"Successfully added character: {new_entry.character_name}\n"
      f"Sheet Link: {new_entry.sheet_link}\n"
      f"Character UID: {new_entry.character_uid}\n"
      f"User ID: {new_entry.user_id}\n"
      f"Guild ID: {new_entry.guild_id}\n"
    )

  @gm.sub_command_group()
  async def coins(self, _: GuildCommandInteraction): ...

  ...

  @gm.sub_command_group()
  async def servercoins(self, _: GuildCommandInteraction): ...

  ...


def setup(bot: "LegendLoreBot"):
  bot.add_cog(GMCommandsCog(bot))
  print("GMCommandsCog loaded.")
