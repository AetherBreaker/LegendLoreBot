if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

from logging import getLogger

from autocomplete.autocomp_cache import AutocompCache, prepass_cache
from component_menus.choice_discriminator import DiscriminateChoices
from database.cache import DatabaseCache, DatabaseCharactersColumns
from disnake import ApplicationCommandInteraction
from rapidfuzz.process import extract
from typing_custom import CharacterUID

logger = getLogger(__name__)

type CharacterName = str

type AutocompChoice = CharacterName
type AutocompValue = CharacterUID | DiscriminateChoices


@prepass_cache
async def autocomp_charname(
  cache: AutocompCache[dict[CharacterUID, str]], inter: ApplicationCommandInteraction, user_input: str
) -> dict[AutocompChoice, AutocompValue]:
  # Grab the singleton instance of our database accessor
  db = DatabaseCache()
  await db._refresh_cache()

  search_index = (
    (slice(None), inter.user.id, inter.guild_id)
    if inter.guild_id is not None
    else (slice(None), inter.user.id, slice(None))
  )

  cached_query = cache.get(search_index)
  if cached_query is None:
    # enter context manager for db.characters
    async with db.characters as characters:
      # select the character names column, filtered by the current interactions guildid and userid
      selection = characters.loc[search_index, DatabaseCharactersColumns.character_name]

    # drop the unecessary index levels
    almost = selection.droplevel([DatabaseCharactersColumns.user_id, DatabaseCharactersColumns.guild_id])

    # cast the resulting series to a dict of uid -> character name pairs
    names: dict[CharacterUID, str] = almost.to_dict()

    cache[search_index] = names

  else:
    names: dict[CharacterUID, str] = cached_query

  # iterate through and flip the dict's keys and values via dict comprehension
  # during comprehension locate any dict entries with identical character names, and replace their uids with an instance
  # of DiscriminateChoices with the two character uids prepassed.
  fixed = {}
  for uid, name in names.items():
    if name in fixed:
      discrim = DiscriminateChoices({uid: f"{name} - {uid}", fixed[name]: f"{name} - {fixed[name]}"})
      fixed[name] = discrim
    else:
      fixed[name] = [uid]

  options: dict[str, DiscriminateChoices | CharacterUID] = fixed

  # rapidfuzz the user_input against the character name keys of the resulting dict
  matches = [option for option, _, _ in extract(user_input, options.keys(), limit=5)]

  return {match: options[match] for match in matches}
