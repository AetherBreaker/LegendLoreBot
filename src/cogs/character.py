if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

from logging import getLogger
from typing import TYPE_CHECKING

from autocomplete.command_autocompleters import autocomp_charname
from disnake import ApplicationCommandInteraction, Embed
from disnake.ext.commands import Cog, Param, slash_command
from pydantic import ValidationError

if TYPE_CHECKING:
  from bot_base import SwallowBot


logger = getLogger(__name__)


class CharacterTracking(Cog):
  def __init__(self, bot: "SwallowBot"):
    self.bot = bot
    self._last_member = None

  @slash_command()
  async def characters(self, _: ApplicationCommandInteraction): ...

  # View character data

  @characters.sub_command()
  async def status(
    self,
    inter: ApplicationCommandInteraction,
    character_name: str = Param(autocomplete=autocomp_charname),
  ):
    character = (
      await self.bot.database.characters.read_typed_row((inter.user.id, character_name))
      if inter.guild_id is None
      else await self.bot.database.characters.read_typed_row((inter.user.id, inter.guild_id, character_name))
    )
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

    if character.images:
      embeds[0].set_image(url=character.images.root[0])
      embeds.extend(Embed().set_image(url=str(url)) for url in character.images.root[1:])

    await inter.send(embeds=embeds)

  # Art and images

  @characters.sub_command()
  async def add_art(
    self,
    inter: ApplicationCommandInteraction,
    character_name: str,
    image_url: str,
  ):
    character = (
      await self.bot.database.characters.read_typed_row((inter.user.id, character_name))
      if inter.guild_id is None
      else await self.bot.database.characters.read_typed_row((inter.user.id, inter.guild_id, character_name))
    )

    if character is None:
      await inter.send("Character not found.")
      return

    character.images.root.append(image_url)  # type: ignore
    await self.bot.database.characters.update_row(character.character_uid, character)
    await inter.send(f"Character art added.\n{image_url}")

  @characters.sub_command()
  async def remove_art(
    self,
    inter: ApplicationCommandInteraction,
    character_name: str,
    art_position: int = Param(description="Position of the art to remove, starting from 1."),
  ):
    character = (
      await self.bot.database.characters.read_typed_row((inter.user.id, character_name))
      if inter.guild_id is None
      else await self.bot.database.characters.read_typed_row((inter.user.id, inter.guild_id, character_name))
    )

    if character is None:
      await inter.send("Character not found.")
      return

    try:
      removed_art = character.images.root.pop(art_position - 1)
    except IndexError:
      await inter.send("Art not found.")
      return

    await self.bot.database.characters.update_row(character.character_uid, character)
    await inter.send(f"Removed art from character.\n{removed_art}")

  @characters.sub_command()
  async def set_token(
    self,
    inter: ApplicationCommandInteraction,
    character_name: str,
    token_url: str,
  ):
    character = (
      await self.bot.database.characters.read_typed_row((inter.user.id, character_name))
      if inter.guild_id is None
      else await self.bot.database.characters.read_typed_row((inter.user.id, inter.guild_id, character_name))
    )

    if character is None:
      await inter.send("Character not found.")
      return

    try:
      character.token_url = token_url  # type: ignore
      await self.bot.database.characters.update_row(character.character_uid, character)
      await inter.send(f"Token URL set for character {character.character_name}: {token_url}.")

    except ValidationError as e:
      await inter.send("Invalid URL format.")
      return

  # Add the autocomplete function without having to make character_name the last param
  add_art.autocomplete("character_name")(autocomp_charname)
  remove_art.autocomplete("character_name")(autocomp_charname)
  set_token.autocomplete("character_name")(autocomp_charname)


def setup(bot: "SwallowBot"):
  bot.add_cog(CharacterTracking(bot))
  print("CharacterTracking loaded.")
