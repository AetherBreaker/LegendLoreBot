if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

from functools import partial
from logging import getLogger
from typing import Annotated
from uuid import uuid1

from environment_init_vars import SETTINGS
from number_types.character_money import CopperPieces, GoldPieces, PlatinumPieces, SilverPieces
from number_types.downtime import DowntimeStockpile
from number_types.server_money import GenericMoney
from pydantic import UUID1, Field, HttpUrl, PlainSerializer
from typing_custom import GuildID, UserID

from validation import CustomBaseModel

logger = getLogger(__name__)


class CharacterDBEntryModel(CustomBaseModel):
  character_uid: Annotated[UUID1, Field(default_factory=partial(uuid1, SETTINGS.uid_generator_seed))]
  user_id: Annotated[UserID, PlainSerializer(str, when_used="json")]
  guild_id: Annotated[GuildID, PlainSerializer(str, when_used="json")]
  character_name: str
  sheet_link: HttpUrl
  milestones: int = 0
  level_rate: Literal["medium", "slow"] = "medium"
  mythic_trials: int = 0
  money_pp: PlatinumPieces = PlatinumPieces(0)
  money_gp: GoldPieces = GoldPieces(0)
  money_sp: SilverPieces = SilverPieces(0)
  money_cp: CopperPieces = CopperPieces(0)
  downtime_stockpiled: DowntimeStockpile = DowntimeStockpile(0)


class GuildDBEntryModel(CustomBaseModel):
  guild_id: GuildID
  guild_name: str


class UserDBEntryModel(CustomBaseModel):
  user_id: UserID
  guild_id: GuildID
  user_name: str
  server_money: GenericMoney = GenericMoney(0)
