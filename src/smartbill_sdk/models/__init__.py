"""Pydantic models for SmartBill API requests and responses.

All models use snake_case Python attributes aliased to the camelCase JSON
field names used by the SmartBill API (e.g. ``company_vat_code`` ↔
``companyVatCode``). Models are permissive (``extra="allow"``) so that
new API fields don't break parsing.
"""

from .common import (
    Client,
    DiscountType,
    DocumentType,
    InvoiceRef,
    PaymentType,
    Product,
)
from .invoices import Invoice, InvoicePayment, StornoRequest
from .estimates import Estimate
from .payments import Payment
from .email import EmailDocument
from .config import Series, Tax, SeriesListResponse, TaxesResponse
from .stocks import StockList, StockProduct, StockWarehouse, StocksResponse
from .responses import (
    BaseResponse,
    EmailResponse,
    FiscalReceiptResponse,
    InvoiceCreateResponse,
    PaymentStatusResponse,
    ProformaInvoicesResponse,
    StornoResponse,
)

__all__ = [
    "BaseResponse",
    "Client",
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
    "StornoRequest",
    "StornoResponse",
    "StockList",
    "StockProduct",
    "StockWarehouse",
    "StocksResponse",
    "Tax",
    "TaxesResponse",
]
