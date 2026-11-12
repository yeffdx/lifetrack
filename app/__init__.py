"""LifeTrack application factory."""
import flask

from .config import Config
from .csrf import init_csrf
from .extensions import db


def create_app(config_override: dict | None = None) -> flask.Flask:
    app = flask.Flask(__name__)
    app.config.from_object(Config)
    if config_override:
        app.config.update(config_override)

    db.init_app(app)
    init_csrf(app)

    from .routes.main import main_bp
    from .routes.tasks import tasks_bp
    from .routes.habits import habits_bp
    from .routes.goals import goals_bp
    from .routes.analysis import analysis_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(tasks_bp, url_prefix="/tasks")
    app.register_blueprint(habits_bp, url_prefix="/habits")
    app.register_blueprint(goals_bp, url_prefix="/goals")
    app.register_blueprint(analysis_bp, url_prefix="/analysis")

    with app.app_context():
        db.create_all()

    return app
