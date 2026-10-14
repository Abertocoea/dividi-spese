from typing import Any

from fastapi.testclient import TestClient


def prodotto(nome: str, quantita: int, prezzo: str) -> dict[str, Any]:
    return {"nome": nome, "quantita": quantita, "dettagli": "", "prezzo_unitario": prezzo}


def ordine(prodotti: list[dict[str, Any]], costi: list[str]) -> dict[str, Any]:
    return {
        "valuta": "EUR",
        "ordine": {"numero": None, "data": None, "venditore": None},
        "prodotti": prodotti,
        "costi_comuni": [{"descrizione": f"Costo {i}", "importo": c, "tipo": "altro"} for i, c in enumerate(costi)],
        "totali_dichiarati": {"subtotale_prodotti": None, "totale": None},
    }


def totali(risposta: dict[str, Any]) -> dict[str, str]:
    return {p["nome"]: p["totale"] for p in risposta["persone"]}


# Esempio della spec: costi comuni 12,80 €, Marco 100,00 €, Anna 69,20 €
ESEMPIO = ordine([prodotto("A", 1, "100.00"), prodotto("B", 1, "69.20")], ["11.95", "0.85"])
ASSEGNAZIONI_ESEMPIO = [{"riga": 0, "persona": "Marco", "unita": 1}, {"riga": 1, "persona": "Anna", "unita": 1}]


def test_ripartizione_proporzionale_esempio_della_spec(client: TestClient) -> None:
    r = client.post("/calcola", json={"ordine": ESEMPIO, "assegnazioni": ASSEGNAZIONI_ESEMPIO, "criterio": "proporzionale"})
    assert r.status_code == 200
    assert totali(r.json()) == {"Marco": "107.57", "Anna": "74.43"}
    assert r.json()["totale"] == "182.00"


def test_ripartizione_in_parti_uguali_esempio_della_spec(client: TestClient) -> None:
    r = client.post("/calcola", json={"ordine": ESEMPIO, "assegnazioni": ASSEGNAZIONI_ESEMPIO, "criterio": "parti_uguali"})
    assert totali(r.json()) == {"Marco": "106.40", "Anna": "75.60"}


def test_la_ripartizione_proporzionale_e_il_criterio_predefinito(client: TestClient) -> None:
    r = client.post("/calcola", json={"ordine": ESEMPIO, "assegnazioni": ASSEGNAZIONI_ESEMPIO})
    assert r.json()["criterio"] == "proporzionale"
    assert totali(r.json()) == {"Marco": "107.57", "Anna": "74.43"}


def test_i_centesimi_avanzati_vanno_a_chi_ha_il_resto_maggiore(client: TestClient) -> None:
    # 10,00 € di costi tra 3 persone: 3,33 + 3,33 + 3,33 = 9,99, il centesimo avanzato va alla prima
    o = ordine([prodotto("A", 1, "5.00"), prodotto("B", 1, "5.00"), prodotto("C", 1, "5.00")], ["10.00"])
    assegnazioni = [{"riga": i, "persona": n, "unita": 1} for i, n in enumerate(["Marco", "Anna", "Luca"])]
    r = client.post("/calcola", json={"ordine": o, "assegnazioni": assegnazioni, "criterio": "parti_uguali"})
    quote = [p["quota_costi_comuni"] for p in r.json()["persone"]]
    assert quote == ["3.34", "3.33", "3.33"]
    assert r.json()["totale"] == "25.00"


def test_la_somma_dei_totali_e_sempre_il_totale_dell_ordine(client: TestClient) -> None:
    o = ordine([prodotto("A", 1, "33.33"), prodotto("B", 1, "17.01"), prodotto("C", 1, "0.99")], ["7.77", "1.13"])
    assegnazioni = [{"riga": i, "persona": n, "unita": 1} for i, n in enumerate(["Marco", "Anna", "Luca"])]
    r = client.post("/calcola", json={"ordine": o, "assegnazioni": assegnazioni})
    somma = sum(float(p["totale"]) for p in r.json()["persone"])
    assert round(somma, 2) == 60.23
    assert totali(r.json()) == {"Marco": "39.11", "Anna": "19.96", "Luca": "1.16"}


def test_le_unita_di_una_riga_si_dividono_tra_piu_persone(client: TestClient) -> None:
    o = ordine([prodotto("Fauceardente", 4, "1.30")], [])
    assegnazioni = [{"riga": 0, "persona": "Marco", "unita": 3}, {"riga": 0, "persona": "Anna", "unita": 1}]
    r = client.post("/calcola", json={"ordine": o, "assegnazioni": assegnazioni})
    assert totali(r.json()) == {"Marco": "3.90", "Anna": "1.30"}
    prodotti_anna = r.json()["persone"][1]["prodotti"]
    assert [(p["unita"], p["unita_riga"]) for p in prodotti_anna] == [(1, 4)]


def test_chi_non_ha_prodotti_non_paga_i_costi_in_parti_uguali(client: TestClient) -> None:
    o = ordine([prodotto("A", 2, "10.00")], ["9.00"])
    assegnazioni = [{"riga": 0, "persona": "Marco", "unita": 2}]
    r = client.post("/calcola", json={"ordine": o, "assegnazioni": assegnazioni, "criterio": "parti_uguali"})
    assert totali(r.json()) == {"Marco": "29.00"}


def test_gli_sconti_riducono_i_costi_comuni_di_tutti(client: TestClient) -> None:
    # spedizione 10,00 € e coupon -4,00 €: restano 6,00 € da dividere in proporzione 3:1
    o = ordine([prodotto("A", 1, "30.00"), prodotto("B", 1, "10.00")], ["10.00", "-4.00"])
    r = client.post("/calcola", json={"ordine": o, "assegnazioni": ASSEGNAZIONI_ESEMPIO})
    assert totali(r.json()) == {"Marco": "34.50", "Anna": "11.50"}


def test_uno_sconto_maggiore_dei_costi_si_divide_come_credito(client: TestClient) -> None:
    o = ordine([prodotto("A", 1, "30.00"), prodotto("B", 1, "10.00")], ["-10.00"])
    r = client.post("/calcola", json={"ordine": o, "assegnazioni": ASSEGNAZIONI_ESEMPIO, "criterio": "parti_uguali"})
    assert totali(r.json()) == {"Marco": "25.00", "Anna": "5.00"}


def test_rifiuta_il_calcolo_con_unita_non_assegnate(client: TestClient) -> None:
    o = ordine([prodotto("Fauceardente", 4, "1.30")], [])
    r = client.post("/calcola", json={"ordine": o, "assegnazioni": [{"riga": 0, "persona": "Marco", "unita": 3}]})
    assert r.status_code == 422
    assert "Fauceardente: 3 unità assegnate su 4" in r.json()["detail"]


def test_rifiuta_il_calcolo_con_unita_assegnate_in_eccesso(client: TestClient) -> None:
    o = ordine([prodotto("A", 1, "1.00")], [])
    assegnazioni = [{"riga": 0, "persona": "Marco", "unita": 1}, {"riga": 0, "persona": "Anna", "unita": 1}]
    r = client.post("/calcola", json={"ordine": o, "assegnazioni": assegnazioni})
    assert r.status_code == 422
    assert "A: 2 unità assegnate su 1" in r.json()["detail"]
