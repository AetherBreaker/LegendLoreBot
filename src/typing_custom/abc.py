if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

from logging import getLogger

from aiologic import Lock

logger = getLogger(__name__)


class SingletonType(type):
  __shared_instance_lock__: Lock

  def __new__(mcs, name, bases, attrs):
    cls = super(SingletonType, mcs).__new__(mcs, name, bases, attrs)
    cls.__shared_instance_lock__ = Lock()
    return cls

  def __call__(self, *args, **kwargs):
    with self.__shared_instance_lock__:
      try:
        return self.__shared_instance__
      except AttributeError:
        self.__shared_instance__ = super(SingletonType, self).__call__(*args, **kwargs)
        return self.__shared_instance__


class SingletonNamedInstances(type):
  __shared_instances__: dict[str, "SingletonNamedInstances"]
  __shared_instance_locks__: dict[str, Lock]

  def __new__(mcs, name, bases, attrs):
    cls = super(SingletonNamedInstances, mcs).__new__(mcs, name, bases, attrs)
    cls.__shared_instances__ = {}
    cls.__shared_instance_locks__ = {}
    return cls

  def __call__(self, name: str, *args, **kwargs):
    with self.__shared_instance_locks__.setdefault(name, Lock()):
      return self.__shared_instances__.setdefault(name, super(SingletonNamedInstances, self).__call__(*args, **kwargs))
