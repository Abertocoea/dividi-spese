"""Il server è locale: le richieste da altri siti aperti nel browser vanno rifiutate."""
from fastapi.testclient import TestClient


def test_rifiuta_le_richieste_che_arrivano_da_un_altro_sito(client: TestClient) -> None:
    r = client.post("/rubrica", json={"nome": "Marco"}, headers={"Origin": "https://sito-malevolo.example"})
    assert r.status_code == 403
    assert client.get("/rubrica").json()["nomi"] == []


def test_accetta_le_richieste_dalla_pagina_dell_app(client: TestClient) -> None:
    for origine in ("http://127.0.0.1:8765", "http://localhost:8765"):
        r = client.post("/rubrica", json={"nome": "Marco"}, headers={"Origin": origine})
        assert r.status_code == 200


def test_rifiuta_un_host_diverso_da_localhost(client: TestClient) -> None:
    # DNS rebinding: un dominio esterno che punta a 127.0.0.1
    r = client.get("/rubrica", headers={"Host": "sito-malevolo.example:8765"})
    assert r.status_code == 400
