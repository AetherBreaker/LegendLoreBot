if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

from logging import getLogger

from component_menus.choice_discriminator import DiscriminateChoices
from database.cache import DatabaseCache
from disnake import ApplicationCommandInteraction
from rapidfuzz.process import extract

logger = getLogger(__name__)

type AutocompChoice = str
type AutocompValue = str | DiscriminateChoices


async def autocomp_charname(inter: ApplicationCommandInteraction, user_input: str) -> dict[AutocompChoice, AutocompValue]:
  # Grab the singleton instance of our database accessor
  db = DatabaseCache()

  # enter context manager for db.characters

  # select the character names column, filtered by the current interactions guildid and userid

  # cast the resulting series to a dict of uid -> character name pairs

  # iterate through and flip the dict's keys and values via dict comprehension
  # during comprehension locate any dict entries with identical character names, and replace their uids with an instance
  # of DiscriminateChoices with the two character uids prepassed.

  # rapidfuzz the user_input against the character name keys of the resulting dict

  # return matches

  pass
