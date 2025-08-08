if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

from logging import getLogger
from typing import Optional

from bot_base import SwallowBot
from disnake import Member, User
from disnake.ext.commands import Cog, Context, command

logger = getLogger(__name__)


class ExampleCog(Cog):
  def __init__(self, bot):
    self.bot = bot
    self._last_member = None

  @Cog.listener()
  async def on_member_join(self, member: Member):
    channel = member.guild.system_channel
    if channel is not None:
      await channel.send(f"Welcome {member.mention}.")

  @command()
  async def hello(self, ctx: Context, *, member: Optional[Member | User] = None):
    """Says hello"""
    member = member or ctx.author
    if self._last_member is None or self._last_member.id != member.id:
      await ctx.send(f"Hello {member.name}~")
    else:
      await ctx.send(f"Hello {member.name}... This feels familiar.")
    self._last_member = member


def setup(bot: SwallowBot):
  bot.add_cog(ExampleCog(bot))
  print("ExampleCog loaded.")
