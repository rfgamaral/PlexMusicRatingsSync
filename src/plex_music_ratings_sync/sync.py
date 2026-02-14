import sys
from datetime import datetime
from pathlib import Path

from plexapi.server import PlexServer

from plex_music_ratings_sync.cache import RatingCache
from plex_music_ratings_sync.config import get_plex_config
from plex_music_ratings_sync.logger import log_debug, log_error, log_info, log_warning
from plex_music_ratings_sync.ratings import (
    get_rating_from_file,
    get_rating_from_plex,
    set_rating_to_file,
    set_rating_to_plex,
)
from plex_music_ratings_sync.state import is_clear_cache, is_dry_run, is_no_cache
from plex_music_ratings_sync.util.datetime import format_time

_SUPPORTED_EXTENSIONS = (".flac", ".m4a", ".mp3", ".ogg", ".opus", ".aif", ".aiff")
"""Audio file extensions that are supported for rating synchronization."""


class RatingSync:
    def __init__(self):
        plex_config = get_plex_config()

        try:
            log_info(f"Connecting to Plex server: **{plex_config['url']}**")

            self.plex = PlexServer(plex_config["url"], plex_config["token"])

            log_info(f"Connected to Plex server: **{self.plex.friendlyName}**")
        except Exception as e:
            log_error(f"Failed to connect to Plex server: {e}")
            sys.exit(1)

        self.libraries = plex_config["libraries"]

        if is_dry_run():
            log_warning("Running in dry-run mode (no changes will be made)")

        if is_clear_cache():
            RatingCache.clear()

        if is_no_cache():
            self._cache = None
            log_warning("File rating cache is disabled")
        else:
            self._cache = RatingCache()

        self._stats = {
            "cache_hits": 0,
            "cache_misses": 0,
            "file_updates": 0,
            "plex_updates": 0,
            "skipped_not_found": 0,
            "skipped_unsupported": 0,
        }

    def _process_item(self, item, mode="sync"):
        """
        Process a single track with the specified mode:
        - `sync`: Bidirectional sync between Plex and files
        - `import`: One-way import from audio files to Plex
        - `export`: One-way export from Plex to audio files
        """
        item_start_time = datetime.now()

        file_path = Path(item.media[0].parts[0].file)

        track_index = item.index if item.index is not None else 0

        log_info(
            f"Track: **{track_index:02d}. {item.title}** __({file_path.name})__",
            3,
        )

        try:
            file_stat = file_path.stat()
        except OSError:
            log_warning("▸ File not found on disk", 4)
            self._stats["skipped_not_found"] += 1

            if self._cache is not None:
                self._cache.remove(file_path)

            return

        if file_path.suffix.lower() not in _SUPPORTED_EXTENSIONS:
            log_warning("▸ Skipping unsupported file type", 4)
            self._stats["skipped_unsupported"] += 1
            return

        plex_rating = get_rating_from_plex(item)

        cache_hit = False

        if self._cache is not None:
            cache_hit, file_rating = self._cache.lookup(file_path, file_stat)

        if cache_hit:
            self._stats["cache_hits"] += 1
        else:
            self._stats["cache_misses"] += 1
            file_rating = get_rating_from_file(str(file_path))

            if self._cache is not None:
                self._cache.update(file_path, file_stat, file_rating)

        if mode == "import" and file_rating is not None:
            if plex_rating != file_rating:
                set_rating_to_plex(item, file_rating)
                self._stats["plex_updates"] += 1
            else:
                log_debug("▸ Plex rating already matches file", 4)
        elif mode == "export" and plex_rating is not None:
            if file_rating != plex_rating:
                set_rating_to_file(str(file_path), plex_rating)
                self._update_cache_after_write(file_path, plex_rating)
                self._stats["file_updates"] += 1
            else:
                log_debug("▸ File rating already matches Plex", 4)
        elif mode == "sync":
            if plex_rating != file_rating:
                if plex_rating is not None:
                    set_rating_to_file(str(file_path), plex_rating)
                    self._update_cache_after_write(file_path, plex_rating)
                    self._stats["file_updates"] += 1
                elif file_rating is not None:
                    set_rating_to_plex(item, file_rating)
                    self._stats["plex_updates"] += 1
            else:
                log_debug("▸ Ratings are already in sync", 4)

        item_elapsed_time = datetime.now() - item_start_time

        log_debug(f"▸ Processed in **{format_time(item_elapsed_time)}**", 4)

    def _update_cache_after_write(self, file_path, rating):
        """Re-stat a file after writing tags and update the cache entry."""
        if self._cache is None:
            return

        try:
            new_stat = file_path.stat()
            self._cache.update(file_path, new_stat, rating)
        except OSError:
            pass

    def _process_libraries(self, mode="sync"):
        """Process all configured libraries with the specified mode."""
        total_start_time = datetime.now()
        processed_tracks = 0

        try:
            for library_name in self.libraries:
                log_info(f"Processing Plex library: **{library_name}**")

                music_items = self.plex.library.section(library_name).all()

                if not music_items:
                    log_warning(f"No items found in library: **{library_name}**")
                    continue

                for item in music_items:
                    if hasattr(item, "type") and item.type == "artist":
                        log_info(f"Artist: **{item.title}**", 1)

                        for album in item.albums():
                            album_tracks = album.tracks()
                            album_path = Path(
                                album_tracks[0].media[0].parts[0].file
                            ).parent

                            log_info(
                                f"Album: **{album.title}** __({album_path})__",
                                2,
                            )

                            for track in album_tracks:
                                self._process_item(track, mode=mode)
                                processed_tracks += 1

                                if self._cache is not None:
                                    self._cache.save_if_interval_elapsed()
        finally:
            total_elapsed_item = datetime.now() - total_start_time

            self._log_summary(processed_tracks, total_elapsed_item)

            if self._cache is not None:
                self._cache.save()

    def _log_summary(self, processed_tracks, elapsed_time):
        """Log a summary of the processing run."""

        def fmt(v):
            return f"**{v}**" if v else f"__{v}__"

        summary = f"Processed **{processed_tracks}** tracks in **{format_time(elapsed_time)}**"

        if self._cache is not None:
            summary += f" ({fmt(self._stats['cache_hits'])} cached, {fmt(self._stats['cache_misses'])} read)"

        log_info(summary)

        log_info(
            f"Ratings updated: {fmt(self._stats['file_updates'])} file, {fmt(self._stats['plex_updates'])} Plex",
            1,
        )

        skipped = self._stats["skipped_not_found"] + self._stats["skipped_unsupported"]

        if skipped:
            log_warning(
                f"Skipped: {fmt(self._stats['skipped_not_found'])} not found, {fmt(self._stats['skipped_unsupported'])} unsupported",
                1,
            )

    def sync_ratings(self):
        """Synchronize ratings between Plex and supported audio files."""
        log_info("Synchronization started: **Plex ⇄ Audio Files**")

        self._process_libraries(mode="sync")

        log_info("Synchronization completed: **Plex** ⇄ **Audio Files**")

    def import_ratings(self):
        """Import ratings from audio files into Plex."""
        log_info("Import started: **Audio Files → Plex**")

        self._process_libraries(mode="import")

        log_info("Import completed: **Audio Files → Plex**")

    def export_ratings(self):
        """Export ratings from Plex to audio files."""
        log_info("Export started: **Plex → Audio Files**")

        self._process_libraries(mode="export")

        log_info("Export completed: **Plex → Audio Files**")
