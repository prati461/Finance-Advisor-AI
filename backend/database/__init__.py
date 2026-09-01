from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from backend.core.config import settings
from backend.core.logging import logger


engine_options = {
    "future": True,
    "echo": False,
    "pool_pre_ping": True,
}

if settings.database_url.startswith("mysql+pymysql://"):
    # Railway connections can be dropped while an instance is idle.  Recycle
    # pooled connections before MySQL's server-side timeout and validate them.
    logger.info("Database: Configuring MySQL connection pooling")
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
    logger.info("Database: Using SQLite (development only)")
    # SQLite remains a local-development default only.
    engine_options["connect_args"] = {"check_same_thread": False}

logger.info("Database: Creating engine for URL pattern: %s", settings.database_url[:50])
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
    logger.info("Database: Checking connection...")
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        logger.info("Database: Connection check passed")
    except Exception as e:
        logger.exception("Database: Connection check failed - %s", e)
        raise


def get_db():
    logger.debug("Database: Getting session")
    db = SessionLocal()
    try:
        yield db
    finally:
        logger.debug("Database: Closing session")
        db.close()

