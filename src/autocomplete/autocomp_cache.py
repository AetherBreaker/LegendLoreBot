from collections import UserDict
from collections.abc import Callable, Hashable
from functools import partial
from sys import getsizeof
from typing import Any, Concatenate, ParamSpec, TypeVar, overload


class AutocompCache[Val_T](UserDict):
  def __init__(self, max_size: int = 5120, *args: Any, **kwargs: Any) -> None:
    super().__init__(*args, **kwargs)
    self.data: dict[Hashable, Val_T]
    self.max_size = max_size

  def __setitem__(self, key: Hashable, item: Val_T) -> None:
    if getsizeof(self) > self.max_size:
      self.data.clear()
    super().__setitem__(key, item)

  def get(self, key: Hashable, default=None) -> Val_T | None:
    return super().get(key, default)


SubP = ParamSpec("SubP")
SubR = TypeVar("SubR")


@overload
def prepass_cache[SubR, **SubP](
  func: None = None, /, *, max_size: int = 5120
) -> Callable[[Callable[Concatenate[AutocompCache, SubP], SubR]], Callable[SubP, SubR]]: ...


@overload
def prepass_cache[SubR, **SubP](func: Callable[Concatenate[AutocompCache, SubP], SubR], /, *, max_size: int = 5120) -> Callable[SubP, SubR]: ...


# create a decorator that creates an AutocompCache instance that will be shared across all instances of
# the decorated function and prepass it into the decorated function using functools.partial
def prepass_cache[SubR, **SubP](
  func=None, /, *, max_size=5120
) -> Callable[[Callable[Concatenate[AutocompCache[Any], SubP], SubR]], Callable[SubP, SubR]] | Callable[SubP, SubR]:
  if func is None:

    def decorator(f: Callable[Concatenate[AutocompCache, SubP], SubR], /) -> Callable[SubP, SubR]:
      cache = AutocompCache(max_size=max_size)
      return partial(f, cache)

    return decorator

  cache = AutocompCache(max_size=max_size)
  return partial(func, cache)
