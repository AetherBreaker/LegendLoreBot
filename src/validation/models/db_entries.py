if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

from functools import partial
from inspect import get_annotations
from itertools import accumulate, takewhile
from logging import getLogger
from math import floor
from typing import Annotated, Any, Literal, Optional
from uuid import uuid1

from environment_init_vars import SETTINGS
from number_types.character_money import CopperPieces, GoldPieces, PlatinumPieces, SilverPieces
from number_types.downtime import DowntimeStockpile
from pydantic import UUID1, Field, HttpUrl, PlainSerializer, TypeAdapter, ValidationInfo, field_validator
from typing_custom import GuildID, UserID

from validation import PYDANTIC_CONFIG, CustomBaseModel, CustomRootModel

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

tier_rate = [floor((i + 1) / 2) for i in range(2, 11)]


class CharacterClassesModel(CustomRootModel[dict[str, int]]):
  root: dict[str, int] = Field(default_factory=dict)


class CharacterImgURLs(CustomRootModel[list[HttpUrl]]):
  root: list[HttpUrl] = Field(default_factory=list)


class CharacterDBEntryModel(CustomBaseModel):
  character_uid: Annotated[UUID1, Field(default_factory=partial(uuid1, SETTINGS.uid_generator_seed))]
  user_id: Annotated[UserID, PlainSerializer(str, when_used="json")]
  guild_id: Annotated[GuildID, PlainSerializer(str, when_used="json")]
  character_name: str
  sheet_link: HttpUrl
  classes: CharacterClassesModel = Field(default_factory=CharacterClassesModel)
  level_rate: Literal["medium", "slow"] = "medium"
  milestones: int = 0
  mythic_trials: int = 0
  epic_deeds: int = 0
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

  @property
  def tier(self) -> int:
    return max(len(list(takewhile(lambda x: x <= self.mythic_trials, accumulate(tier_rate, initial=0)))), self.level // 3)

  @field_validator("classes", mode="before")
  @classmethod
  def default_if_none(cls, val: Any, info: ValidationInfo) -> Any:
    return cls.model_fields[info.field_name].get_default(call_default_factory=True) if val is None else val  # type: ignore


class GuildClassList(CustomRootModel[set[str]]):
  root: set[str] = Field(default_factory=set)


class GuildChannelEphemSettings(CustomRootModel[dict[int, bool]]):
  root: dict[int, bool] = Field(default_factory=dict)


class GuildDBEntryModel(CustomBaseModel):
  guild_id: Annotated[GuildID, PlainSerializer(str, when_used="json")]
  guild_name: str
  class_list: GuildClassList = Field(default_factory=GuildClassList)
  channel_ephem_settings: GuildChannelEphemSettings = Field(default_factory=GuildChannelEphemSettings)
  channel_ephem_default: bool = True  # True = ephemeral | False = normal

  @field_validator("class_list", mode="before")
  @classmethod
  def default_if_none(cls, val: Any, info: ValidationInfo) -> Any:
    return cls.model_fields[info.field_name].get_default(call_default_factory=True) if val is None else val  # type: ignore


class UserDBEntryModel(CustomBaseModel):
  user_id: Annotated[UserID, PlainSerializer(str, when_used="json")]
  guild_id: Annotated[GuildID, PlainSerializer(str, when_used="json")]
  user_name: str
  server_money: int = 0


GUILDS_TYPE_ADAPTERS = {
  field: TypeAdapter(fieldinf, config=None if issubclass(fieldinf, (CustomBaseModel, CustomRootModel)) else PYDANTIC_CONFIG)
  for field, fieldinf in get_annotations(GuildDBEntryModel).items()
}
USERS_TYPE_ADAPTERS = {
  field: TypeAdapter(fieldinf, config=None if issubclass(fieldinf, (CustomBaseModel, CustomRootModel)) else PYDANTIC_CONFIG)
  for field, fieldinf in get_annotations(UserDBEntryModel).items()
}
CHARACTERS_TYPE_ADAPTERS = {
  field: TypeAdapter(fieldinf, config=None if issubclass(fieldinf, (CustomBaseModel, CustomRootModel)) else PYDANTIC_CONFIG)
  for field, fieldinf in get_annotations(CharacterDBEntryModel).items()
}
