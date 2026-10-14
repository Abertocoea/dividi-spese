"""Forma dei dati scambiati tra API, estrazione e ripartizione."""
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, PlainSerializer
from typing import Annotated

CENT = Decimal("0.01")
# Differenza sotto la quale due importi sono considerati uguali.
TOLLERANZA = Decimal("0.005")


def _serializza_importo(d: Decimal) -> str:
    """Due decimali; fino a quattro solo se servono (es. prezzo unitario 10,00 € / 3 = 3.3333)."""
    testo = f"{d:.4f}".rstrip("0")
    intero, _, decimali = testo.partition(".")
    return f"{intero}.{decimali.ljust(2, '0')}"


# Importi in euro come Decimal, serializzati come stringa ("12.50") per non perdere precisione nel JSON.
Importo = Annotated[Decimal, PlainSerializer(_serializza_importo, return_type=str)]

TipoCosto = Literal["spedizione", "commissione", "assicurazione", "sconto", "altro"]
Criterio = Literal["proporzionale", "parti_uguali"]


class DatiOrdine(BaseModel):
    numero: str | None = None
    data: str | None = None
    venditore: str | None = None


class Prodotto(BaseModel):
    nome: str
    quantita: int = Field(ge=1)
    dettagli: str = ""
    prezzo_unitario: Importo


class CostoComune(BaseModel):
    descrizione: str
    importo: Importo
    tipo: TipoCosto = "altro"


class TotaliDichiarati(BaseModel):
    subtotale_prodotti: Importo | None = None
    totale: Importo | None = None


class OrdineEstratto(BaseModel):
    valuta: str = "EUR"
    ordine: DatiOrdine = DatiOrdine()
    prodotti: list[Prodotto]
    costi_comuni: list[CostoComune] = []
    totali_dichiarati: TotaliDichiarati = TotaliDichiarati()


class Assegnazione(BaseModel):
    """Unità di una riga prodotto (indice in `prodotti`) assegnate a una persona."""

    riga: int = Field(ge=0)
    persona: str = Field(min_length=1)
    unita: int = Field(ge=1)


class RichiestaCalcolo(BaseModel):
    ordine: OrdineEstratto
    assegnazioni: list[Assegnazione]
    criterio: Criterio = "proporzionale"


class ProdottoAssegnato(BaseModel):
    riga: int
    nome: str
    dettagli: str
    unita: int
    unita_riga: int
    prezzo_unitario: Importo
    totale: Importo


class QuotaPersona(BaseModel):
    nome: str
    prodotti: list[ProdottoAssegnato]
    subtotale: Importo
    quota_costi_comuni: Importo
    totale: Importo


class Ripartizione(BaseModel):
    criterio: Criterio
    persone: list[QuotaPersona]
    subtotale_prodotti: Importo
    costi_comuni: Importo
    totale: Importo
