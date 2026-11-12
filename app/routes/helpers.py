from functools import wraps

from flask import flash, redirect, request, url_for

from app.services.validation import ValidationError


def handle_validation(endpoint: str):
    """Convert expected domain errors into user feedback, not HTTP 500 errors."""
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            try:
                return view(*args, **kwargs)
            except ValidationError as exc:
                flash(str(exc), "error")
                return redirect(request.referrer or url_for(endpoint))
        return wrapped
    return decorator
