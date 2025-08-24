if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

from logging import getLogger

from component_menus.choice_discriminator import DiscriminateChoices
from database.cache import DatabaseCache, DatabaseCharactersColumns
from disnake import ApplicationCommandInteraction
from rapidfuzz.process import extract
from typing_custom import CharacterUID
from typing_custom.dataframe_column_names import DatabaseGuildsColumns
from validation.models.db_entries import CharacterClassesModel, GuildClassList

from autocomplete.autocomp_cache import AutocompCache, prepass_cache

logger = getLogger(__name__)

type CharacterName = str

type AutocompChoice = CharacterName
type AutocompValue = CharacterUID | DiscriminateChoices


@prepass_cache(name="charname")
async def autocomp_self_charname(cache: AutocompCache[set[CharacterName]], inter: ApplicationCommandInteraction, user_input: str) -> list[str]:
  # Grab the singleton instance of our database accessor
  db = DatabaseCache()

  search_index = (
    (slice(None), inter.user.id, inter.guild_id, slice(None))
    if inter.guild_id is not None
    else (slice(None), inter.user.id, slice(None), slice(None))
  )

  cached_query = cache.get(search_index)
  if cached_query is None:
    # enter context manager for db.characters
    async with db.characters as characters:
      # select the character names column, filtered by the current interactions guildid and userid
      selection = characters.loc[search_index, DatabaseCharactersColumns.character_name]

    # cast the resulting series to a dict of uid -> character name pairs
    names: set[CharacterName] = set(selection.tolist())

    cache[search_index] = names

  else:
    names: set[CharacterName] = cached_query

  # rapidfuzz the user_input against the character name keys of the resulting dict
  return [option for option, _, _ in extract(user_input, names, limit=5)]


type ClassName = str


@prepass_cache(max_size=2048)
async def autocomp_all_classnames(cache: AutocompCache[set[ClassName]], inter: ApplicationCommandInteraction, user_input: str) -> list[str]:
  # Grab the singleton instance of our database accessor
  db = DatabaseCache()

  char_name: str | None = inter.filled_options.get("character_name")

  if char_name is None:
    return []

  if inter.guild_id is None:
    search_index = (inter.user.id, char_name)
  else:
    search_index = inter.guild_id

  cached_query = cache.get(search_index)
  if cached_query is None:
    if isinstance(search_index, tuple):
      guild_id: int = await db.characters.read_value(search_index, DatabaseCharactersColumns.guild_id)
      search_index = guild_id

    result: GuildClassList = await db.guilds.read_value(search_index, DatabaseGuildsColumns.class_list)

    classes = result.root

    cache[search_index] = classes

  else:
    classes: set[ClassName] = cached_query

  # rapidfuzz the user_input against the character name keys of the resulting dict
  return [option for option, _, _ in extract(user_input, classes, limit=5)]


@prepass_cache(max_size=1024)
async def autocomp_char_classname(cache: AutocompCache[set[ClassName]], inter: ApplicationCommandInteraction, user_input: str) -> list[str]:
  # Grab the singleton instance of our database accessor
  db = DatabaseCache()

  char_name = inter.filled_options.get("character_name")

  if char_name is None:
    return []

  search_index = (inter.user.id, inter.guild_id, char_name) if inter.guild_id is not None else (inter.user.id, char_name)

  cached_query = cache.get(search_index)
  if cached_query is None:
    result: CharacterClassesModel = await db.characters.read_value(search_index, DatabaseCharactersColumns.classes)

    classes = set(result.root.keys())

    cache[search_index] = classes

  else:
    classes: set[ClassName] = cached_query

  # rapidfuzz the user_input against the character name keys of the resulting dict
  return [option for option, _, _ in extract(user_input, classes, limit=5)]
