from collections import UserDict
from collections.abc import Callable, Hashable
from functools import partial
from sys import getsizeof
from typing import Any, Concatenate


class AutocompCache[Val_T](UserDict):
  def __init__(self, *args: Any, **kwargs: Any) -> None:
    super().__init__(*args, **kwargs)
    self.data: dict[Hashable, Val_T]

  def __setitem__(self, key: Hashable, item: Val_T) -> None:
    if getsizeof(self) > 5120:
      self.data.clear()
    super().__setitem__(key, item)

  def get(self, key: Hashable, default=None) -> Val_T | None:
    return super().get(key, default)


# create a decorator that creates an AutocompCache instance that will be shared across all instances of
# the decorated function and prepass it into the decorated function using functools.partial
def prepass_cache[R, **P](func: Callable[Concatenate[AutocompCache, P], R]) -> Callable[P, R]:
  cache = AutocompCache()
  return partial(func, cache)
