if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

from logging import getLogger

from aiologic import Lock


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
