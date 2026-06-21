"""Exemplu: înregistrarea unei încasări pe o factură (sincron).

Aici se emite o încasare de tip „Chitanta” care este legată de o
factură existentă prin ``invoices_list`` (perechi serie + număr).

Endpoint: ``POST /payment``. Modelul :class:`Payment` acoperă toate
tipurile de încasări (chitanță, bon, card, ordin de plată etc.) prin
câmpul ``type``. Câmpurile care nu se aplică tipului ales se lasă
``None``.

Pentru ștergerea unei încasări „Alta incasare”/„Card”/... (care nu e
chitanță) se folosește ``client.payments.delete_other(...)`` (endpoint-ul
``DELETE /payment/v2``), iar pentru chitanțe
``client.payments.delete_chitanta(...)`` (``DELETE /payment/chitanta``).
"""

from smartbill_sdk import SmartBillClient
from smartbill_sdk.models import Client, InvoiceRef, Payment, PaymentType


def main() -> None:
    with SmartBillClient(username="you@example.com", token="YOUR_TOKEN") as client:
        payment = Payment(
            company_vat_code="RO12345678",
            client=Client(name="Intelligent IT", vat_code="RO12345678"),
            value=62.0,
            type=PaymentType.CHITANTA,
            is_cash=True,
            invoices_list=[
                InvoiceRef(series_name="FCT", number="0040"),
            ],
        )

        resp = client.payments.create(payment)
        print(f"Încasare înregistrată: seria {resp.series}, numărul {resp.number}")

        # Ștergere chitanță (dacă ulterior se anulează).
        # client.payments.delete_chitanta("RO12345678", resp.series, resp.number)


if __name__ == "__main__":
    main()
