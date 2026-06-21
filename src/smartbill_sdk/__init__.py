"""smartbill-sdk — Python SDK for the SmartBill Cloud REST API.

Provides synchronous (:class:`SmartBillClient`) and asynchronous
(:class:`AsyncSmartBillClient`) clients with typed pydantic models for
every endpoint in the SmartBill OpenAPI specification.
"""

from ._transport import DEFAULT_BASE_URL
from .async_client import AsyncSmartBillClient
from .client import SmartBillClient
from .exceptions import (
    SmartBillAPIError,
    SmartBillAuthError,
    SmartBillError,
    SmartBillRateLimitError,
    SmartBillTransportError,
)
from .models import (
    BaseResponse,
    Client,
    DiscountType,
    DocumentType,
    EmailDocument,
    EmailResponse,
    Estimate,
    FiscalReceiptResponse,
    Invoice,
    InvoiceCreateResponse,
    InvoicePayment,
    InvoiceRef,
    Payment,
    PaymentStatusResponse,
    PaymentType,
    Product,
    ProformaInvoicesResponse,
    Series,
    SeriesListResponse,
    StornoRequest,
    StornoResponse,
    StockList,
    StockProduct,
    StockWarehouse,
    StocksResponse,
    Tax,
    TaxesResponse,
)

__all__ = [
    "AsyncSmartBillClient",
    "BaseResponse",
    "Client",
    "DEFAULT_BASE_URL",
    "DiscountType",
    "DocumentType",
    "EmailDocument",
    "EmailResponse",
    "Estimate",
    "FiscalReceiptResponse",
    "Invoice",
    "InvoiceCreateResponse",
    "InvoicePayment",
    "InvoiceRef",
    "Payment",
    "PaymentStatusResponse",
    "PaymentType",
    "Product",
    "ProformaInvoicesResponse",
    "Series",
    "SeriesListResponse",
    "SmartBillAPIError",
    "SmartBillAuthError",
    "SmartBillClient",
    "SmartBillError",
    "SmartBillRateLimitError",
    "SmartBillTransportError",
    "StockList",
    "StockProduct",
    "StockWarehouse",
    "StocksResponse",
    "StornoRequest",
    "StornoResponse",
    "Tax",
    "TaxesResponse",
]

__version__ = "0.1.0"
