"""Exemplu: emiterea unei proforme (sincron).

Proforma se creează cu :class:`Estimate` și se trimite prin
``client.estimates.create(estimate)`` (``POST /estimate``). Structura
este foarte asemănătoare cu o factură: client, serie, produse.

Documentul poate fi convertit ulterior în factură; starea conversiei se
verifică cu ``client.estimates.invoices_status(...)``.
"""

from smartbill_sdk import SmartBillClient
from smartbill_sdk.models import Client, Estimate, Product


def main() -> None:
    with SmartBillClient(username="you@example.com", token="YOUR_TOKEN") as client:
        estimate = Estimate(
            company_vat_code="RO12345678",
            client=Client(name="Intelligent IT", vat_code="RO12345678",
                          email="office@intelligent.ro"),
            series_name="PFC",
            is_draft=False,
            products=[
                Product(
                    name="Serviciu dezvoltare",
                    measuring_unit_name="ore",
                    currency="RON",
                    quantity=10,
                    price=150,
                    is_tax_included=False,
                    tax_name="Normala",
                    tax_percentage=19,
                ),
            ],
        )

        resp = client.estimates.create(estimate)
        print(f"Proforma emisa: seria {resp.series}, numarul {resp.number}")

        # Verificăm dacă proforma a fost deja convertită în factură.
        status = client.estimates.invoices_status(
            "RO12345678", resp.series, resp.number,
        )
        if status.are_invoices_created:
            for inv in status.invoices:
                print(f"  Factura generată: {inv.series_name} {inv.number}")
        else:
            print("  Proforma nu a fost încă convertită în factură.")


if __name__ == "__main__":
    main()
