import sys
from shutil import copyfile

import yaml

from plex_music_ratings_sync.logger import log_error
from plex_music_ratings_sync.util.paths import (
    get_config_dir,
    get_config_file_path,
    get_template_file_path,
)

_config = None
"""User configuration data."""


def _create_config(config_file_path):
    """Create a new configuration file from the template."""
    template_path = get_template_file_path()

    copyfile(template_path, config_file_path)


def init_config():
    """Initialize the configuration by loading and parsing the YAML config file."""
    global _config

    config_dir = get_config_dir()

    if not config_dir.exists():
        config_dir.mkdir(parents=True, exist_ok=True)

    config_file_path = get_config_file_path()

    if not config_file_path.exists():
        _create_config(config_file_path)

    with open(config_file_path, "r") as config_file:
        _config = yaml.safe_load(config_file)


def get_plex_config():
    """Retrieve the Plex configuration."""
    plex_config = _config.get("plex", {})

    if not isinstance(plex_config.get("url"), str) or not isinstance(
        plex_config.get("token"), str
    ):
        log_error("The Plex configuration is not valid")
        sys.exit(1)

    return plex_config
