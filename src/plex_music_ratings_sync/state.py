_state = {"dry_run": False}
"""Global state for the application."""


def is_dry_run():
    """Check if application is running in dry-run mode."""
    return _state["dry_run"]


def set_dry_run(enabled):
    """Enable or disabled the dry-run mode."""
    _state["dry_run"] = enabled
