import fastapi
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text

from backend.api import api_router
from backend.core.config import settings
from backend.core.logging import configure_logging, logger
from backend.core.exceptions import AppException
from backend.database import engine
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
        logger.info("Starting Finance Advisor API")
        try:
            Base.metadata.create_all(bind=engine)
            _ensure_compatible_schema()
            app.state.database_ready = True
        except Exception:
            logger.exception("Database initialization failed")
            if settings.environment.strip().lower() in {"production", "prod"}:
                raise

    @app.on_event("shutdown")
    def shutdown_event() -> None:
        logger.info("Shutting down Finance Advisor API")

    @app.exception_handler(AppException)
    def app_exception_handler(request, exc: AppException):
        return fastapi.responses.JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    return app


def _ensure_compatible_schema() -> None:
    """Apply small additive changes for installations without Alembic history."""
    columns = {column["name"] for column in inspect(engine).get_columns("users")}
    additions = {
        "risk_profile": "VARCHAR(32)",
        "investment_horizon_years": "INTEGER",
    }
    with engine.begin() as connection:
        for name, definition in additions.items():
            if name not in columns:
                connection.execute(text(f"ALTER TABLE users ADD COLUMN {name} {definition}"))

app = create_app()


@app.get("/health", include_in_schema=False)
def health() -> dict:
    """Deployment health check, available without the API version prefix."""
    if not app.state.database_ready:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database is not ready")
    return {"status": "ok"}
