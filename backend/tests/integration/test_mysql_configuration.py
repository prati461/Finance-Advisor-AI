"""Database URL validation and MySQL schema-creation coverage.

Set MYSQL_TEST_DATABASE_URL to run the optional live-database test.  This is
intended for a disposable MySQL database (for example docker-compose's db
service), never a shared production database.
"""

import os

import pytest
from sqlalchemy import create_engine, inspect

from backend.core.settings import Settings
from backend.models import Base


def test_mysql_url_uses_pymysql_and_encodes_password() -> None:
    settings = Settings(
        environment="production",
        database_url="mysql+pymysql://finance:p%40ss%3Aword@db.example:3306/finance_advisor",
    )
    assert settings.database_url.startswith("mysql+pymysql://")


def test_mysql_scheme_is_normalized_to_pymysql() -> None:
    settings = Settings(database_url="mysql://finance:password@db.example:3306/finance_advisor")
    assert settings.database_url.startswith("mysql+pymysql://")


def test_production_rejects_sqlite() -> None:
    with pytest.raises(ValueError, match="SQLite is not allowed"):
        Settings(environment="production", database_url="sqlite:///./finance_advisor.db")


@pytest.mark.skipif(not os.getenv("MYSQL_TEST_DATABASE_URL"), reason="MYSQL_TEST_DATABASE_URL is not configured")
def test_mysql_creates_application_schema() -> None:
    engine = create_engine(os.environ["MYSQL_TEST_DATABASE_URL"], pool_pre_ping=True)
    try:
        Base.metadata.create_all(engine)
        assert {"users", "incomes", "expenses", "budgets", "advisor_records", "ai_conversations"}.issubset(
            inspect(engine).get_table_names()
        )
    finally:
        engine.dispose()
