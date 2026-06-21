"""Exemplu: stornare, anulare, restaurare factură și descărcare PDF (sincron).

Acest exemplu ilustrează operațiile secundare pe facturi:

    * ``client.invoices.reverse(StornoRequest)`` — emite o factură
      storno pentru o factură existentă (``POST /invoice/reverse``).
      Răspunsul conține URL-urile documentului storno.
    * ``client.invoices.cancel(cif, series, number)`` — anulează
      factură (``PUT /invoice/cancel``).
    * ``client.invoices.restore(cif, series, number)`` — restaurează
      o factură anulată (``PUT /invoice/restore``).
    * ``client.invoices.pdf(cif, series, number)`` — descarcă PDF-ul
      brut al facturii (``GET /invoice/pdf``) ca ``bytes``.
"""

from smartbill_sdk import SmartBillClient
from smartbill_sdk.models import StornoRequest


def main() -> None:
    with SmartBillClient(username="you@example.com", token="YOUR_TOKEN") as client:
        cif = "RO12345678"
        series = "FCT"
        number = "0040"

        # 1. Stornare.
        storno = StornoRequest(
            company_vat_code=cif, series_name=series, number=number,
        )
        st = client.invoices.reverse(storno)
        print(f"Factură storno: {st.series} {st.number}")
        print(f"  Document URL: {st.document_url}")

        # 2. Anulare factură originală.
        client.invoices.cancel(cif, series, number)
        print("Factura a fost anulată.")

        # 3. Restaurare factură (se poate face ulterior).
        client.invoices.restore(cif, series, number)
        print("Factura a fost restaurată.")

        # 4. Descărcare PDF.
        pdf_bytes = client.invoices.pdf(cif, series, number)
        with open("factura.pdf", "wb") as f:
            f.write(pdf_bytes)
        print(f"PDF salvat ({len(pdf_bytes)} bytes).")


if __name__ == "__main__":
    main()
