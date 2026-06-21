"""Exemplu: listarea seriilor de documente (sincron).

Endpoint: ``GET /series``. Returnează seriile (și următorul număr
liber) pentru documentele din cont. Parametrul opțional ``type`` filtrează
după tipul documentului:

    * ``f`` — facturi
    * ``c`` — chitanțe
    * ``p`` — proforme
    * ``i`` — bonuri fiscale
    * ``n`` — avize

Dacă ``type`` nu este dat, se returnează toate seriile.
"""

from smartbill_sdk import SmartBillClient


def main() -> None:
    with SmartBillClient(username="you@example.com", token="YOUR_TOKEN") as client:
        # Doar seriile de facturi.
        facturi = client.series.series("RO12345678", type="f")
        print("Serii facturi:")
        for s in facturi.list:
            print(f"  - {s.name}: următorul număr {s.next_number}")

        # Toate seriile (fără filtru).
        toate = client.series.series("RO12345678")
        print(f"Total serii (orice tip): {len(toate.list)}")


if __name__ == "__main__":
    main()
