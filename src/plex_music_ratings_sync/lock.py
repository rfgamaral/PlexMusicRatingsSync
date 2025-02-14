import atexit
import fcntl
import sys
from pathlib import Path

from plex_music_ratings_sync import APP_NAME

_process_lock = None
"""File descriptor for the process lock."""

_process_lock_file = Path("/run/lock/plex_music_ratings_sync.lock")
"""Path to the lock file."""


def _release_process_lock():
    """Release the process lock and cleanup."""
    global _process_lock

    if _process_lock:
        fcntl.flock(_process_lock, fcntl.LOCK_UN)
        _process_lock.close()

        try:
            _process_lock_file.unlink()
        except FileNotFoundError:
            pass


def acquire_process_lock():
    """Try to acquire the process lock. Exit if already locked."""
    global _process_lock

    try:
        _process_lock = open(_process_lock_file, "w")
        fcntl.flock(_process_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)

        atexit.register(_release_process_lock)
    except (IOError, OSError):
        print(f"Another instance of {APP_NAME} is already running. Exiting.")
        sys.exit(1)
