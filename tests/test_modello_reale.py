"""Estrazione reale con Ollama. Lento: si esegue con `pytest -m lento`.

I file CSV/Excel di esempio sono nel repository. PDF e screenshot dell'ordine reale contengono dati
personali e restano fuori da git: metti `ordine.pdf` e/o `ordine.png` nella cartella indicata da
DIVIDI_SPESE_ESEMPI. Il modello si sceglie con DIVIDI_SPESE_MODELLO (predefinito: quello dell'app).
"""
import json
import os
from collections.abc import Iterator
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

from conftest import FIXTURES, URL_APP
from dividi_spese.app import crea_app
from dividi_spese.ollama import EstrattoreOllama

pytestmark = pytest.mark.lento
ATTESO = json.loads((FIXTURES / "ordine_atteso.json").read_text())
ESEMPI = Path(os.environ.get("DIVIDI_SPESE_ESEMPI", "/nonesiste"))


def documenti() -> list[Path]:
    privati = [ESEMPI / n for n in ("ordine.pdf", "ordine.png") if (ESEMPI / n).exists()]
    return [*privati, FIXTURES / "ordine_it.csv", FIXTURES / "ordine_en.csv", FIXTURES / "ordine.xlsx"]


@pytest.fixture(scope="module")
def client(tmp_path_factory: pytest.TempPathFactory) -> Iterator[TestClient]:
    try:
        httpx.get("http://localhost:11434/api/version", timeout=2)
    except httpx.HTTPError:
        pytest.skip("Ollama non è avviato")
    with TestClient(crea_app(EstrattoreOllama(), tmp_path_factory.mktemp("dati")), base_url=URL_APP) as c:
        yield c


@pytest.mark.parametrize("documento", documenti(), ids=lambda p: p.name)
def test_estrae_l_ordine_di_riferimento(client: TestClient, documento: Path) -> None:
    modello = os.environ.get("DIVIDI_SPESE_MODELLO")
    r = client.post("/estrai", files={"file": (documento.name, documento.read_bytes())}, data={"modello": modello} if modello else {})
    assert r.status_code == 200, r.text
    ordine, coerenza = r.json()["ordine"], r.json()["coerenza"]
    assert len(ordine["prodotti"]) == ATTESO["righe"]
    assert sum(p["quantita"] for p in ordine["prodotti"]) == ATTESO["unita"]
    assert float(coerenza["subtotale_calcolato"]) == ATTESO["subtotale_prodotti"]
    assert sorted(float(c["importo"]) for c in ordine["costi_comuni"]) == sorted(ATTESO["costi_comuni"])
    assert float(coerenza["totale_calcolato"]) == ATTESO["totale"]
    assert coerenza["ok"] is True
