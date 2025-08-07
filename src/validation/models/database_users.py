from number_types.server_money import GenericMoney

from validation import CustomBaseModel
from validation.models import GuildID, UserID


class UserDBEntryModel(CustomBaseModel):
  user_id: UserID
  guild_id: GuildID
  user_name: str
  server_money: GenericMoney = GenericMoney(0)
