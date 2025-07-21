#!/usr/bin/env python

# --- UTF-8 shim ---
import sys, io
# On Windows, re-wrap stdout/stderr as UTF-8 with replacement errors
if sys.platform.startswith("win"):
    try:
        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer,
            encoding="utf-8",
            errors="replace",
            line_buffering=True,
        )
        sys.stderr = io.TextIOWrapper(
            sys.stderr.buffer,
            encoding="utf-8",
            errors="replace",
            line_buffering=True,
        )
    except Exception:
        pass

import logging
logging.raiseExceptions = False     # disable the “Logging error” traceback
# --- end of UTF-8 shim ---

import click

from plex_music_ratings_sync.cli import cli


def main():
    """Entry point for the binary."""
    cli()


if __name__ == "__main__":
    main()
