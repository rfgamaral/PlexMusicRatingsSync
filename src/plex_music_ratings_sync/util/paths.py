from os import getenv
from pathlib import Path

from platformdirs import user_config_dir, user_log_dir

from plex_music_ratings_sync import APP_NAME


def get_config_dir():
    """Return the path to the config directory."""
    return Path(getenv("PMRS_CONFIG_DIR", user_config_dir(APP_NAME)))


def get_config_file_path():
    """Return the path to the user config file."""
    return get_config_dir() / "config.yml"


def get_log_dir():
    """Return the path to the log directory."""
    return Path(getenv("PMRS_LOG_DIR", user_log_dir(APP_NAME)))


def get_log_file_path():
    """Return the path to the log file."""
    return get_log_dir() / f"{APP_NAME}.log"


def get_template_file_path():
    """Get the path to the config template file."""
    return Path(__file__).parent.parent / "config.template.yml"
