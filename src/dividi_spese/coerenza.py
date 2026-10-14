"""Confronto tra i dati (estratti o corretti a mano) e i totali dichiarati nel documento."""
from decimal import Decimal

from pydantic import BaseModel

from .modelli import TOLLERANZA, Importo, OrdineEstratto


class Coerenza(BaseModel):
    """`ok` è None quando il documento non dichiara né subtotale né totale."""

    ok: bool | None
    subtotale_calcolato: Importo
    subtotale_dichiarato: Importo | None
    differenza_subtotale: Importo | None
    totale_calcolato: Importo
    totale_dichiarato: Importo | None
    differenza_totale: Importo | None


def verifica(ordine: OrdineEstratto) -> Coerenza:
    subtotale = sum((p.quantita * p.prezzo_unitario for p in ordine.prodotti), Decimal(0))
    totale = subtotale + sum((c.importo for c in ordine.costi_comuni), Decimal(0))
    dichiarati = ordine.totali_dichiarati
    diff_sub = subtotale - dichiarati.subtotale_prodotti if dichiarati.subtotale_prodotti is not None else None
    diff_tot = totale - dichiarati.totale if dichiarati.totale is not None else None
    differenze = [d for d in (diff_sub, diff_tot) if d is not None]
    return Coerenza(
        ok=all(abs(d) <= TOLLERANZA for d in differenze) if differenze else None,
        subtotale_calcolato=subtotale,
        subtotale_dichiarato=dichiarati.subtotale_prodotti,
        differenza_subtotale=diff_sub,
        totale_calcolato=totale,
        totale_dichiarato=dichiarati.totale,
        differenza_totale=diff_tot,
    )
