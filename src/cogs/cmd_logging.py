if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

from logging import getLogger
from typing import TYPE_CHECKING

from disnake.ext.commands import Cog

if TYPE_CHECKING:
  from bot_base import LegendLoreBot


logger = getLogger(__name__)


class AppCMDLoggingCog(Cog):
  def __init__(self, bot: "LegendLoreBot"):
    self.bot = bot


def setup(bot: "LegendLoreBot"):
  bot.add_cog(AppCMDLoggingCog(bot))
  print("AppCMDLoggingCog loaded.")
