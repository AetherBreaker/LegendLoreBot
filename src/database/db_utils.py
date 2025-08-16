from disnake import Guild, User
from validation.models.db_entries import GuildDBEntryModel, UserDBEntryModel

from database.cache import DatabaseCache


async def ensure_user_exists(user: User, guild: Guild) -> None:
  db = DatabaseCache()
  if not await db.users.check_exists((user.id, guild.id)):
    await db.users.append_row(UserDBEntryModel(user_id=user.id, guild_id=guild.id, user_name=user.name))


async def ensure_guild_exists(guild: Guild) -> None:
  db = DatabaseCache()
  if not await db.guilds.check_exists(guild.id):
    await db.guilds.append_row(GuildDBEntryModel(guild_id=guild.id, guild_name=guild.name))
