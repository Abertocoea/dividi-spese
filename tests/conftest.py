from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from dividi_spese.app import crea_app
from dividi_spese.estrazione import ContenutoDocumento

FIXTURES = Path(__file__).parent / "fixtures"


class EstrattoreFinto:
    """Sostituisce Ollama: registra cosa riceve e restituisce un output grezzo prefissato."""

    def __init__(self) -> None:
        self.risposta: dict[str, Any] = output_grezzo()
        self.ricevuti: list[ContenutoDocumento] = []
        self.errore: Exception | None = None
        self.installati = ["qwen3.5:9b-q4_K_M", "qwen3.5:4b-q4_K_M"]
        self.modelli_usati: list[str | None] = []
        self.avvisi: list[str] = []

    def estrai(self, contenuto: ContenutoDocumento, modello: str | None) -> tuple[dict[str, Any], list[str]]:
        if self.errore:
            raise self.errore
        self.ricevuti.append(contenuto)
        self.modelli_usati.append(modello)
        return self.risposta, self.avvisi

    def modelli(self) -> list[str]:
        if self.errore:
            raise self.errore
        return self.installati


def output_grezzo(**sovrascritture: Any) -> dict[str, Any]:
    """Output del modello sull'ordine di riferimento ridotto a tre righe."""
    base: dict[str, Any] = {
        "valuta": "EUR",
        "ordine": {"numero": "1000000001", "data": "2026-10-12", "venditore": "Venditore Esempio"},
        "prodotti": [
            {"nome": "Silenzio", "quantita": 1, "dettagli": "IT NM M10", "prezzo_unitario": 6.00, "totale_riga": None},
            {"nome": "Negazione Ostinata", "quantita": 3, "dettagli": "EN NM KTK", "prezzo_unitario": 2.50, "totale_riga": None},
            {"nome": "Laghetto Bollente", "quantita": 2, "dettagli": "EN NM MH2", "prezzo_unitario": 27.00, "totale_riga": None},
        ],
        "costi_comuni": [
            {"descrizione": "Spese di spedizione", "importo": 11.95, "tipo": "spedizione"},
            {"descrizione": "Tasse di servizio TRUST", "importo": 0.85, "tipo": "commissione"},
        ],
        "totali_dichiarati": {"subtotale_prodotti": 67.50, "totale": 80.30},
    }
    base.update(sovrascritture)
    return base


@pytest.fixture
def estrattore() -> EstrattoreFinto:
    return EstrattoreFinto()


@pytest.fixture
def client(estrattore: EstrattoreFinto, tmp_path: Path) -> Iterator[TestClient]:
    with TestClient(crea_app(estrattore=estrattore, cartella_dati=tmp_path)) as c:
        yield c


@pytest.fixture
def nuovo_client(estrattore: EstrattoreFinto, tmp_path: Path) -> Callable[[], TestClient]:
    """Crea un'altra istanza dell'app sulla stessa cartella dati (simula un riavvio)."""
    return lambda: TestClient(crea_app(estrattore=estrattore, cartella_dati=tmp_path))


__all__ = ["EstrattoreFinto", "output_grezzo", "FIXTURES"]
