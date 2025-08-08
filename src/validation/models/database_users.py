if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

from logging import getLogger

from number_types.server_money import GenericMoney

from validation import CustomBaseModel
from validation.models import GuildID, UserID

logger = getLogger(__name__)


class UserDBEntryModel(CustomBaseModel):
  user_id: UserID
  guild_id: GuildID
  user_name: str
  server_money: GenericMoney = GenericMoney(0)
