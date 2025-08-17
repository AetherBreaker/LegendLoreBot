if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

from logging import getLogger
from typing import TYPE_CHECKING

from disnake.ext.commands import Cog

if TYPE_CHECKING:
  from bot_base import SwallowBot


logger = getLogger(__name__)


class AppCMDLoggingCog(Cog):
  def __init__(self, bot: "SwallowBot"):
    self.bot = bot


def setup(bot: "SwallowBot"):
  bot.add_cog(AppCMDLoggingCog(bot))
  print("AppCMDLoggingCog loaded.")
