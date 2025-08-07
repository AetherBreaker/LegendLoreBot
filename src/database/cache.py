from typing_custom.abc import SingletonType


class DatabaseCache(metaclass=SingletonType):
  def __init__(self) -> None: ...

  async def refresh_cache(self) -> None: ...
