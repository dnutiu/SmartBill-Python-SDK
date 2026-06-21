"""Exemplu: emiterea unui bon fiscal cu încasare mixtă (asincron).

Bonul fiscal se emite tot prin ``POST /payment`` cu ``type='Bon'``. Pe
lângă produsele vândute, se pot specifica sumele încasate pe fiecare
metodă de plată (cash, card, tichete de masă etc.) prin câmpurile
``received_*``. Dacă ``return_fiscal_printer_text=True``, API-ul
returnează textul destinat imprimantei fiscale (în ``message``).

Acest exemplu rulează asincron și arată și o stare de plată a unei
facturi concurent cu emiterea bonului.
"""

import asyncio

from smartbill_sdk import AsyncSmartBillClient
from smartbill_sdk.models import Payment, Product


async def main() -> None:
    async with AsyncSmartBillClient(
        username="you@example.com", token="YOUR_TOKEN",
    ) as client:
        payment = Payment(
            company_vat_code="RO12345678",
            value=260.0,
            type="Bon",
            is_cash=False,
            use_stock=False,
            return_fiscal_printer_text=True,
            products=[
                Product(
                    name="Produs 1",
                    measuring_unit_name="buc",
                    currency="RON",
                    quantity=1,
                    price=200,
                    is_tax_included=True,
                    tax_name="Normala",
                    tax_percentage=19,
                ),
                Product(
                    name="Produs 2",
                    measuring_unit_name="buc",
                    currency="RON",
                    quantity=1,
                    price=60,
                    is_tax_included=True,
                    tax_name="Normala",
                    tax_percentage=19,
                ),
            ],
            received_cash=200.0,
            received_card=60.0,
        )

        # Emite bonul fiscal și, în paralel, verifică starea plății
        # pentru o factură deja existentă.
        receipt_task = client.payments.acreate(payment)
        status_task = client.invoices.apayment_status("RO12345678", "FCT", "0040")
        receipt, status = await asyncio.gather(receipt_task, status_task)

        print(f"Bon fiscal emis: id={receipt.id}")
        print(f"  Text imprimantă fiscală: {receipt.message}")
        print(
            "Stare plată factură: "
            f"total={status.invoice_total_amount}, "
            f"plătit={status.paid_amount}, "
            f"rest={status.unpaid_amount}"
        )


if __name__ == "__main__":
    asyncio.run(main())
