if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

from logging import getLogger
from typing import TYPE_CHECKING, Literal

from autocomplete.command_autocompleters import autocomp_other_charname
from database.db_utils import ensure_user_exists
from disnake import GuildCommandInteraction, User
from disnake.ext.commands import Cog, Param, Range, contexts, default_member_permissions, install_types, slash_command
from pydantic import ValidationError
from typing_custom.dataframe_column_names import DatabaseCharactersColumns
from typing_custom.enums import CustomEvent
from validation.models.db_entries import CharacterDBEntryModel

from cogs.cog_utils import run_ephemerally

logger = getLogger(__name__)


if TYPE_CHECKING:
  from bot_base import LegendLoreBot


class GMCommandsCog(Cog):
  def __init__(self, bot: "LegendLoreBot"):
    self.bot = bot

  @slash_command()
  @default_member_permissions(administrator=True)
  @contexts(guild=True)
  @install_types(guild=True)
  async def gm(self, _: GuildCommandInteraction): ...

  # Characters #####################################################################

  @gm.sub_command_group()
  async def characters(self, _: GuildCommandInteraction): ...

  @characters.sub_command(name="add")
  async def char_add(
    self,
    inter: GuildCommandInteraction,
    player: User,
    character_name: str,
    sheetlink: str,
    level_rate: Literal["medium", "slow"] = Param(choices=["medium", "slow"], default="medium"),
  ):
    run_ephemeral = await run_ephemerally(self.bot, inter)
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
      await inter.send(f"Failed to add character.\n {e}", ephemeral=run_ephemeral)
      raise e

    if await self.bot.database.characters.check_uid_exists(new_entry.character_uid):
      await inter.send(f"Character with UID {new_entry.character_uid} already exists.", ephemeral=run_ephemeral)
      raise ValueError("Character already exists")

    if await self.bot.database.characters.check_name_exists(player.id, character_name):
      await inter.send(f"Character with name {character_name} for {player.mention} already exists.", ephemeral=run_ephemeral)
      raise ValueError("Character already exists")

    await self.bot.database.characters.append_row(new_entry)

    await inter.send(
      f"Successfully added character: {new_entry.character_name}\n"
      f"Sheet Link: {new_entry.sheet_link}\n"
      f"Character UID: {new_entry.character_uid}\n"
      f"User ID: {new_entry.user_id}\n"
      f"Guild ID: {new_entry.guild_id}\n",
      ephemeral=run_ephemeral,
    )

  # Milestones #####################################################################

  @gm.sub_command_group()
  async def milestones(self, _: GuildCommandInteraction): ...

  @milestones.sub_command(name="add")
  async def milestones_add(
    self,
    inter: GuildCommandInteraction,
    player: User,
    character_name: str,
    milestone_amount: Range[int, 1, 176],
  ):
    await self.do_attribute_math(
      self.bot,
      inter,
      player,
      character_name,
      "Milestones",
      DatabaseCharactersColumns.milestones,
      milestone_amount,
    )

  @milestones.sub_command(name="remove")
  async def milestones_remove(
    self,
    inter: GuildCommandInteraction,
    player: User,
    character_name: str,
    milestone_amount: Range[int, 1, 176],
  ):
    await self.do_attribute_math(
      self.bot,
      inter,
      player,
      character_name,
      "Milestones",
      DatabaseCharactersColumns.milestones,
      -milestone_amount,
    )

  # Mythic Trials ###################################################################

  @gm.sub_command_group()
  async def mythic_trials(self, _: GuildCommandInteraction): ...

  @mythic_trials.sub_command(name="add")
  async def trials_add(
    self,
    inter: GuildCommandInteraction,
    player: User,
    character_name: str,
    trials_amount: int = Param(gt=0),
  ):
    await self.do_attribute_math(
      self.bot,
      inter,
      player,
      character_name,
      "Mythic Trials",
      DatabaseCharactersColumns.mythic_trials,
      trials_amount,
    )

  @mythic_trials.sub_command(name="remove")
  async def trials_remove(
    self,
    inter: GuildCommandInteraction,
    player: User,
    character_name: str,
    trials_amount: int = Param(gt=0),
  ):
    await self.do_attribute_math(
      self.bot,
      inter,
      player,
      character_name,
      "Mythic Trials",
      DatabaseCharactersColumns.mythic_trials,
      -trials_amount,
    )

  # Epic Deeds #####################################################################

  @gm.sub_command_group()
  async def epic(self, _: GuildCommandInteraction): ...

  @epic.sub_command(name="add")
  async def epic_add(
    self,
    inter: GuildCommandInteraction,
    player: User,
    character_name: str,
    deeds_amount: int = Param(gt=0),
  ):
    await self.do_attribute_math(
      self.bot,
      inter,
      player,
      character_name,
      "Epic Deeds",
      DatabaseCharactersColumns.epic_deeds,
      deeds_amount,
    )

  @epic.sub_command(name="remove")
  async def epic_remove(
    self,
    inter: GuildCommandInteraction,
    player: User,
    character_name: str,
    deeds_amount: int = Param(gt=0),
  ):
    await self.do_attribute_math(
      self.bot,
      inter,
      player,
      character_name,
      "Epic Deeds",
      DatabaseCharactersColumns.epic_deeds,
      -deeds_amount,
    )

  # Shared #########################################################################

  async def do_attribute_math(
    self,
    bot: "LegendLoreBot",
    inter: GuildCommandInteraction,
    player: User,
    character_name: str,
    attr_type: Literal["Milestones", "Mythic Trials", "Epic Deeds"],
    attribute: DatabaseCharactersColumns,
    amount: int,
  ):
    run_ephemeral = await run_ephemerally(bot, inter)

    try:
      existing_val = await self.bot.database.characters.read_value((player.id, character_name), attribute)
    except KeyError:
      await inter.send(f'Character "{character_name}" not found.', ephemeral=run_ephemeral)
      return

    existing_val += amount

    if existing_val < 0:
      await inter.send(
        f"Cannot remove {abs(amount)} {attr_type} from character {character_name} as it would result in a negative value.", ephemeral=run_ephemeral
      )
      return

    await self.bot.database.characters.write_value((player.id, character_name), attribute, existing_val)

    await inter.send(
      f"{'Removed' if amount < 0 else 'Added'} {abs(amount)} {attr_type} {'from' if amount < 0 else 'to'} character {character_name}. New total {attr_type}: {existing_val}"
    )

    self.bot.dispatch(CustomEvent.on_character_attr_changed, locals())

  # Currency #######################################################################

  @gm.sub_command_group()
  async def coins(self, _: GuildCommandInteraction): ...

  ...

  # BC #############################################################################

  @gm.sub_command_group()
  async def servercoins(self, _: GuildCommandInteraction): ...

  ...

  # Autocompleters #################################################################
  milestones_add.autocomplete("character_name")(autocomp_other_charname)
  milestones_remove.autocomplete("character_name")(autocomp_other_charname)
  trials_add.autocomplete("character_name")(autocomp_other_charname)
  trials_remove.autocomplete("character_name")(autocomp_other_charname)
  epic_add.autocomplete("character_name")(autocomp_other_charname)
  epic_remove.autocomplete("character_name")(autocomp_other_charname)


def setup(bot: "LegendLoreBot"):
  bot.add_cog(GMCommandsCog(bot))
  print("GMCommandsCog loaded.")
