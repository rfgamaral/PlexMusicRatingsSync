_state = {"dry_run": False, "no_cache": False, "clear_cache": False}
"""Global state for the application."""


def is_dry_run():
    """Check if application is running in dry-run mode."""
    return _state["dry_run"]


def set_dry_run(enabled):
    """Enable or disabled the dry-run mode."""
    _state["dry_run"] = enabled


def is_no_cache():
    """Check if caching is disabled."""
    return _state["no_cache"]


def set_no_cache(enabled):
    """Enable or disable the no-cache mode."""
    _state["no_cache"] = enabled


def is_clear_cache():
    """Check if cache should be cleared."""
    return _state["clear_cache"]


def set_clear_cache(enabled):
    """Enable or disable the clear-cache mode."""
    _state["clear_cache"] = enabled
