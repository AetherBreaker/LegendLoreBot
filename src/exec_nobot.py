if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

from asyncio import run
from logging import getLogger

from bot_base import SwallowBot
from database.cache import DatabaseCache
from environment_init_vars import SETTINGS
from validation.models.db_entries import GuildDBEntryModel

logger = getLogger(__name__)


async def main():
  database = DatabaseCache()
  await database.refresh_cache()

  await database.guilds.append_row(
    GuildDBEntryModel(
      guild_id=123,
      guild_name="Test Guild",
      class_list=["test", "test2"],  # type: ignore
    )
  )

  await database.submit_queued_writes_to_pool()


if __name__ == "__main__":
  run(main())
