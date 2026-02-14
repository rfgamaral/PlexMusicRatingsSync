import sys
from os import getenv
from shutil import copyfile

import yaml

from plex_music_ratings_sync.logger import log_error, log_info
from plex_music_ratings_sync.util.paths import (
    get_config_dir,
    get_config_file_path,
    get_template_file_path,
)

_config = None
"""User configuration data."""

_ENV_OVERRIDES = {
    "PMRS_PLEX_URL": "url",
    "PMRS_PLEX_TOKEN": "token",
    "PMRS_PLEX_LIBRARIES": "libraries",
}
"""Mapping of environment variable names to plex config keys."""


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

    if not isinstance(_config, dict):
        _config = {}

    _apply_env_overrides()


def _apply_env_overrides():
    """Override configuration values with PMRS_PLEX_* environment variables."""
    overrides = {}

    for env_var, key in _ENV_OVERRIDES.items():
        value = getenv(env_var)

        if value is None:
            continue

        value = value.strip()

        if not value:
            continue

        overrides[key] = value

    if not overrides:
        return

    if not isinstance(_config.get("plex"), dict):
        _config["plex"] = {}

    for key, value in overrides.items():
        if key == "libraries":
            _config["plex"][key] = [
                lib.strip() for lib in value.split(",") if lib.strip()
            ]
        else:
            _config["plex"][key] = value


def get_plex_config():
    """Retrieve the Plex configuration."""
    plex_config = _config.get("plex", {})

    overridden = [
        key for env_var, key in _ENV_OVERRIDES.items() if getenv(env_var, "").strip()
    ]

    if overridden:
        log_info(f"Config overridden by environment: **{', '.join(overridden)}**")

    if not isinstance(plex_config.get("url"), str) or not isinstance(
        plex_config.get("token"), str
    ):
        log_error("The Plex configuration is not valid")
        sys.exit(1)

    libraries = plex_config.get("libraries")

    if not isinstance(libraries, list) or not all(
        isinstance(lib, str) and lib.strip() for lib in libraries
    ):
        log_error("The Plex libraries configuration is not valid")
        sys.exit(1)

    return plex_config
