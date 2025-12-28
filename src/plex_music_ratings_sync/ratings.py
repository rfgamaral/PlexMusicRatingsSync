from mutagen.aiff import AIFF
from mutagen.flac import FLAC
from mutagen.id3 import ID3, POPM
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.oggopus import OggOpus
from mutagen.oggvorbis import OggVorbis

from plex_music_ratings_sync.logger import log_debug, log_error, log_info
from plex_music_ratings_sync.state import is_dry_run

_PRIMARY_MP3_RATING_MAP = {
    0: 0,
    1: 13,
    2: 1,
    3: 54,
    4: 64,
    5: 118,
    6: 128,
    7: 186,
    8: 196,
    9: 242,
    10: 255,
}
"""
The primary rating map for our Plex POPM tag (maintains compatibility with
MusicBee/MediaMonkey). Supports half-star ratings (1-10 with 0.5 increments) through
carefully chosen POPM values that these players recognize as intermediate ratings.
"""

_ALTERNATIVE_MP3_RATING_MAP = {0: 0, 2: 1, 4: 64, 6: 128, 8: 196, 10: 255}
"""
The alternative rating map used by apps like WMP, Winamp, Foobar, and possibly others.
Only supports full-star ratings (2,4,6,8,10) as these players use a simplified 5-star
system.
"""

_PICARD_MP3_RATING_MAP = {0: 0, 2: 51, 4: 102, 6: 153, 8: 204, 10: 255}
"""
The rating map used by Picard with a linear scale of 51 points per star. Only supports
full-star ratings (2,4,6,8,10) despite using linear increments.
"""

_KNOWN_PRIMARY_RATING_PLAYERS = [
    "MusicBee",
    "no@email",  # MediaMonkey
    "Plex",
]
"""
Email identifiers for players known to use the primary rating map with half-star
support.
"""

_AIFF_FORMATS = {".aif": "AIFF", ".aiff": "AIFF"}
"""
Maps file extensions to their format names for AIFF audio files that use ID3 tags for
metadata storage.
"""

_VORBIS_FORMATS = {".flac": "FLAC", ".ogg": "OGG", ".opus": "OPUS"}
"""
Maps file extensions to their format names for audio files that use Vorbis Comments
for metadata storage.
"""


def _popm_rating_to_plex(popm_rating, email=None):
    """
    Convert MP3 POPM ratings to Plex's 1-10 scale.

    Different music players use different schemes for storing ratings in MP3 files:
    - MusicBee/MediaMonkey/Plex use a non-linear scale with half stars support (0.5-5.0)
    - WMP/Winamp/Foobar/Others use a simpler scale limited to full stars only (1-5)
    - Picard uses a linear scale limited to full stars only (1-5)

    When no known scheme is detected, falls back to linear interpolation which preserves
    the original granularity of the rating, effectively supporting half stars.
    """
    if popm_rating == 0 or popm_rating is None:
        return None

    if email in _KNOWN_PRIMARY_RATING_PLAYERS:
        for plex_rating, popm_value in _PRIMARY_MP3_RATING_MAP.items():
            if popm_rating == popm_value:
                return plex_rating

    for map_to_try in [_ALTERNATIVE_MP3_RATING_MAP, _PICARD_MP3_RATING_MAP]:
        for plex_rating, popm_value in map_to_try.items():
            if popm_rating == popm_value:
                return plex_rating

    return min(10, max(1, round((popm_rating / 255) * 9 + 1)))


def _plex_rating_to_popm(plex_rating):
    """
    Convert Plex's 1-10 ratings to MP3 POPM format.

    When writing ratings back to MP3 files, we exclusively use the primary rating map
    (compatible with MusicBee/MediaMonkey) since it offers the most granular control
    with distinct values for all ratings 1-10. This ensures maximum compatibility when
    these files are later read by other music players, as most players can interpret
    this scheme correctly even if they don't use it natively.
    """
    if plex_rating == 0 or plex_rating is None:
        return 0

    return _PRIMARY_MP3_RATING_MAP.get(plex_rating, 0)


def _get_rating_from_mp3(file_path):
    """
    Read rating from an MP3 file's POPM tag. Attempts to read the rating from a Plex
    POPM tag first, falling back to other POPM tags if no Plex tag is found. Converts
    the rating to Plex's 1-10 scale.
    """
    try:
        audio = MP3(file_path, ID3=ID3)

        if audio.tags:
            popm_frames = audio.tags.getall("POPM")

            if popm_frames:
                plex_popm = next(
                    (frame for frame in popm_frames if frame.email == "Plex"), None
                )

                if plex_popm:
                    rating = _popm_rating_to_plex(plex_popm.rating, "Plex")
                else:
                    frame = popm_frames[0]
                    rating = _popm_rating_to_plex(frame.rating, frame.email)

                log_debug(f"▸ Successfully read MP3 rating: **{rating}**", 4)

                return rating

        log_debug("▸ No rating found in MP3 file", 4)

        return None
    except Exception as e:
        log_error(f"▪ Failed to read rating from MP3 file: {e}", 4)
        return None


def _set_rating_to_mp3(file_path, plex_rating):
    """
    Write rating to an MP3 file's POPM tag. Creates or updates a Plex POPM tag with the
    provided rating value converted to the appropriate POPM scale.
    """
    try:
        popm_rating = _plex_rating_to_popm(plex_rating)

        log_rating = f"**{plex_rating}** (**{plex_rating / 2}**) ⇒ **{popm_rating}**"

        if is_dry_run():
            log_info(
                f"▸ [dry-run] Would have rated MP3 file: {log_rating}",
                4,
            )
        else:
            audio = MP3(file_path, ID3=ID3)

            if audio.tags is None:
                audio.tags = ID3()

            popm_frames = audio.tags.getall("POPM")
            plex_popm = next(
                (frame for frame in popm_frames if frame.email == "Plex"), None
            )

            if plex_popm:
                plex_popm.rating = popm_rating
                plex_popm.count = 0
            else:
                audio.tags.add(POPM(email="Plex", rating=popm_rating, count=0))

            audio.save()

            log_info(f"▸ Successfully rated MP3 file: {log_rating}", 4)
    except Exception as e:
        log_error(f"▪ Failed to write rating for MP3 file: {e}", 4)


def _get_rating_from_aiff(file_path):
    """
    Read rating from an AIFF file's POPM tag. Attempts to read the rating from a Plex
    POPM tag first, falling back to other POPM tags if no Plex tag is found. Converts
    the rating to Plex's 1-10 scale.
    """
    try:
        audio = AIFF(file_path)

        if audio.tags:
            popm_frames = audio.tags.getall("POPM")

            if popm_frames:
                plex_popm = next(
                    (frame for frame in popm_frames if frame.email == "Plex"), None
                )

                if plex_popm:
                    rating = _popm_rating_to_plex(plex_popm.rating, "Plex")
                else:
                    frame = popm_frames[0]
                    rating = _popm_rating_to_plex(frame.rating, frame.email)

                log_debug(f"▸ Successfully read AIFF rating: **{rating}**", 4)

                return rating

        log_debug("▸ No rating found in AIFF file", 4)

        return None
    except Exception as e:
        log_error(f"▪ Failed to read rating from AIFF file: {e}", 4)
        return None


def _set_rating_to_aiff(file_path, plex_rating):
    """
    Write rating to an AIFF file's POPM tag. Creates or updates a Plex POPM tag with the
    provided rating value converted to the appropriate POPM scale.
    """
    try:
        popm_rating = _plex_rating_to_popm(plex_rating)

        log_rating = f"**{plex_rating}** (**{plex_rating / 2}**) ⇒ **{popm_rating}**"

        if is_dry_run():
            log_info(
                f"▸ [dry-run] Would have rated AIFF file: {log_rating}",
                4,
            )
        else:
            audio = AIFF(file_path)

            if audio.tags is None:
                audio.add_tags()

            popm_frames = audio.tags.getall("POPM")
            plex_popm = next(
                (frame for frame in popm_frames if frame.email == "Plex"), None
            )

            if plex_popm:
                plex_popm.rating = popm_rating
                plex_popm.count = 0
            else:
                audio.tags.add(POPM(email="Plex", rating=popm_rating, count=0))

            audio.save()

            log_info(f"▸ Successfully rated AIFF file: {log_rating}", 4)
    except Exception as e:
        log_error(f"▪ Failed to write rating for AIFF file: {e}", 4)


def _get_rating_from_vorbis(file_path, file_type):
    """
    Read rating from a file using Vorbis Comments (FLAC/OGG/OPUS) RATING tag. Converts
    the rating (10-100 scale) to Plex's 1-10 scale.
    """
    try:
        if file_type == "FLAC":
            audio = FLAC(file_path)
        elif file_type == "OGG":
            audio = OggVorbis(file_path)
        else:  # OPUS
            audio = OggOpus(file_path)

        rating_raw = audio.get("RATING")

        if rating_raw:
            vorbis_rating = int(
                rating_raw[0] if isinstance(rating_raw, list) else rating_raw
            )

            if vorbis_rating == 0:
                rating = None
            else:
                rating = max(1, min(10, round(vorbis_rating / 10)))

            log_debug(f"▸ Successfully read {file_type} rating: **{rating}**", 4)

            return rating

        log_debug(f"▸ No rating found in {file_type} file", 4)

        return None
    except Exception as e:
        log_error(f"▪ Failed to read rating from {file_type} file: {e}", 4)
        return None


def _set_rating_to_vorbis(file_path, plex_rating, file_type):
    """
    Write rating to a file using Vorbis Comments (FLAC/OGG/OPUS) RATING tag.
    Converts the Plex rating (1-10 scale) to Vorbis Comments' 10-100 scale.
    """
    try:
        if plex_rating is None or plex_rating == 0:
            vorbis_rating = "0"
        else:
            vorbis_rating = str(max(10, min(100, plex_rating * 10)))

        log_rating = f"**{plex_rating}** (**{plex_rating / 2}**) ⇒ **{vorbis_rating}**"

        if is_dry_run():
            log_info(
                f"▸ [dry-run] Would have rated {file_type} file: {log_rating}",
                4,
            )
        else:
            if file_type == "FLAC":
                audio = FLAC(file_path)
            elif file_type == "OGG":
                audio = OggVorbis(file_path)
            else:  # OPUS
                audio = OggOpus(file_path)

            audio["RATING"] = vorbis_rating
            audio.save()

            log_info(f"▸ Successfully rated {file_type} file: {log_rating}", 4)
    except Exception as e:
        log_error(f"▪ Failed to write rating for {file_type} file: {e}", 4)


def _get_rating_from_m4a(file_path):
    """
    Read rating from an M4A (AAC/ALAC) file's RATE tag. Converts the rating (10-100
    scale) to Plex's 1-10 scale.
    """
    try:
        audio = MP4(file_path)

        rating_raw = audio.tags.get("rate")

        if rating_raw:
            m4a_rating = int(
                rating_raw[0] if isinstance(rating_raw, list) else rating_raw
            )

            if m4a_rating == 0:
                rating = None
            else:
                rating = max(1, min(10, round(m4a_rating / 10)))

            log_debug(f"▸ Successfully read M4A rating: **{rating}**", 4)
            return rating

        log_debug("▸ No rating found in M4A file", 4)

        return None
    except Exception as e:
        log_error(f"▪ Failed to read rating from M4A file: {e}", 4)
        return None


def _set_rating_to_m4a(file_path, plex_rating):
    """
    Write rating to an M4A (AAC/ALAC) file's RATE tag. Converts the Plex rating (1-10
    scale) to M4A's 10-100 scale.
    """
    try:
        if plex_rating is None or plex_rating == 0:
            m4a_rating = "0"
        else:
            m4a_rating = str(max(10, min(100, plex_rating * 10)))

        log_rating = f"**{plex_rating}** (**{plex_rating / 2}**) ⇒ **{m4a_rating}**"

        if is_dry_run():
            log_info(
                f"▸ [dry-run] Would have rated M4A file: {log_rating}",
                4,
            )
        else:
            audio = MP4(file_path)
            audio["----:com.apple.iTunes:RATE"] = [m4a_rating.encode("utf-8")]
            audio.save()

            log_info(f"▸ Successfully rated M4A file: {log_rating}", 4)
    except Exception as e:
        log_error(f"▪ Failed to write rating for M4A file: {e}", 4)


def get_rating_from_file(file_path):
    """
    Read rating from a music file based on its extension. Returns the rating on the 1-10
    scale used by Plex.
    """
    if file_path.endswith(".mp3"):
        return _get_rating_from_mp3(file_path)

    if file_path.endswith(".m4a"):
        return _get_rating_from_m4a(file_path)

    for ext, file_type in _AIFF_FORMATS.items():
        if file_path.endswith(ext):
            return _get_rating_from_aiff(file_path)

    for ext, file_type in _VORBIS_FORMATS.items():
        if file_path.endswith(ext):
            return _get_rating_from_vorbis(file_path, file_type)

    return None


def set_rating_to_file(file_path, plex_rating):
    """
    Write rating to a music file based on its extension. Converts the Plex rating to the
    appropriate format for the file type.
    """
    if file_path.endswith(".mp3"):
        _set_rating_to_mp3(file_path, plex_rating)

    if file_path.endswith(".m4a"):
        _set_rating_to_m4a(file_path, plex_rating)

    for ext, file_type in _AIFF_FORMATS.items():
        if file_path.endswith(ext):
            _set_rating_to_aiff(file_path, plex_rating)

    for ext, file_type in _VORBIS_FORMATS.items():
        if file_path.endswith(ext):
            _set_rating_to_vorbis(file_path, plex_rating, file_type)


def get_rating_from_plex(plex_item):
    """
    Read rating from a Plex media item. Converts Plex's rating to an integer on the
    1-10 scale.
    """
    try:
        rating_raw = plex_item.userRating

        if rating_raw is None:
            log_debug("▸ No rating found in Plex media", 4)
            return None

        rating = int(float(rating_raw)) if rating_raw is not None else None

        if rating == 0:
            rating = None

        log_debug(f"▸ Successfully read Plex rating: **{rating}**", 4)

        return rating
    except Exception as e:
        log_error(f"▪ Failed to read rating from Plex media: {e}", 4)
        return None


def set_rating_to_plex(plex_item, file_rating):
    """Write rating to a Plex media item using Plex's 1-10 scale."""
    try:
        log_rating = f"**{file_rating}** (**{file_rating / 2}**"

        if is_dry_run():
            log_info(
                f"▸ [dry-run] Would have rated Plex media: {log_rating})",
                4,
            )
        else:
            plex_item.rate(float(file_rating))

            log_info(f"▸ Successfully rated Plex media: {log_rating})", 4)
    except AttributeError as e:
        log_error(f"▪ Failed to write rating for Plex media: {e}", 4)
