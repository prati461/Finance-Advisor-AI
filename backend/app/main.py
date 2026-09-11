import fastapi
import time
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text

from backend.api import api_router
from backend.core.config import settings
from backend.core.logging import configure_logging, logger
from backend.core.exceptions import AppException
from backend.database import check_database_connection, engine
from backend.models import Base


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        description="AI-Powered Personal Finance & Investment Advisor backend API",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url=f"{settings.api_v1_str}/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.api_v1_str)

    app.state.database_ready = False

    @app.on_event("startup")
    def startup_event() -> None:
        try:
            from sqlalchemy.engine import make_url
            safe_db_url = make_url(settings.database_url).render_as_string(hide_password=True)
        except Exception:
            safe_db_url = "configured"

        logger.info("Application module: backend.app.main")
        logger.info("Environment: %s", settings.environment)
        logger.info("Database URL: %s", safe_db_url)
        logger.info("Debug mode: %s", settings.debug)
        logger.info("Registered routes: %s", sorted(route.path for route in app.routes))
        logger.info("Starting Finance Advisor API")
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            try:
                logger.info("Database init attempt %s/%s", attempt, max_attempts)
                check_database_connection()
                logger.info("Database connection check passed")
                Base.metadata.create_all(bind=engine)
                logger.info("Database schema created")
                _ensure_compatible_schema()
                logger.info("Schema compatibility check passed")
                check_database_connection()
                logger.info("Final database connection check passed")
                app.state.database_ready = True
                logger.info("✓ Database initialized successfully")
                return
            except Exception as e:
                app.state.database_ready = False
                engine.dispose()
                if attempt == max_attempts:
                    logger.warning("Database initialization deferred after %s attempts: %s", max_attempts, e)
                    return
                logger.warning("Database initialization attempt %s/%s failed: %s; retrying in 2s", attempt, max_attempts, e)
                time.sleep(2)

    @app.on_event("shutdown")
    def shutdown_event() -> None:
        logger.info("Shutting down Finance Advisor API")

    @app.exception_handler(AppException)
    def app_exception_handler(request, exc: AppException):
        return fastapi.responses.JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    @app.get("/", include_in_schema=False)
    def root() -> dict:
        return {"service": "finance-advisor-ai", "status": "ok"}

    @app.get("/health", include_in_schema=False)
    def health() -> dict:
        """Deployment health check, available without the API version prefix."""
        if not app.state.database_ready:
            try:
                check_database_connection()
                Base.metadata.create_all(bind=engine)
                _ensure_compatible_schema()
                app.state.database_ready = True
                logger.info("✓ Database initialized successfully via health recovery")
            except Exception:
                raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database is not ready")
        return {"service": "finance-advisor-ai", "status": "ok"}

    @app.get("/__deployment_check", include_in_schema=False)
    def deployment_check() -> dict:
        return {
            "service": "finance-advisor-ai",
            "version": settings.version,
            "routes": sorted(route.path for route in app.routes),
        }

    return app


def _ensure_compatible_schema() -> None:
    """Apply small additive changes for installations without Alembic history."""
    inspector = inspect(engine)
    if not inspector.has_table("users"):
        return
    columns = {column["name"] for column in inspector.get_columns("users")}
    additions = {
        "risk_profile": "VARCHAR(32)",
        "investment_horizon_years": "INTEGER",
    }
    with engine.begin() as connection:
        for name, definition in additions.items():
            if name not in columns:
                connection.execute(text(f"ALTER TABLE users ADD COLUMN {name} {definition}"))

app = create_app()
