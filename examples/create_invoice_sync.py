"""Exemplu: emiterea unei facturi simple (sincron).

Acest script arată cum se creează și se emite o factură nouă folosind
clasa sincronă :class:`SmartBillClient`. Factura conține un singur produs
cu TVA inclus (cota redusă) și este emisă direct (``is_draft=False``).

Pași:
    1. Se instanțiază clientul cu username-ul și token-ul SmartBill.
    2. Se construiește modelul :class:`Invoice` cu datele clientului și
       lista de produse.
    3. Se apelează ``client.invoices.create(invoice)`` care trimite
       ``POST /invoice`` și returnează seria și numărul documentului.

Notă: câmpurile din modele folosesc ``snake_case`` în Python, dar sunt
serializate automat în ``camelCase`` către API (ex. ``company_vat_code``
devine ``companyVatCode``).
"""

from smartbill_sdk import SmartBillClient
from smartbill_sdk.models import Client, Invoice, Product


def main() -> None:
    # 1. Autentificare (HTTP Basic Auth: username:token).
    client = SmartBillClient(username="you@example.com", token="YOUR_TOKEN")

    # 2. Construirea facturii.
    invoice = Invoice(
        company_vat_code="RO12345678",
        client=Client(
            name="Intelligent IT",
            vat_code="RO12345678",
            address="str. Sperantei, nr. 5",
            city="Sibiu",
            county="Sibiu",
            country="Romania",
            email="office@intelligent.ro",
        ),
        series_name="FCT",
        is_draft=False,
        issue_date="2024-05-01",
        due_date="2024-05-15",
        products=[
            Product(
                name="Produs 1",
                code="ccd1",
                measuring_unit_name="buc",
                currency="RON",
                quantity=2,
                price=10,
                is_tax_included=True,
                tax_name="Redusa",
                tax_percentage=9,
            ),
        ],
    )

    # 3. Emiterea facturii.
    with client:
        resp = client.invoices.create(invoice)
        print(f"Factura emisa: seria {resp.series}, numarul {resp.number}")


if __name__ == "__main__":
    main()
