# Architecture Guide

## Clean Architecture and Package Organization

The backend is organized with clear separation between framework interfaces, business logic, persistence, and machine learning.

- `backend/app/` - application factory and runtime entrypoint
- `backend/api/v1/` - versioned API router definitions
- `backend/core/` - configuration, logging, security, and shared exceptions
- `backend/database/` - SQLAlchemy engine setup, session management, migrations
- `backend/domain/` - pure business entities and domain logic boundaries
- `backend/models/` - ORM entities and persistence schemas
- `backend/repositories/` - repository interfaces and data access implementations
- `backend/schemas/` - Pydantic request and response models
- `backend/services/` - application services and business orchestration
- `backend/ml/` - machine learning workflows, data processing, model storage, and inference
  - `data/` - data ingestion and cleaning pipelines
  - `features/` - feature engineering and transformation
  - `models/` - model definitions and wrappers
  - `pipelines/` - reusable training and inference workflows
  - `serialization/` - artifact versioning and storage
  - `stock/`, `real_estate/`, `recommendation/`, `risk/` - domain ML modules
- `backend/utils/` - reusable utilities and helpers
- `backend/tests/` - organized unit and integration tests

## Database Recommendation

The design should use normalized entities and foreign keys for users, income, expenses, budgets, portfolios, predictions, and recommendations.

Use SQLAlchemy ORM for backend portability and environment-driven database configuration.

Future PostgreSQL compatibility is ensured by using a connection URL and ORM abstraction rather than SQLite-specific SQL.

## ML Pipeline Recommendation

Machine learning should be centralized under `backend/ml/` with separate responsibilities for data, features, models, evaluation, and artifact storage.

Recommended dataset mapping:
- Personal finance dataset for risk classification and investment recommendation
- Global market macro dataset for stock forecasting
- House price dataset for real estate regression

## Security and Production Readiness

The architecture is designed to support:
- JWT authentication and token security
- bcrypt password hashing
- environment-driven configuration and secret management
- input validation with Pydantic
- CORS origin control for frontend integration
- clear separations for logging and exception handling

## Roadmap

Phase 0 completed. Phase 1 will implement backend scaffolding, config, and core infrastructure after approval.
