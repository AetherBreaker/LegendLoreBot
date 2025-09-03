if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

from logging import getLogger
from typing import TYPE_CHECKING

from autocomplete.command_autocompleters import autocomp_all_classnames, autocomp_char_classname, autocomp_self_charname
from disnake import ApplicationCommandInteraction, Embed
from disnake.ext.commands import Cog, Param, Range, slash_command
from pydantic import ValidationError

from cogs.cog_utils import run_ephemerally

if TYPE_CHECKING:
  from bot_base import LegendLoreBot


logger = getLogger(__name__)


class CharacterTrackingCog(Cog):
  def __init__(self, bot: "LegendLoreBot"):
    self.bot = bot

  @slash_command()
  async def characters(self, _: ApplicationCommandInteraction): ...

  # View character data

  @characters.sub_command()
  async def status(
    self,
    inter: ApplicationCommandInteraction,
    character_name: str = Param(autocomplete=autocomp_self_charname),
  ):
    run_ephemeral = await run_ephemerally(self.bot, inter)

    try:
      character = (
        await self.bot.database.characters.read_typed_row((inter.user.id, character_name))
        if inter.guild_id is None
        else await self.bot.database.characters.read_typed_row((inter.user.id, inter.guild_id, character_name))
      )

    except KeyError:
      await inter.send(f"Character {character_name} not found.", ephemeral=run_ephemeral)
      return

    guild = self.bot.get_guild(character.guild_id) if inter.guild_id is None else inter.guild
    if guild is None:
      guild = await self.bot.fetch_guild(character.guild_id)

    embeds = [
      Embed(
        title=character.character_name,
        url=str(character.sheet_link),
      ).set_author(name=guild.name, icon_url=guild.icon.url if guild.icon is not None else None)
    ]

    # Add fields
    embeds[0].add_field(
      name=f"Character Level: {character.level}",
      value="Character Classes:\n" + "\n".join((f"{classname}: {level}" for classname, level in character.classes.root.items())),
      inline=True,
    )
    embeds[0].add_field(name=f"Milestones: {character.milestones}", value="", inline=True)
    embeds[0].add_field(name=f"Mythic Tier: {character.tier}", value=f"Mythic Trials: {character.mythic_trials}", inline=True)
    embeds[0].add_field(
      name="Money:",
      value=(
        f"Platinum: {character.money_pp}\n"
        f"    Gold: {character.money_gp}\n"
        f"  Silver: {character.money_sp}\n"
        f"  Copper: {character.money_cp}"  # keep expanded
      ),
      inline=True,
    )

    if character.token_url is not None:
      embeds[0].set_thumbnail(url=str(character.token_url))

    if character.images.root:
      embeds[0].set_image(url=character.images.root[0])
      embeds.extend(Embed().set_image(url=str(url)) for url in character.images.root[1:])

    await inter.send(embeds=embeds, ephemeral=run_ephemeral)

  # Art and images

  @characters.sub_command()
  async def add_art(
    self,
    inter: ApplicationCommandInteraction,
    character_name: str,
    image_url: str,
  ):
    run_ephemeral = await run_ephemerally(self.bot, inter)

    try:
      character = (
        await self.bot.database.characters.read_typed_row((inter.user.id, character_name))
        if inter.guild_id is None
        else await self.bot.database.characters.read_typed_row((inter.user.id, inter.guild_id, character_name))
      )

    except KeyError:
      await inter.send(f"Character {character_name} not found.", ephemeral=run_ephemeral)
      return

    if character is None:
      await inter.send("Character not found.", ephemeral=run_ephemeral)
      return

    char_images = character.images

    char_images.root.append(image_url)  # type: ignore

    # Assign back to the model to ensure the updated data receives validation
    character.images = char_images

    await self.bot.database.characters.update_row(character.character_uid, character)
    await inter.send(f"Character art added.\n{image_url}", ephemeral=run_ephemeral)

  @characters.sub_command()
  async def remove_art(
    self,
    inter: ApplicationCommandInteraction,
    character_name: str,
    art_position: int = Param(description="Position of the art to remove, starting from 1."),
  ):
    run_ephemeral = await run_ephemerally(self.bot, inter)

    try:
      character = (
        await self.bot.database.characters.read_typed_row((inter.user.id, character_name))
        if inter.guild_id is None
        else await self.bot.database.characters.read_typed_row((inter.user.id, inter.guild_id, character_name))
      )

    except KeyError:
      await inter.send(f"Character {character_name} not found.", ephemeral=run_ephemeral)
      return

    if character is None:
      await inter.send("Character not found.", ephemeral=run_ephemeral)
      return

    char_images = character.images

    try:
      removed_art = char_images.root.pop(art_position - 1)
    except IndexError:
      await inter.send("Art not found.", ephemeral=run_ephemeral)
      return

    character.images = char_images  # Reassign to ensure validation

    await self.bot.database.characters.update_row(character.character_uid, character)
    await inter.send(f"Removed art from character.\n{removed_art}", ephemeral=run_ephemeral)

  @characters.sub_command()
  async def set_token(
    self,
    inter: ApplicationCommandInteraction,
    character_name: str,
    token_url: str,
  ):
    run_ephemeral = await run_ephemerally(self.bot, inter)

    try:
      character = (
        await self.bot.database.characters.read_typed_row((inter.user.id, character_name))
        if inter.guild_id is None
        else await self.bot.database.characters.read_typed_row((inter.user.id, inter.guild_id, character_name))
      )
    except KeyError:
      await inter.send(f"Character {character_name} not found.", ephemeral=run_ephemeral)
      return

    if character is None:
      await inter.send(f"Character {character_name} not found.", ephemeral=run_ephemeral)
      return

    try:
      character.token_url = token_url  # type: ignore
      await self.bot.database.characters.update_row(character.character_uid, character)
      await inter.send(f"Token URL set for character {character.character_name}: {token_url}.", ephemeral=run_ephemeral)

    except ValidationError:
      await inter.send("Invalid URL format.", ephemeral=run_ephemeral)
      return

  # Character classes

  @characters.sub_command()
  async def add_class(
    self,
    inter: ApplicationCommandInteraction,
    character_name: str,
    class_name: str,
    class_level: Range[int, 1, 20],
  ):
    run_ephemeral = await run_ephemerally(self.bot, inter)

    try:
      character = (
        await self.bot.database.characters.read_typed_row((inter.user.id, character_name))
        if inter.guild_id is None
        else await self.bot.database.characters.read_typed_row((inter.user.id, inter.guild_id, character_name))
      )
    except KeyError:
      await inter.send(f"Character {character_name} not found.", ephemeral=run_ephemeral)
      return

    if character is None:
      await inter.send(f"Character {character_name} not found.", ephemeral=run_ephemeral)
      return

    char_classes = character.classes

    char_classes.root[class_name] = class_level

    character.classes = char_classes  # Reassign to ensure validation

    if character is None:
      await inter.send(f"Character {character_name} not found.", ephemeral=run_ephemeral)
      return

    char_classes = character.classes

    char_classes.root[class_name] = class_level

    character.classes = char_classes  # Reassign to ensure validation
    await self.bot.database.characters.update_row(character.character_uid, character)
    await inter.send(f"Added class {class_name} (Level {class_level}) to character {character_name}.", ephemeral=run_ephemeral)

  @characters.sub_command()
  async def remove_class(
    self,
    inter: ApplicationCommandInteraction,
    character_name: str,
    class_name: str,
  ):
    run_ephemeral = await run_ephemerally(self.bot, inter)

    try:
      character = (
        await self.bot.database.characters.read_typed_row((inter.user.id, character_name))
        if inter.guild_id is None
        else await self.bot.database.characters.read_typed_row((inter.user.id, inter.guild_id, character_name))
      )

    except KeyError:
      await inter.send(f"Character {character_name} not found.", ephemeral=run_ephemeral)
      return

    if character is None:
      await inter.send(f"Character {character_name} not found.", ephemeral=run_ephemeral)
      return

    char_classes = character.classes

    if class_name in char_classes.root:
      del char_classes.root[class_name]

      character.classes = char_classes  # Reassign to ensure validation

      await self.bot.database.characters.update_row(character.character_uid, character)
      await inter.send(f"Removed class {class_name} from character {character_name}.", ephemeral=run_ephemeral)
    else:
      await inter.send(f"Class {class_name} not found for character {character_name}.", ephemeral=run_ephemeral)

  @characters.sub_command()
  async def update_class_level(
    self,
    inter: ApplicationCommandInteraction,
    character_name: str,
    class_name: str,
    class_level: Range[int, 1, 20],
  ):
    run_ephemeral = await run_ephemerally(self.bot, inter)

    try:
      character = (
        await self.bot.database.characters.read_typed_row((inter.user.id, character_name))
        if inter.guild_id is None
        else await self.bot.database.characters.read_typed_row((inter.user.id, inter.guild_id, character_name))
      )
    except KeyError:
      await inter.send(f"Character {character_name} not found.", ephemeral=run_ephemeral)
      return

    if character is None:
      await inter.send(f"Character {character_name} not found.", ephemeral=run_ephemeral)
      return

    char_classes = character.classes

    if class_name in char_classes.root:
      char_classes.root[class_name] = class_level
      character.classes = char_classes  # Reassign to ensure validation
      await self.bot.database.characters.update_row(character.character_uid, character)
      await inter.send(f"Updated class {class_name} to level {class_level} for character {character_name}.", ephemeral=run_ephemeral)
    else:
      await inter.send(f"Class {class_name} not found for character {character_name}.", ephemeral=run_ephemeral)

  # Add the autocomplete function without having to make character_name the last param
  add_art.autocomplete("character_name")(autocomp_self_charname)
  remove_art.autocomplete("character_name")(autocomp_self_charname)
  set_token.autocomplete("character_name")(autocomp_self_charname)
  add_class.autocomplete("character_name")(autocomp_self_charname)
  remove_class.autocomplete("character_name")(autocomp_self_charname)
  update_class_level.autocomplete("character_name")(autocomp_self_charname)

  # add guildwide classname autocompleter
  add_class.autocomplete("class_name")(autocomp_all_classnames)

  # add specific char classname autocompleter
  remove_class.autocomplete("class_name")(autocomp_char_classname)
  update_class_level.autocomplete("class_name")(autocomp_char_classname)


def setup(bot: "LegendLoreBot"):
  bot.add_cog(CharacterTrackingCog(bot))
  print("CharacterTrackingCog loaded.")
