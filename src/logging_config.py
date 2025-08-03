import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from typing import Literal, Optional

from rich.console import Console, ConsoleRenderable
from rich.logging import RichHandler
from rich.traceback import Traceback

RICH_CONSOLE = Console()

PROJECT_NAME = "SwallowBot"

max_width = 40

logging_timestamp_fmt = "%b, %d %a %I:%M %p"


class FixedRichHandler(RichHandler):
  def render(
    self,
    *,
    record: logging.LogRecord,
    traceback: Optional[Traceback],
    message_renderable: ConsoleRenderable,
  ) -> ConsoleRenderable:
    """Render log for display.

    Args:
        record (LogRecord): logging Record.
        traceback (Optional[Traceback]): Traceback instance or None for no Traceback.
        message_renderable (ConsoleRenderable): Renderable (typically Text) containing log message contents.

    Returns:
        ConsoleRenderable: Renderable to display log.
    """

    pathpath = Path(record.pathname)

    if "site-packages" in pathpath.parts:
      libname_index = pathpath.parts.index("site-packages") + 1
    elif PROJECT_NAME in pathpath.parts:
      libname_index = pathpath.parts.index(PROJECT_NAME)
    elif "Lib" in pathpath.parts:
      libname_index = pathpath.parts.index("Lib") + 1
    else:
      libname_index = 0

    path = ".".join(pathpath.parts[libname_index:])

    level = self.get_level_text(record)
    time_format = None if self.formatter is None else self.formatter.datefmt
    log_time = datetime.fromtimestamp(record.created)

    return self._log_render(
      self.console,
      [message_renderable, traceback] if traceback else [message_renderable],
      log_time=log_time,
      time_format=time_format,
      level=level,
      path=path,
      line_no=record.lineno,
      link_path=record.pathname if self.enable_link_path else None,
    )


class FixedLogRecord(logging.LogRecord):
  def __init__(self, *args, **kwargs):
    global max_width
    pathpath = Path(args[2])

    if "site-packages" in pathpath.parts:
      libname_index = pathpath.parts.index("site-packages") + 1
      libname = pathpath.parts[libname_index]
    elif PROJECT_NAME in pathpath.parts:
      libname_index = pathpath.parts.index(PROJECT_NAME)
      libname = pathpath.parts[libname_index]
    elif "Lib" in pathpath.parts:
      libname_index = pathpath.parts.index("Lib") + 1
      libname = pathpath.parts[libname_index]
    else:
      libname_index = 0
      libname = PROJECT_NAME

    libpath = ".".join(pathpath.parts[libname_index:])

    length = len(libpath)

    if length > max_width:
      max_width = length
      with open("max_width.txt", "w") as f:
        f.write(str(max_width))
      print(f"New max width: {max_width}")

    self.libname = libname
    self.libpath = libpath

    super().__init__(*args, **kwargs)


class FixedFormatter(logging.Formatter):
  default_msec_format = None
  converter = datetime.fromtimestamp  # type: ignore

  def formatTime(self, record, datefmt=None):
    """
    Return the creation time of the specified LogRecord as formatted text.

    This method should be called from format() by a formatter which
    wants to make use of a formatted time. This method can be overridden
    in formatters to provide for any specific requirement, but the
    basic behaviour is as follows: if datefmt (a string) is specified,
    it is used with time.strftime() to format the creation time of the
    record. Otherwise, an ISO8601-like (or RFC 3339-like) format is used.
    The resulting string is returned. This function uses a user-configurable
    function to convert the creation time to a tuple. By default,
    time.localtime() is used; to change this for a particular formatter
    instance, set the 'converter' attribute to a function with the same
    signature as time.localtime() or time.gmtime(). To change it for all
    formatters, for example if you want all logging times to be shown in GMT,
    set the 'converter' attribute in the Formatter class.
    """
    dt = self.converter(record.created)
    if datefmt:
      s = dt.strftime(datefmt)  # type: ignore
    else:
      s = dt.strftime(self.default_time_format)  # type: ignore
      if self.default_msec_format:
        s = self.default_msec_format % (s, record.msecs)
    return s


CWD = Path.cwd()

LOGGING_BASE_NAME = "SwallowBot"

LOG_LOC_FOLDER = CWD / "logs"
LOG_LOC_FOLDER.mkdir(exist_ok=True)
DEBUG_LOG_LOC = LOG_LOC_FOLDER / f"{LOGGING_BASE_NAME}_debug.log"
INFO_LOG_LOC = LOG_LOC_FOLDER / f"{LOGGING_BASE_NAME}.log"


LOGGING_TYPE: Literal["daily", "per_run"] = "daily"


daily_debug_handler = TimedRotatingFileHandler(
  DEBUG_LOG_LOC, when="midnight", backupCount=14, delay=True
)
daily_info_handler = TimedRotatingFileHandler(
  INFO_LOG_LOC, when="midnight", backupCount=14, delay=True
)

per_run_debug_handler = RotatingFileHandler(DEBUG_LOG_LOC, maxBytes=0, backupCount=30, delay=True)
per_run_info_handler = RotatingFileHandler(INFO_LOG_LOC, maxBytes=0, backupCount=30, delay=True)

if LOGGING_TYPE == "per_run":
  per_run_debug_handler.doRollover()
  per_run_info_handler.doRollover()


def configure_logging():
  logging.setLogRecordFactory(FixedLogRecord)

  root = logging.getLogger()
  root.setLevel(logging.DEBUG if __debug__ else logging.INFO)

  debugging_file_handler = daily_debug_handler if LOGGING_TYPE == "daily" else per_run_debug_handler
  debugging_file_handler.setLevel(logging.DEBUG)

  info_file_handler = daily_info_handler if LOGGING_TYPE == "daily" else per_run_info_handler
  info_file_handler.setLevel(logging.INFO)

  # console_error_handler = logging.StreamHandler(sys.stderr)
  # console_error_handler.setLevel(logging.ERROR)
  # console_info_handler = logging.StreamHandler(sys.stdout)
  # console_info_handler.setLevel(logging.INFO)

  console_info_handler = FixedRichHandler(
    # level=logging.DEBUG if __debug__ else logging.INFO,
    console=RICH_CONSOLE,
    rich_tracebacks=True,
    log_time_format=logging_timestamp_fmt,
  )

  formatter = FixedFormatter(
    fmt=f"[{{asctime}}] {{levelname: >8}} | {{libpath: <{max_width}}} | {{message}}",
    datefmt=logging_timestamp_fmt,
    style="{",
  )

  debugging_file_handler.setFormatter(formatter)
  info_file_handler.setFormatter(formatter)
  # console_error_handler.setFormatter(formatter)
  # console_info_handler.setFormatter(formatter)

  root.addHandler(debugging_file_handler)
  root.addHandler(info_file_handler)
  # root.addHandler(console_error_handler)
  root.addHandler(console_info_handler)

  # if __debug__:
  #   console_debug_handler = FixedRichHandler(
  #     level=logging.DEBUG,
  #     console=RICH_CONSOLE,
  #     rich_tracebacks=True,
  #     log_time_format=logging_timestamp_fmt,
  #   )
  #   # console_debug_handler.setFormatter(formatter)
  #   root.addHandler(console_debug_handler)
