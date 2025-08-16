if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

from logging import getLogger
from typing import TYPE_CHECKING, Optional

from autocomplete.command_autocompleters import autocomp_charname
from disnake import ApplicationCommandInteraction, Embed, GuildCommandInteraction, Member, User
from disnake.ext.commands import Cog, Param, message_command, slash_command, user_command

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



def setup(bot: "SwallowBot"):
  bot.add_cog(CharacterTracking(bot))
  print("CharacterTracking loaded.")
