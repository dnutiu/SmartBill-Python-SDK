"""Stock (gestiuni) models."""

from __future__ import annotations

from typing import List, Optional

from pydantic import Field

from .common import ModelConfig


class StockProduct(ModelConfig):
    """A product entry within a stock list."""

    measuring_unit: Optional[str] = Field(None, alias="measuringUnit")
    product_code: Optional[str] = Field(None, alias="productCode")
    product_name: Optional[str] = Field(None, alias="productName")
    quantity: Optional[float] = Field(None, alias="quantity")


class StockWarehouse(ModelConfig):
    """Warehouse details attached to a stock list entry."""

    warehouse_name: Optional[str] = Field(None, alias="warehouseName")
    warehouse_type: Optional[str] = Field(None, alias="warehouseType")


class StockList(ModelConfig):
    """A ``list`` entry under the stocks response — products + warehouse."""

    products: List[StockProduct] = Field(default_factory=list, alias="products")
    warehouse: Optional[StockWarehouse] = Field(None, alias="warehouse")


class StocksResponse(ModelConfig):
    """Parsed response of ``GET /stocks``."""

    error_text: Optional[str] = Field(None, alias="errorText")
    message: Optional[str] = Field(None, alias="message")
    list: List[StockList] = Field(default_factory=list, alias="list")
