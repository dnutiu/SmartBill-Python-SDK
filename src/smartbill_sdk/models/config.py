"""Configuration models: taxes and document series."""

from __future__ import annotations

from typing import List, Optional, Union

from pydantic import Field

from .common import ModelConfig


class Tax(ModelConfig):
    """A VAT rate entry from ``GET /tax``."""

    name: Optional[str] = Field(None, alias="name")
    percentage: Optional[float] = Field(None, alias="percentage")
    # Some tax entries include additional metadata.
    id: Optional[int] = Field(None, alias="id")


class Series(ModelConfig):
    """A document series entry from ``GET /series``."""

    name: Optional[str] = Field(None, alias="name")
    next_number: Optional[Union[str, int]] = Field(None, alias="nextNumber")
    type: Optional[str] = Field(None, alias="type")


class TaxesResponse(ModelConfig):
    """Parsed response of ``GET /tax``."""

    error_text: Optional[str] = Field(None, alias="errorText")
    message: Optional[str] = Field(None, alias="message")
    taxes: List[Tax] = Field(default_factory=list, alias="taxes")


class SeriesListResponse(ModelConfig):
    """Parsed response of ``GET /series``."""

    error_text: Optional[str] = Field(None, alias="errorText")
    message: Optional[str] = Field(None, alias="message")
    list: List[Series] = Field(default_factory=list, alias="list")
