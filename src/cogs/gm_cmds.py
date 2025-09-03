if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

from logging import getLogger
from typing import TYPE_CHECKING, Literal

from autocomplete.command_autocompleters import autocomp_other_charname
from database.db_utils import ensure_user_exists
from disnake import GuildCommandInteraction, User
from disnake.ext.commands import Cog, Param, slash_command
from pydantic import ValidationError
from typing_custom.enums import CustomEvent
from validation.models.db_entries import CharacterDBEntryModel

logger = getLogger(__name__)


if TYPE_CHECKING:
  from bot_base import LegendLoreBot


class GMCommandsCog(Cog):
  def __init__(self, bot: "LegendLoreBot"):
    self.bot = bot

  @slash_command()
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

  # Milestones #####################################################################

  @gm.sub_command_group()
  async def milestones(self, _: GuildCommandInteraction): ...

  @milestones.sub_command(name="add")
  async def milestones_add(
    self,
    inter: GuildCommandInteraction,
    player: User,
    character_name: str,
    milestone_amount: int = Param(gt=0),
  ):
    # TODO add checks to prevent adding more milestones than should be possible
    if inter.user.id == player.id:
      await inter.send("You can't change your own character's data. Get someone else to do it!")
      self.bot.dispatch(CustomEvent.on_attempted_change_own_data, inter.user, player, "milestones_amount", milestone_amount)
      return

    character = await self.bot.database.characters.read_typed_row((player.id, character_name))

    if character is None:
      await inter.send("Character not found.")
      return

    character.milestones += milestone_amount
    await self.bot.database.characters.update_row(character.character_uid, character)

    await inter.send(f"Added {milestone_amount} milestones to character {character.character_name}. Total milestones: {character.milestones}")

    self.bot.dispatch(CustomEvent.on_character_milestones_changed, inter.user, player, character_name, milestone_amount)

  @milestones.sub_command(name="remove")
  async def milestones_remove(
    self,
    inter: GuildCommandInteraction,
    player: User,
    character_name: str,
    milestone_amount: int = Param(gt=0),
  ):
    # TODO add checks to prevent removing more milestones than the character has

    if inter.user.id == player.id:
      await inter.send("You can't change your own character's data. Get someone else to do it!")
      self.bot.dispatch(CustomEvent.on_attempted_change_own_data, inter.user, player, "milestones_amount", -milestone_amount)
      return

    character = await self.bot.database.characters.read_typed_row((player.id, character_name))

    if character is None:
      await inter.send("Character not found.")
      return

    character.milestones -= milestone_amount
    await self.bot.database.characters.update_row(character.character_uid, character)

    await inter.send(f"Removed {milestone_amount} milestones from character {character.character_name}. Total milestones: {character.milestones}")

    self.bot.dispatch(CustomEvent.on_character_milestones_changed, inter.user, player, character_name, -milestone_amount)

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
    if inter.user.id == player.id:
      await inter.send("You can't change your own character's data. Get someone else to do it!")
      self.bot.dispatch(CustomEvent.on_attempted_change_own_data, inter.user, player, "mythic_trials", trials_amount)
      return

    character = await self.bot.database.characters.read_typed_row((player.id, character_name))

    if character is None:
      await inter.send("Character not found.")
      return

    character.mythic_trials += trials_amount
    await self.bot.database.characters.update_row(character.character_uid, character)

    await inter.send(f"Added {trials_amount} mythic trials to character {character.character_name}. Total mythic trials: {character.mythic_trials}")

    self.bot.dispatch(CustomEvent.on_character_trials_changed, inter.user, player, character_name, trials_amount)

  @mythic_trials.sub_command(name="remove")
  async def trials_remove(
    self,
    inter: GuildCommandInteraction,
    player: User,
    character_name: str,
    trials_amount: int = Param(gt=0),
  ):
    # TODO add checks to prevent removing more trials than the character has

    if inter.user.id == player.id:
      await inter.send("You can't change your own character's data. Get someone else to do it!")
      self.bot.dispatch(CustomEvent.on_attempted_change_own_data, inter.user, player, "mythic_trials", -trials_amount)
      return

    character = await self.bot.database.characters.read_typed_row((player.id, character_name))

    if character is None:
      await inter.send("Character not found.")
      return

    character.mythic_trials -= trials_amount
    await self.bot.database.characters.update_row(character.character_uid, character)

    await inter.send(
      f"Removed {trials_amount} mythic trials from character {character.character_name}. Total mythic trials: {character.mythic_trials}"
    )

    self.bot.dispatch(CustomEvent.on_character_trials_changed, inter.user, player, character_name, -trials_amount)

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
    if inter.user.id == player.id:
      await inter.send("You can't change your own character's data. Get someone else to do it!")
      self.bot.dispatch(CustomEvent.on_attempted_change_own_data, inter.user, player, "epic_deeds", deeds_amount)
      return

    character = await self.bot.database.characters.read_typed_row((player.id, character_name))

    if character is None:
      await inter.send("Character not found.")
      return

    character.epic_deeds += deeds_amount
    await self.bot.database.characters.update_row(character.character_uid, character)

    await inter.send(f"Added {deeds_amount} epic deeds to character {character.character_name}. Total epic deeds: {character.epic_deeds}")

    self.bot.dispatch(CustomEvent.on_character_deeds_changed, inter.user, player, character_name, deeds_amount)

  @epic.sub_command(name="remove")
  async def epic_remove(
    self,
    inter: GuildCommandInteraction,
    player: User,
    character_name: str,
    deeds_amount: int = Param(gt=0),
  ):
    # TODO add checks to prevent removing more deeds than the character has
    if inter.user.id == player.id:
      await inter.send("You can't change your own character's data. Get someone else to do it!")
      self.bot.dispatch(CustomEvent.on_attempted_change_own_data, inter.user, player, "epic_deeds", -deeds_amount)
      return

    character = await self.bot.database.characters.read_typed_row((player.id, character_name))

    if character is None:
      await inter.send("Character not found.")
      return

    character.epic_deeds -= deeds_amount
    await self.bot.database.characters.update_row(character.character_uid, character)

    await inter.send(f"Removed {deeds_amount} epic deeds from character {character.character_name}. Total epic deeds: {character.epic_deeds}")

    self.bot.dispatch(CustomEvent.on_character_deeds_changed, inter.user, player, character_name, -deeds_amount)

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
