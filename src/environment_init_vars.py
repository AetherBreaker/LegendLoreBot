# sourcery skip: raise-from-previous-error
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

try:
  GOOGLE_API_KEY_FILE = next(CWD.glob("bot-db-key.json"))
except StopIteration:
  raise FileNotFoundError(
    "Google API key file 'bot-db-key.json' not found in the current directory.\n"
    "Please create a service account key in the Google Cloud Console "
    "and save it as 'bot-db-key.json' in the current directory."
  )


OWNER_IDS = {200632489998417929}
TEST_GUILDS = [1401596917355380826]
