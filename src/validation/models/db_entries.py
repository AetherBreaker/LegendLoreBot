if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

from functools import partial
from logging import getLogger
from typing import Annotated, Any, Literal
from uuid import uuid1

from environment_init_vars import SETTINGS
from number_types.character_money import CopperPieces, GoldPieces, PlatinumPieces, SilverPieces
from number_types.downtime import DowntimeStockpile
from number_types.server_money import GenericMoney
from pydantic import UUID1, Field, HttpUrl, PlainSerializer, ValidationInfo, field_validator
from typing_custom import GuildID, UserID

from validation import CustomBaseModel, CustomRootModel

logger = getLogger(__name__)


level_milestone_rates = {
  (0, 0): 2,
  (2, 4): 3,
  (4, 8): 4,
  (6, 12): 5,
  (10, 20): 6,
  (12, 24): 7,
  (15, 30): 8,
  (18, 36): 9,
  (22, 44): 10,
  (26, 52): 11,
  (30, 60): 12,
  (34, 68): 13,
  (40, 80): 14,
  (48, 96): 15,
  (58, 116): 16,
  (62, 124): 17,
  (68, 136): 18,
  (76, 152): 19,
  (88, 176): 20,
}


class CharacterClassesModel(CustomRootModel):
  root: dict[str, int] = Field(default_factory=dict)


class CharacterImgURLs(CustomRootModel):
  root: list[HttpUrl] = Field(default_factory=list)


class CharacterDBEntryModel(CustomBaseModel):
  character_uid: Annotated[UUID1, Field(default_factory=partial(uuid1, SETTINGS.uid_generator_seed))]
  user_id: Annotated[UserID, PlainSerializer(str, when_used="json")]
  guild_id: Annotated[GuildID, PlainSerializer(str, when_used="json")]
  character_name: str
  sheet_link: HttpUrl
  classes: CharacterClassesModel = Field(default_factory=CharacterClassesModel)
  milestones: int = 0
  level_rate: Literal["medium", "slow"] = "medium"
  mythic_trials: int = 0
  money_pp: PlatinumPieces = PlatinumPieces(0)
  money_gp: GoldPieces = GoldPieces(0)
  money_sp: SilverPieces = SilverPieces(0)
  money_cp: CopperPieces = CopperPieces(0)
  downtime_stockpiled: DowntimeStockpile = DowntimeStockpile(0)
  images: CharacterImgURLs = Field(default_factory=CharacterImgURLs)
  token_url: Optional[HttpUrl] = None

  @property
  def level(self):
    rate_idx = 0 if self.level_rate == "medium" else 1

    result = 2
    for rate, level in level_milestone_rates.items():
      if self.milestones >= rate[rate_idx]:
        result = level

    return result

  @field_validator("classes", mode="before")
  @classmethod
  def default_if_none(cls, val: Any, info: ValidationInfo) -> Any:
    return cls.model_fields[info.field_name].get_default(call_default_factory=True) if val is None else val  # type: ignore


class GuildClassList(CustomRootModel):
  root: list[str] = Field(default_factory=list)


class GuildDBEntryModel(CustomBaseModel):
  guild_id: GuildID
  guild_name: str
  class_list: GuildClassList = Field(default_factory=GuildClassList)

  @field_validator("class_list", mode="before")
  @classmethod
  def default_if_none(cls, val: Any, info: ValidationInfo) -> Any:
    return cls.model_fields[info.field_name].get_default(call_default_factory=True) if val is None else val  # type: ignore


class UserDBEntryModel(CustomBaseModel):
  user_id: UserID
  guild_id: GuildID
  user_name: str
  server_money: GenericMoney = GenericMoney(0)
