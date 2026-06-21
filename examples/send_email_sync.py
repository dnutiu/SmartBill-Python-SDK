"""Exemplu: trimiterea pe e-mail a unui document (sincron).

Endpoint: ``POST /document/send``. Modelul :class:`EmailDocument`
identifică documentul prin serie + număr + tip (``factura`` sau
``proforma``) și permite specificarea destinatarilor (``to``, ``cc``,
``bcc``) și a conținutului.

Important: câmpurile ``subject`` și ``body_text`` trebuie să fie
**codificate Base64** de către apelant, conform cerințelor API-ului
SmartBill. Mai jos este un helper care face codificarea.
"""

import base64

from smartbill_sdk import SmartBillClient
from smartbill_sdk.models import DocumentType, EmailDocument


def b64(text: str) -> str:
    """Codifică un text în Base64 (necesar pentru subject/bodyText)."""
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


def main() -> None:
    with SmartBillClient(username="you@example.com", token="YOUR_TOKEN") as client:
        email = EmailDocument(
            company_vat_code="RO12345678",
            series_name="FCT",
            number="0040",
            type=DocumentType.INVOICE,
            to="client@example.ro",
            cc="contabilitate@example.ro",
            subject=b64("Factura FCT0040"),
            body_text=b64("Vă trimitemFactura FCT0040. Mulțumim!"),
        )

        resp = client.email.send(email)
        # ``status.code`` este "0" la succes.
        print(f"Status cod: {resp.status.code}, mesaj: {resp.status.message}")


if __name__ == "__main__":
    main()
