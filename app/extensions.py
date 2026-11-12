from flask import current_app
from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, scoped_session, sessionmaker


class Base(DeclarativeBase):
    pass


class Database:
    """Small SQLAlchemy integration, kept independent of Flask extensions."""

    engine = None
    session = scoped_session(sessionmaker(expire_on_commit=False))

    def init_app(self, app):
        self.engine = create_engine(
            app.config["DATABASE_URL"],
            echo=app.config["SQL_ECHO"],
            connect_args={"check_same_thread": False} if app.config["DATABASE_URL"].startswith("sqlite") else {},
        )
        if app.config["DATABASE_URL"].startswith("sqlite"):
            event.listen(self.engine, "connect", self._enable_sqlite_foreign_keys)
        self.session.configure(bind=self.engine)
        app.teardown_appcontext(lambda _exception: self.session.remove())

    @staticmethod
    def _enable_sqlite_foreign_keys(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    def create_all(self):
        Base.metadata.create_all(self.engine)


db = Database()
