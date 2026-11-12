import pytest

from app import create_app
from app.extensions import Base, db


@pytest.fixture()
def app(tmp_path):
    database = (tmp_path / "test.sqlite3").as_posix()
    application = create_app({
        "TESTING": True,
        "CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret",
        "DATABASE_URL": f"sqlite:///{database}",
    })
    with application.app_context():
        yield application
        db.session.remove()
        Base.metadata.drop_all(db.engine)


@pytest.fixture()
def client(app):
    return app.test_client()
