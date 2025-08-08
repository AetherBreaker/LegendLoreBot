if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()


from logging import getLogger

from typing_custom.abc import SingletonType

logger = getLogger(__name__)



class DatabaseCache(metaclass=SingletonType):
  def __init__(self) -> None: ...

  async def refresh_cache(self) -> None: ...
