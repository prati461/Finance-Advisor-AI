from sqlalchemy import create_engine
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
    engine_options.update(pool_recycle=280, connect_args={"charset": "utf8mb4"})
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


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

