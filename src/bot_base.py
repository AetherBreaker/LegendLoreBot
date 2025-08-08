if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

from logging import getLogger

import cogs
from database.cache import DatabaseCache
from disnake import Intents, Message
from disnake.ext.commands import Bot
from environment_init_vars import OWNER_IDS, TEST_GUILDS

logger = getLogger(__name__)


class SwallowBot(Bot):
  def __init__(self, *args, **kwargs):
    self.database = DatabaseCache()

    self.load_extensions(cogs.__name__)

    intents = Intents.default()
    intents.message_content = True
    super().__init__(
      *args,
      **kwargs,
      intents=intents,
      owner_ids=OWNER_IDS,
      test_guilds=TEST_GUILDS,
      reload=bool(__debug__),
    )

  async def on_ready(self):
    print(f"Logged on as {self.user}!")

  async def on_message(self, message: Message):
    print(f"Message from {message.author}: {message.content}")
    if message.content.lower().startswith("what is the airspeed velocity of an unladen swallow?".strip().lower()):
      await message.channel.send("What do you mean? African or European swallow?")
