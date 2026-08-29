from pydantic import ConfigDict, field_validator, model_validator
from pydantic_settings import BaseSettings
from sqlalchemy.engine import make_url


class Settings(BaseSettings):
    app_name: str = "Finance Advisor API"
    api_v1_str: str = "/api/v1"
    version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False
    database_url: str = "sqlite:///./finance_advisor.db"
    jwt_secret_key: str = "CHANGE_ME_CHANGE_ME"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_minutes: int = 60 * 24 * 7
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:3000"
    model_storage_path: str = "./datasets/trained_models"
    datasets_raw_path: str = "./datasets/raw"
    datasets_processed_path: str = "./datasets/processed"

    # --- AI / LLM ---
    gemini_api_key: str = ""
    openai_api_key: str = ""
    llm_provider: str = "gemini"  # "gemini" | "openai" | "none"
    llm_model: str = "gemini-1.5-flash"
    openai_model: str = "gpt-4o-mini"

    # --- Market Data ---
    alpha_vantage_api_key: str = ""
    market_data_cache_path: str = "./datasets/market_cache"
    market_lookback_years: int = 5
    enable_live_market_data: bool = True

    # --- Redis (optional) ---
    redis_url: str = ""

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, value):
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"release", "production", "prod", "false", "0", "no", "off"}:
                return False
            if normalized in {"development", "dev", "true", "1", "yes", "on"}:
                return True
        return value

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        """Accept SQLAlchemy URLs and select PyMySQL for MySQL connections."""
        value = value.strip()
        if value.startswith("mysql://"):
            value = f"mysql+pymysql://{value.removeprefix('mysql://')}"

        try:
            url = make_url(value)
        except Exception as exc:
            raise ValueError(
                "DATABASE_URL must be a valid SQLAlchemy URL. URL-encode special "
                "characters in the username and password (for example @ as %40)."
            ) from exc

        if url.drivername.startswith("mysql") and url.drivername != "mysql+pymysql":
            raise ValueError("MySQL DATABASE_URL must use the mysql+pymysql driver.")
        if not (url.drivername.startswith("mysql") or url.drivername.startswith("sqlite")):
            raise ValueError("DATABASE_URL must use MySQL (mysql+pymysql) or local SQLite.")
        return value

    @model_validator(mode="after")
    def prevent_sqlite_in_production(self):
        if self.environment.strip().lower() in {"production", "prod"} and self.database_url.startswith("sqlite"):
            raise ValueError("SQLite is not allowed when ENVIRONMENT is production; configure Railway MySQL DATABASE_URL.")
        return self

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()

