if __name__ == "__main__":
  from src.logging_config import configure_logging

  configure_logging()

from logging import getLogger
from pathlib import Path

from src.environment_settings import Settings

logger = getLogger(__name__)


# Settings
SETTINGS = Settings()  # type: ignore

# Folder paths
CWD = Path.cwd()
