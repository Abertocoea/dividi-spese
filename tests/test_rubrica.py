from collections.abc import Callable

from fastapi.testclient import TestClient


def nomi(client: TestClient) -> list[str]:
    return list(client.get("/rubrica").json()["nomi"])


def test_la_rubrica_parte_vuota(client: TestClient) -> None:
    assert nomi(client) == []


def test_aggiungere_un_nome_lo_mette_in_rubrica_in_ordine_alfabetico(client: TestClient) -> None:
    client.post("/rubrica", json={"nome": "Marco"})
    client.post("/rubrica", json={"nome": "anna"})
    assert nomi(client) == ["anna", "Marco"]


def test_un_nome_gia_presente_non_viene_duplicato(client: TestClient) -> None:
    client.post("/rubrica", json={"nome": "Marco"})
    r = client.post("/rubrica", json={"nome": "  Marco "})
    assert r.status_code == 200
    assert nomi(client) == ["Marco"]


def test_un_nome_vuoto_viene_rifiutato(client: TestClient) -> None:
    assert client.post("/rubrica", json={"nome": "   "}).status_code == 422


def test_rinominare_un_nome(client: TestClient) -> None:
    client.post("/rubrica", json={"nome": "Marco"})
    r = client.put("/rubrica/Marco", json={"nome": "Marco R."})
    assert r.status_code == 200
    assert nomi(client) == ["Marco R."]


def test_rinominare_un_nome_inesistente_da_errore(client: TestClient) -> None:
    assert client.put("/rubrica/Nessuno", json={"nome": "X"}).status_code == 404


def test_eliminare_un_nome(client: TestClient) -> None:
    client.post("/rubrica", json={"nome": "Marco"})
    client.post("/rubrica", json={"nome": "Anna"})
    assert client.delete("/rubrica/Marco").status_code == 200
    assert nomi(client) == ["Anna"]


def test_la_rubrica_resta_salvata_dopo_un_riavvio(client: TestClient, nuovo_client: Callable[[], TestClient]) -> None:
    client.post("/rubrica", json={"nome": "Marco"})
    client.post("/rubrica", json={"nome": "Anna"})
    with nuovo_client() as riavviato:
        assert nomi(riavviato) == ["Anna", "Marco"]
