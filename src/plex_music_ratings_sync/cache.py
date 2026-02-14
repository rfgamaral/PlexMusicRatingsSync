import json
import os
import tempfile
from datetime import datetime, timedelta

from plex_music_ratings_sync.logger import log_debug, log_info, log_warning
from plex_music_ratings_sync.util.paths import get_cache_dir, get_cache_file_path

_CACHE_SCHEMA_VERSION = 1
"""Increment this when the cache format changes to invalidate old caches."""

_SAVE_INTERVAL = timedelta(minutes=5)
"""How often the cache is periodically saved to disk during a run."""


class RatingCache:
    def __init__(self):
        self._entries = {}
        self._dirty = False
        self._last_save_time = datetime.now()
        self._load()

    def _load(self):
        """Load the cache from disk, starting fresh on missing, corrupt, or outdated files."""
        cache_file = get_cache_file_path()

        if not cache_file.exists():
            return

        try:
            with open(cache_file, "r") as f:
                data = json.load(f)

            if data.get("schema_version") != _CACHE_SCHEMA_VERSION:
                log_warning("Cache schema version mismatch, starting with empty cache")
                self._dirty = True
                return

            self._entries = data.get("entries", {})

            log_info(f"Loaded **{len(self._entries)}** cached file ratings")
        except (json.JSONDecodeError, KeyError, TypeError):
            log_warning("Cache file is corrupted, starting with empty cache")
            self._dirty = True

    def lookup(self, file_path, stat_result):
        """
        Return the cached rating if the file's mtime_ns and size match.
        Returns a (hit, rating) tuple. hit=True means cache was valid.
        rating can be None (meaning "no rating" was cached).
        """
        key = str(file_path)
        entry = self._entries.get(key)

        if entry is None:
            return False, None

        if (
            entry.get("mtime_ns") == stat_result.st_mtime_ns
            and entry.get("size") == stat_result.st_size
        ):
            log_debug("▸ Using cached file rating", 4)
            return True, entry.get("rating")

        return False, None

    def update(self, file_path, stat_result, rating):
        """Store or update a cache entry for the given file."""
        self._entries[str(file_path)] = {
            "mtime_ns": stat_result.st_mtime_ns,
            "size": stat_result.st_size,
            "rating": rating,
        }
        self._dirty = True

    def remove(self, file_path):
        """Remove a cache entry (e.g., file no longer exists)."""
        key = str(file_path)

        if key in self._entries:
            del self._entries[key]
            self._dirty = True

    def save(self):
        """Atomically write the cache to disk if dirty."""
        if not self._dirty:
            return

        cache_file = get_cache_file_path()
        cache_dir = get_cache_dir()

        if not cache_dir.exists():
            cache_dir.mkdir(parents=True, exist_ok=True)

        data = {
            "schema_version": _CACHE_SCHEMA_VERSION,
            "entries": self._entries,
        }

        try:
            fd, tmp_path = tempfile.mkstemp(dir=cache_dir, suffix=".tmp")

            try:
                with os.fdopen(fd, "w") as f:
                    json.dump(data, f, separators=(",", ":"))

                os.replace(tmp_path, cache_file)
            except BaseException:
                os.unlink(tmp_path)
                raise

            self._dirty = False

            self._last_save_time = datetime.now()

            log_info(f"Saved **{len(self._entries)}** cached file ratings")
        except OSError as e:
            log_warning(f"Failed to save rating cache: {e}")

    def save_if_interval_elapsed(self):
        """Save the cache if enough time has passed since the last save."""
        if datetime.now() - self._last_save_time >= _SAVE_INTERVAL:
            self.save()

    @staticmethod
    def clear():
        """Delete the cache file from disk."""
        cache_file = get_cache_file_path()

        if cache_file.exists():
            cache_file.unlink()
            log_warning("Rating cache cleared")
