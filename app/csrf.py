"""Session-bound CSRF protection without an additional form dependency."""
import secrets
from functools import wraps
from hmac import compare_digest

from flask import abort, current_app, request, session


def csrf_token() -> str:
    token = session.get("csrf_token")
    if token is None:
        token = secrets.token_urlsafe(32)
        session["csrf_token"] = token
    return token


def require_csrf(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if current_app.config["CSRF_ENABLED"]:
            submitted = request.form.get("_csrf_token", "")
            if not compare_digest(submitted, csrf_token()):
                abort(400, "Token CSRF inválido o ausente.")
        return view(*args, **kwargs)
    return wrapped


def init_csrf(app):
    app.jinja_env.globals["csrf_token"] = csrf_token
