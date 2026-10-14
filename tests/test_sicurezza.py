"""Il server è locale: le richieste da altri siti aperti nel browser vanno rifiutate."""
from fastapi.testclient import TestClient


def test_rifiuta_le_richieste_che_arrivano_da_un_altro_sito(client: TestClient) -> None:
    r = client.post("/rubrica", json={"nome": "Marco"}, headers={"Origin": "https://sito-malevolo.example"})
    assert r.status_code == 403
    assert client.get("/rubrica").json()["nomi"] == []


def test_accetta_le_richieste_dalla_pagina_dell_app(client: TestClient) -> None:
    for host in ("127.0.0.1:8765", "localhost:8765"):
        intestazioni = {"Host": host, "Origin": f"http://{host}", "Sec-Fetch-Site": "same-origin"}
        r = client.post("/rubrica", json={"nome": "Marco"}, headers=intestazioni)
        assert r.status_code == 200


def test_rifiuta_un_host_diverso_da_localhost(client: TestClient) -> None:
    # DNS rebinding: un dominio esterno che punta a 127.0.0.1
    r = client.get("/rubrica", headers={"Host": "sito-malevolo.example:8765"})
    assert r.status_code == 400


def test_rifiuta_le_richieste_da_un_altra_app_su_localhost(client: TestClient) -> None:
    # Un altro programma locale (es. un server di sviluppo su un'altra porta) non è la pagina dell'app
    r = client.post("/rubrica", json={"nome": "Marco"}, headers={"Origin": "http://localhost:3000"})
    assert r.status_code == 403


def test_rifiuta_le_richieste_che_il_browser_marca_come_provenienti_da_un_altro_sito(client: TestClient) -> None:
    r = client.post("/rubrica", json={"nome": "Marco"}, headers={"Sec-Fetch-Site": "cross-site"})
    assert r.status_code == 403
    assert client.get("/rubrica").json()["nomi"] == []


def test_rifiuta_le_richieste_da_pagine_senza_origine(client: TestClient) -> None:
    # iframe sandbox, file://, data: inviano "Origin: null"
    assert client.post("/rubrica", json={"nome": "Marco"}, headers={"Origin": "null"}).status_code == 403
