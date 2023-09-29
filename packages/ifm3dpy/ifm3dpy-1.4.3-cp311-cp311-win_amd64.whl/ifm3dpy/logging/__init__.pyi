"""Provides access for configuring the logging facilities of ifm3d."""
from __future__ import annotations
import ifm3dpy.logging
import typing

__all__ = [
    "LogEntry",
    "LogFormatterJson",
    "LogFormatterText",
    "LogLevel",
    "LogWriter",
    "Logger"
]


class LogEntry():
    """
    Represent a single log entry.
    """
    @property
    def file(self) -> datetime.datetime:
        """
              The time this log entry occured
            

        :type: datetime.datetime
        """
    pass
class LogFormatterJson():
    """
    Formats a give LogEntry as a json object
    """
    @staticmethod
    def format(entry: LogEntry) -> str: 
        """
        Format the LogEntry as a json object
        """
    pass
class LogFormatterText():
    """
    Formats a give LogEntry as a human readable text line
    """
    @staticmethod
    def format(entry: LogEntry) -> str: 
        """
        Format the LogEntry as a human readable text line
        """
    pass
class LogLevel():
    """
    Enum: The log level.

    Members:

      None

      Critical

      Error

      Warning

      Info

      Debug

      Verbose
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    Critical: ifm3dpy.logging.LogLevel # value = <LogLevel.Critical: 1>
    Debug: ifm3dpy.logging.LogLevel # value = <LogLevel.Debug: 5>
    Error: ifm3dpy.logging.LogLevel # value = <LogLevel.Error: 2>
    Info: ifm3dpy.logging.LogLevel # value = <LogLevel.Info: 4>
    None: ifm3dpy.logging.LogLevel # value = <LogLevel.None: 0>
    Verbose: ifm3dpy.logging.LogLevel # value = <LogLevel.Verbose: 6>
    Warning: ifm3dpy.logging.LogLevel # value = <LogLevel.Warning: 3>
    __members__: dict # value = {'None': <LogLevel.None: 0>, 'Critical': <LogLevel.Critical: 1>, 'Error': <LogLevel.Error: 2>, 'Warning': <LogLevel.Warning: 3>, 'Info': <LogLevel.Info: 4>, 'Debug': <LogLevel.Debug: 5>, 'Verbose': <LogLevel.Verbose: 6>}
    pass
class LogWriter():
    """
    Base class for creating custom log writers.
    """
    def __init__(self) -> None: ...
    def write(self, entry: LogEntry) -> None: 
        """
        Called when the given entry should be written
        """
    pass
class Logger():
    """
    Provides access for configuring the logging facilities of ifm3d
    """
    @staticmethod
    def log_level() -> None: 
        """
        Get the active log level, messages below this level will be discarded
        """
    @staticmethod
    def set_log_level(arg0: LogLevel) -> None: 
        """
        Set the active log level, messages below this level will be discarded
        """
    @staticmethod
    def set_writer(arg0: LogWriter) -> None: 
        """
        Set the log writer.
        """
    pass
