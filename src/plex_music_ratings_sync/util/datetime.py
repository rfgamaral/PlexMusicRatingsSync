def format_time(time_delta):
    """Format a timedelta into a human readable string."""
    total_seconds = int(time_delta.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    milliseconds = int(time_delta.microseconds / 1000)

    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    elif seconds > 0:
        return f"{seconds}.{milliseconds:03d}s"
    else:
        return f"{milliseconds}ms"
