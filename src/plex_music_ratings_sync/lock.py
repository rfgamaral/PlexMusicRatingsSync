import atexit
import sys
from pathlib import Path

from filelock import FileLock, Timeout
from platformdirs import user_cache_dir

from plex_music_ratings_sync import APP_NAME

_process_lock_file = Path(user_cache_dir(APP_NAME)) / "process.lock"
"""Path to the single process lock file."""

_process_lock_file.parent.mkdir(parents=True, exist_ok=True)

_process_lock = FileLock(_process_lock_file)
"""File lock to ensure only one instance of the application is running."""


def _cleanup_lock():
    """Release the lock and remove the lock file."""
    try:
        if _process_lock.is_locked:
            _process_lock.release()

        if _process_lock_file.exists():
            _process_lock_file.unlink()
    except Exception:
        pass


def acquire_process_lock():
    """Try to acquire the process lock. Exit if already locked."""
    try:
        _process_lock.acquire(timeout=0.1)

        atexit.register(_cleanup_lock)
    except Timeout:
        print(f"Another instance of {APP_NAME} is already running. Exiting.")
        sys.exit(1)
