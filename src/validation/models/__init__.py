if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

from logging import getLogger
from typing import NewType

GuildID = NewType("GuildID", str)
UserID = NewType("UserID", str)
