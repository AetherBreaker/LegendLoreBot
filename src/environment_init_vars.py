if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

from logging import getLogger
from pathlib import Path

from environment_settings import Settings

logger = getLogger(__name__)


# Settings
SETTINGS = Settings()  # type: ignore

# Folder paths
CWD = Path.cwd()


OWNER_IDS = {200632489998417929}
TEST_GUILDS = [1401596917355380826]
