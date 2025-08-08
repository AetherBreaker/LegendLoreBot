if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

from logging import getLogger

from validation import CustomBaseModel
from validation.models import GuildID

logger = getLogger(__name__)


class GuildDBEntryModel(CustomBaseModel):
  guild_id: GuildID
