from typing import Annotated
from uuid import UUID, uuid1

from environment_init_vars import SETTINGS
from number_types.character_money import CopperPieces, GoldPieces, PlatinumPieces, SilverPieces
from number_types.downtime import DowntimeStockpile
from pydantic.types import UuidVersion

from validation import CustomBaseModel
from validation.models import GuildID, UserID


class CharacterDBEntryModel(CustomBaseModel):
  character_uid: Annotated[UUID, UuidVersion(1)] = uuid1(SETTINGS.uid_generator_seed)
  user_id: UserID
  guild_id: GuildID
  character_name: str
  milestones: int = 0
  mythic_trials: int = 0
  money_pp: PlatinumPieces = PlatinumPieces(0)
  money_gp: GoldPieces = GoldPieces(0)
  money_sp: SilverPieces = SilverPieces(0)
  money_cp: CopperPieces = CopperPieces(0)
  downtime_stockpiled: DowntimeStockpile = DowntimeStockpile(0)
