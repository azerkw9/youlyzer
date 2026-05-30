from django import template

register = template.Library()


@register.filter
def format_number(value):
    """Format a number with commas."""
    if value is None:
        return 'N/A'
    try:
        return f'{int(value):,}'
    except (ValueError, TypeError):
        return str(value)


@register.filter
def format_duration_seconds(seconds):
    """Format seconds into a human-readable duration string."""
    if seconds is None:
        return 'N/A'
    try:
        seconds = int(seconds)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        if hours > 0:
            return f'{hours}h {minutes}m {secs}s'
        elif minutes > 0:
            return f'{minutes}m {secs}s'
        else:
            return f'{secs}s'
    except (ValueError, TypeError):
        return str(seconds)


@register.filter
def truncate_text(value, length=150):
    """Truncate text to specified length."""
    if not value:
        return ''
    if len(value) <= length:
        return value
    return value[:length].rsplit(' ', 1)[0] + '...'
