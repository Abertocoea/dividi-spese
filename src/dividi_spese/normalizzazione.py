"""Trasforma l'output grezzo del modello in un OrdineEstratto. Il modello copia, il codice calcola."""
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Any, cast, get_args

from .modelli import TOLLERANZA, CostoComune, DatiOrdine, OrdineEstratto, Prodotto, TipoCosto, TotaliDichiarati

# Un prezzo ricavato da totale_riga / quantita può avere più di due decimali (10,00 € / 3).
PRECISIONE_PREZZO = Decimal("0.0001")
VALUTA_PREDEFINITA = "EUR"


def normalizza(grezzo: dict[str, Any]) -> OrdineEstratto:
    totali = _dizionario(grezzo.get("totali_dichiarati"))
    subtotale_dichiarato = _importo(totali.get("subtotale_prodotti"))
    return OrdineEstratto(
        valuta=str(grezzo.get("valuta") or VALUTA_PREDEFINITA),
        ordine=DatiOrdine(**{k: _testo(v) for k, v in _dizionario(grezzo.get("ordine")).items() if k in DatiOrdine.model_fields}),
        prodotti=_prodotti(grezzo.get("prodotti") or [], subtotale_dichiarato),
        costi_comuni=[c for c in map(_costo, grezzo.get("costi_comuni") or []) if c is not None],
        totali_dichiarati=TotaliDichiarati(subtotale_prodotti=subtotale_dichiarato, totale=_importo(totali.get("totale"))),
    )


def _prodotti(righe: list[dict[str, Any]], subtotale_dichiarato: Decimal | None) -> list[Prodotto]:
    quantita = [max(1, int(r.get("quantita") or 1)) for r in righe]
    prezzi = []
    for r, q in zip(righe, quantita):
        unitario, riga = _importo(r.get("prezzo_unitario")), _importo(r.get("totale_riga"))
        prezzi.append(unitario if unitario is not None else (riga / q if riga is not None else Decimal(0)))

    # Il modello a volte copia il totale di riga in prezzo_unitario: se così i conti non tornano
    # ma la somma dei prezzi coincide con il subtotale dichiarato, i prezzi erano totali di riga.
    if subtotale_dichiarato is not None:
        con_quantita = sum(q * p for q, p in zip(quantita, prezzi))
        senza_quantita = sum(prezzi, Decimal(0))
        if abs(con_quantita - subtotale_dichiarato) > TOLLERANZA and abs(senza_quantita - subtotale_dichiarato) <= TOLLERANZA:
            prezzi = [p / q for p, q in zip(prezzi, quantita)]

    return [
        Prodotto(
            nome=str(r.get("nome") or "").strip(),
            quantita=q,
            dettagli=str(r.get("dettagli") or "").strip(),
            prezzo_unitario=p.quantize(PRECISIONE_PREZZO, rounding=ROUND_HALF_UP),
        )
        for r, q, p in zip(righe, quantita, prezzi)
    ]


def _costo(grezzo: dict[str, Any]) -> CostoComune | None:
    importo = _importo(grezzo.get("importo"))
    if importo is None or importo == 0:
        return None
    tipo = grezzo.get("tipo")
    if tipo not in get_args(TipoCosto) or (tipo == "sconto" and importo > 0):
        tipo = "altro"
    tipo = cast(TipoCosto, tipo)
    return CostoComune(descrizione=str(grezzo.get("descrizione") or "").strip(), importo=importo, tipo=tipo)


def _importo(valore: Any) -> Decimal | None:
    if valore is None or valore == "":
        return None
    try:
        return Decimal(str(valore)).quantize(PRECISIONE_PREZZO)
    except InvalidOperation:
        return None


def _dizionario(valore: Any) -> dict[str, Any]:
    return valore if isinstance(valore, dict) else {}


def _testo(valore: Any) -> str | None:
    return str(valore) if valore not in (None, "") else None
