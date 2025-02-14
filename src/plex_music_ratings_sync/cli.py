import sys

import click
import plexapi

from plex_music_ratings_sync import APP_DESCRIPTION, APP_NAME, __version__
from plex_music_ratings_sync.config import init_config
from plex_music_ratings_sync.lock import acquire_process_lock
from plex_music_ratings_sync.logger import init_logging, log_info, log_warning
from plex_music_ratings_sync.state import set_dry_run
from plex_music_ratings_sync.sync import RatingSync
from plex_music_ratings_sync.util.paths import (
    get_config_dir,
    get_config_file_path,
    get_log_dir,
    get_log_file_path,
)


def _validate_verbosity_flags(ctx, param, value):
    """Validate that quiet and verbose flags are not used together."""
    if value:
        other_param = "verbose" if param.name == "quiet" else "quiet"

        if ctx.params.get(other_param):
            raise click.UsageError(
                f"--{other_param} and --{param.name} are mutually exclusive"
            )

    return value


@click.group(invoke_without_command=True, help=APP_DESCRIPTION)
@click.option("--version", is_flag=True, help="Show program version and exit")
@click.option("--help", is_flag=True, help="Show this help message and exit")
@click.pass_context
def cli(ctx, version, help):
    """Entry point for the CLI application that handles global flags and subcommands."""
    init_config()

    if version:
        click.echo(f"{APP_NAME} v{__version__}")
        ctx.exit()
    elif help:
        click.echo(ctx.get_help())
        ctx.exit()
    elif ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


def _colorize_version(text):
    """Format text in bright cyan."""
    return click.style(text, fg="bright_cyan")


def _colorize_path(text):
    """Format text in bright magenta."""
    return click.style(text, fg="bright_magenta")


@cli.command("info")
def show_info():
    """Show system information and configuration paths."""
    click.echo(f"{APP_NAME} Version: {_colorize_version(__version__)}")
    click.echo(f"Python Version: {_colorize_version(sys.version.split()[0])}")
    click.echo(f"PlexAPI Version: {_colorize_version(plexapi.VERSION)}")
    click.echo(f"Config Directory: {_colorize_path(get_config_dir())}")
    click.echo(f"Config File: {_colorize_path(get_config_file_path())}")
    click.echo(f"Log Directory: {_colorize_path(get_log_dir())}")
    click.echo(f"Log File: {_colorize_path(get_log_file_path())}")


@cli.command("sync")
@click.option(
    "--dry-run", is_flag=True, help="Simulates syncing ratings without applying changes"
)
@click.option(
    "--quiet",
    is_flag=True,
    help="Suppress all output except errors",
    callback=_validate_verbosity_flags,
)
@click.option(
    "--verbose",
    is_flag=True,
    help="Show detailed debug information",
    callback=_validate_verbosity_flags,
)
def sync_ratings(dry_run, quiet, verbose):
    """
    Synchronize ratings between Plex and supported audio files.

    When ratings match between Plex and files, no action is taken. For mismatched
    ratings, Plex's rating takes precedence and overwrites the file. When a rating
    exists in only one place, it will be copied to the other location.
    """
    acquire_process_lock()

    init_logging(quiet=quiet, verbose=verbose)
    log_info(f"{APP_NAME} v{__version__}")

    set_dry_run(dry_run)

    try:
        RatingSync().sync_ratings()
    except KeyboardInterrupt:
        log_warning("Synchronization operation interrupted by user")
        sys.exit(1)


@cli.command("import")
@click.option(
    "--dry-run", is_flag=True, help="Simulates importing ratings without making changes"
)
@click.option(
    "--quiet",
    is_flag=True,
    help="Suppress all output except errors",
    callback=_validate_verbosity_flags,
)
@click.option(
    "--verbose",
    is_flag=True,
    help="Show detailed debug information",
    callback=_validate_verbosity_flags,
)
def import_ratings(dry_run, quiet, verbose):
    """
    Import ratings from audio files into Plex.

    This is a one-way operation that reads ratings from audio file metadata
    and updates the corresponding tracks in Plex. Useful for initial setup
    or recovering Plex ratings from files.
    """
    acquire_process_lock()

    init_logging(quiet=quiet, verbose=verbose)
    log_info(f"{APP_NAME} v{__version__}")

    set_dry_run(dry_run)

    try:
        RatingSync().import_ratings()
    except KeyboardInterrupt:
        log_warning("Import operation interrupted by user")
        sys.exit(1)


@cli.command("export")
@click.option(
    "--dry-run", is_flag=True, help="Simulates exporting ratings without making changes"
)
@click.option(
    "--quiet",
    is_flag=True,
    help="Suppress all output except errors",
    callback=_validate_verbosity_flags,
)
@click.option(
    "--verbose",
    is_flag=True,
    help="Show detailed debug information",
    callback=_validate_verbosity_flags,
)
def export_ratings(dry_run, quiet, verbose):
    """
    Export ratings from Plex to audio files.

    This is a one-way operation that reads ratings from Plex
    and updates the corresponding audio files' metadata. Useful for
    backing up Plex ratings or preparing files for use in other players.
    """
    acquire_process_lock()

    init_logging(quiet=quiet, verbose=verbose)
    log_info(f"{APP_NAME} v{__version__}")

    set_dry_run(dry_run)

    try:
        RatingSync().export_ratings()
    except KeyboardInterrupt:
        log_warning("Export operation interrupted by user")
        sys.exit(1)
