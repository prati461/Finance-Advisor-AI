"""
Dataset Configuration Module

Provides a reusable DatasetConfig class for managing dataset paths
and loading configurations through environment variables.
"""

from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from backend.core.config import settings


class DatasetInfo(BaseModel):
    """Metadata for a single dataset."""

    name: str
    description: str
    relative_path: str
    file_pattern: str
    expected_columns: Optional[List[str]] = None

    model_config = ConfigDict(frozen=True)


class DatasetConfig(BaseModel):
    """
    Centralized dataset configuration.

    Supports loading dataset paths through environment variables.
    Never hardcodes paths inside business logic.
    """

    raw_path: Path = Field(default_factory=lambda: Path(settings.datasets_raw_path))
    processed_path: Path = Field(default_factory=lambda: Path(settings.datasets_processed_path))
    trained_models_path: Path = Field(default_factory=lambda: Path(settings.model_storage_path))
    external_path: Path = Field(default_factory=lambda: Path("./datasets/external"))

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def available_datasets(self) -> Dict[str, DatasetInfo]:
        """Return metadata for all known datasets."""
        return {
            "personal_finance": DatasetInfo(
                name="Synthetic Personal Finance",
                description="User financial profiles for risk scoring and investment recommendation",
                relative_path="raw/synthetic_personal_finance_dataset.csv",
                file_pattern="*.csv",
                expected_columns=[
                    "Age", "Income", "Expenses", "Savings", "Risk_Score",
                ],
            ),
            "stock_market": DatasetInfo(
                name="Global India Markets Macro",
                description="Daily market and commodity indicators for time-series forecasting",
                relative_path="raw/daily_market_data.csv",
                file_pattern="*.csv",
                expected_columns=[
                    "Date", "Open", "High", "Low", "Close", "Volume",
                ],
            ),
            "real_estate": DatasetInfo(
                name="House Price India",
                description="Housing attributes and price target for real estate value prediction",
                relative_path="raw/House Price India.csv",
                file_pattern="*.csv",
                expected_columns=[
                    "Price", "Area", "Bedrooms", "Bathrooms", "Location",
                ],
            ),
        }

    def get_raw_path(self, dataset_name: str) -> Optional[Path]:
        """Get the full path to a raw dataset file."""
        info = self.available_datasets.get(dataset_name)
        if not info:
            return None
        return self.raw_path / info.relative_path

    def get_processed_path(self, dataset_name: str) -> Optional[Path]:
        """Get the full path to a processed dataset file."""
        info = self.available_datasets.get(dataset_name)
        if not info:
            return None
        stem = Path(info.relative_path).stem
        return self.processed_path / f"{stem}_processed.csv"

    def ensure_directories(self) -> None:
        """Create all dataset directories if they don't exist."""
        for path in [self.raw_path, self.processed_path, self.trained_models_path, self.external_path]:
            path.mkdir(parents=True, exist_ok=True)

    def list_raw_datasets(self) -> List[str]:
        """List available raw dataset names that exist on disk."""
        available = []
        for name, info in self.available_datasets.items():
            full_path = self.get_raw_path(name)
            if full_path and full_path.exists():
                available.append(name)
        return available


# Singleton instance
dataset_config = DatasetConfig()
