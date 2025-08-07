from validation import CustomBaseModel
from validation.models import GuildID


class GuildDBEntryModel(CustomBaseModel):
  guild_id: GuildID
