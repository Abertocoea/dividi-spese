"""Numeri e importi in formato italiano (1.234,56)."""
from decimal import ROUND_HALF_UP, Decimal


def numero_italiano(valore: Decimal, decimali: int = 2, migliaia: bool = True) -> str:
    arrotondato = valore.quantize(Decimal(1).scaleb(-decimali), rounding=ROUND_HALF_UP)
    testo = f"{arrotondato:{',' if migliaia else ''}.{decimali}f}"
    return testo.replace(",", "\0").replace(".", ",").replace("\0", ".")


def euro(importo: Decimal) -> str:
    return f"{numero_italiano(importo)} €"
