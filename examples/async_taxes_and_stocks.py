"""Exemplu: listarea taxelor (TVA) și a stocurilor (asincron).

Acest script folosește clientul asincron :class:`AsyncSmartBillClient`
pentru a executa, concurent, două operații de tip GET:

    * ``GET /tax`` — returnează lista cotelor de TVA configurate în
      contul SmartBill (``client.taxes.ataxes(cif)``).
    * ``GET /stocks`` — returnează valoarea stocului la o dată dată,
      opțional filtrată după gestiune / produs (``client.stocks.aget(...)``).

Avantajul variantei asincrone: mai multe request-uri către SmartBill pot
rula în paralel într-un singur event loop, fără să blocheze firul
principal. Rețineți prefixul ``a`` pentru metodele asincrone
(``ataxes``, ``aget``, ``acreate`` etc.).
"""

import asyncio

from smartbill_sdk import AsyncSmartBillClient


async def main() -> None:
    client = AsyncSmartBillClient(username="you@example.com", token="YOUR_TOKEN")
    async with client:
        # Rulează cele două request-uri concurent.
        taxes_task = client.taxes.ataxes("RO12345678")
        stocks_task = client.stocks.aget(
            "RO12345678",
            "2024-05-01",
            warehouse_name="Depozit",
        )
        taxes, stocks = await asyncio.gather(taxes_task, stocks_task)

        print("Cote TVA:")
        for t in taxes.taxes:
            print(f"  - {t.name}: {t.percentage}%")

        print("Stocuri:")
        for group in stocks.list:
            wh = group.warehouse
            print(f"  Gestiune: {wh.warehouse_name} ({wh.warehouse_type})")
            for p in group.products:
                print(f"    - {p.product_name} [{p.product_code}]: "
                      f"{p.quantity} {p.measuring_unit}")


if __name__ == "__main__":
    asyncio.run(main())
