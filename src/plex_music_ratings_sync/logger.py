import logging
import re
from inspect import currentframe
from pathlib import Path

from colorama import Fore, Style

from plex_music_ratings_sync import APP_NAME
from plex_music_ratings_sync.util.paths import get_log_dir, get_log_file_path

MAX_LOG_FILES = 7
"""Maximum number of log files to keep."""

_logger = None
"""Application logger instance."""


class PlainFormatter(logging.Formatter):
    """A formatter that uses standard log format for file output."""

    def __init__(self):
        super().__init__(
            fmt="%(asctime)s.%(msecs)03d %(levelname)-8s %(pathname)-12s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    def format(self, record):
        """
        Format the log record using standard format and strip highlight/dim markers.
        """
        record.msg = re.sub(r"\*\*|\_\_", "", record.getMessage())
        record.pathname = Path(getattr(record, "caller_pathname", record.pathname)).stem

        return super().format(record)


class ColoredFormatter(logging.Formatter):
    """
    A custom formatter that adds colors and styling to log messages.

    This formatter provides:
    - Colored timestamp, log levels, and messages
    - Support for indentation using the 'indent' attribute
    - Highlighting of text marked with **
    - Dimming of text marked with __
    - Simplified filename display in log messages
    """

    TIME_COLOR = Fore.WHITE
    LEVEL_COLORS = {
        "DEBUG": Fore.GREEN,
        "INFO": Fore.BLUE,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "CRITICAL": Fore.MAGENTA,
    }
    TAG_COLOR = Fore.CYAN + Style.BRIGHT
    MESSAGE_COLOR = Fore.WHITE + Style.BRIGHT
    HIGHLIGHT_COLOR = "\033[38;5;229m"
    DIM_COLOR = "\033[38;5;232m"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.indent_char = "  "

    def _highlight_text(self, message):
        """Highlight the message between double asterisks."""
        return re.sub(
            r"\*\*(.*?)\*\*", f"{self.HIGHLIGHT_COLOR}\\1{Style.RESET_ALL}", message
        )

    def _dim_text(self, message):
        """Dim the message between double underscores."""
        return re.sub(
            r"\_\_(.*?)\_\_", f"{self.DIM_COLOR}\\1{Style.RESET_ALL}", message
        )

    def format(self, record):
        """Format the log record with colors and custom styling."""
        timestamp = self.formatTime(record, datefmt="%Y-%m-%d %H:%M:%S")
        timestamp_text = f"[{self.TIME_COLOR}{timestamp}{Style.RESET_ALL}]"

        level_color = self.LEVEL_COLORS.get(record.levelname, "")
        level_text = f"{level_color}{record.levelname:8}{Style.RESET_ALL}"

        filename = f"{Path(getattr(record, 'caller_pathname', record.pathname)).stem}"
        filename_text = f"{self.TAG_COLOR}{filename:9}{Style.RESET_ALL}"

        indentation = self.indent_char * getattr(record, "indent", 0)
        message = self._highlight_text(record.getMessage())
        message = self._dim_text(message)
        message_text = f"{self.MESSAGE_COLOR}{indentation}{message}{Style.RESET_ALL}"

        colored_log = f"{timestamp_text} {level_text} {filename_text} {message_text}"

        return colored_log


def init_logging(quiet=None, verbose=None):
    """
    Initialize the logger with appropriate configuration.

    Configures the logger based on the application config and command line arguments.
    Supports different log levels with colored output for console, and plain output for
    file. The log file is truncated on initialization.
    """
    global _logger

    log_dir = get_log_dir()

    if not log_dir.exists():
        log_dir.mkdir(parents=True, exist_ok=True)

    _logger = logging.getLogger(APP_NAME)
    _logger.propagate = False

    _logger.setLevel(
        logging.ERROR if quiet else logging.DEBUG if verbose else logging.INFO
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ColoredFormatter())
    _logger.addHandler(console_handler)

    file_handler = logging.FileHandler(get_log_file_path(), mode="w")
    file_handler.setFormatter(PlainFormatter())
    _logger.addHandler(file_handler)


def _get_caller_info():
    """Get the filename and line number of the caller of the logging function."""
    current_frame = currentframe()

    if current_frame is not None:
        caller_frame = current_frame.f_back.f_back

        if caller_frame is not None:
            return (caller_frame.f_code.co_filename, caller_frame.f_lineno)

    return (__file__, 0)


def log_debug(message, indent=0):
    """Log a debug message with the specified indentation level."""
    pathname, lineno = _get_caller_info()

    _logger.debug(
        message,
        extra={"indent": indent, "caller_pathname": pathname, "caller_lineno": lineno},
    )


def log_info(message, indent=0):
    """Log an info message with the specified indentation level."""
    pathname, lineno = _get_caller_info()

    _logger.info(
        message,
        extra={"indent": indent, "caller_pathname": pathname, "caller_lineno": lineno},
    )


def log_warning(message, indent=0):
    """Log a warning message with the specified indentation level."""
    pathname, lineno = _get_caller_info()

    _logger.warning(
        message,
        extra={"indent": indent, "caller_pathname": pathname, "caller_lineno": lineno},
    )


def log_error(message, indent=0):
    """Log an error message with the specified indentation level."""
    pathname, lineno = _get_caller_info()

    _logger.error(
        message,
        extra={"indent": indent, "caller_pathname": pathname, "caller_lineno": lineno},
    )


def log_critical(message, indent=0):
    """Log a critical message with the specified indentation level."""
    pathname, lineno = _get_caller_info()

    _logger.critical(
        message,
        extra={"indent": indent, "caller_pathname": pathname, "caller_lineno": lineno},
    )
