from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from backend.core.config import settings


engine_options = {
    "future": True,
    "echo": False,
    "pool_pre_ping": True,
}

if settings.database_url.startswith("mysql+pymysql://"):
    # Railway connections can be dropped while an instance is idle.  Recycle
    # pooled connections before MySQL's server-side timeout and validate them.
    engine_options.update(
        pool_recycle=300,
        pool_timeout=30,
        connect_args={
            "charset": "utf8mb4",
            "connect_timeout": 20,
            "read_timeout": 30,
            "write_timeout": 30,
        },
    )
elif settings.database_url.startswith("sqlite"):
    # SQLite remains a local-development default only.
    engine_options["connect_args"] = {"check_same_thread": False}

engine = create_engine(settings.database_url, **engine_options)
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    class_=Session,
)
Base = declarative_base()


def check_database_connection() -> None:
    """Raise if the configured database cannot execute a minimal query."""
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

