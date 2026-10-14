from typing import Any

from fastapi.testclient import TestClient

from conftest import EstrattoreFinto, output_grezzo

SCREENSHOT = {"file": ("carrello.png", b"immagine", "image/png")}


def estrai(client: TestClient, estrattore: EstrattoreFinto, **grezzo: Any) -> Any:
    estrattore.risposta = output_grezzo(**grezzo)
    r = client.post("/estrai", files=SCREENSHOT)
    assert r.status_code == 200, r.text
    return r.json()


def prezzi(risposta: Any) -> list[str]:
    return [p["prezzo_unitario"] for p in risposta["ordine"]["prodotti"]]


# --- Normalizzazione dell'output del modello ---

def test_i_costi_comuni_da_zero_vengono_scartati(client: TestClient, estrattore: EstrattoreFinto) -> None:
    r = estrai(client, estrattore, costi_comuni=[
        {"descrizione": "Spedizione", "importo": 11.95, "tipo": "spedizione"},
        {"descrizione": "Assicurazione", "importo": 0, "tipo": "assicurazione"},
    ])
    assert [c["descrizione"] for c in r["ordine"]["costi_comuni"]] == ["Spedizione"]


def test_il_prezzo_unitario_si_ricava_dal_totale_di_riga(client: TestClient, estrattore: EstrattoreFinto) -> None:
    r = estrai(client, estrattore, prodotti=[
        {"nome": "A", "quantita": 4, "dettagli": "", "prezzo_unitario": None, "totale_riga": 5.20},
    ], totali_dichiarati={"subtotale_prodotti": 5.20, "totale": None})
    assert prezzi(r) == ["1.30"]


def test_i_totali_di_riga_scambiati_per_prezzi_unitari_vengono_corretti(client: TestClient, estrattore: EstrattoreFinto) -> None:
    # Caso osservato con il CSV inglese: il modello copia il "Line total" in prezzo_unitario
    r = estrai(client, estrattore, prodotti=[
        {"nome": "A", "quantita": 1, "dettagli": "", "prezzo_unitario": 6.00, "totale_riga": None},
        {"nome": "B", "quantita": 3, "dettagli": "", "prezzo_unitario": 7.50, "totale_riga": None},
        {"nome": "C", "quantita": 2, "dettagli": "", "prezzo_unitario": 54.00, "totale_riga": None},
    ])
    assert prezzi(r) == ["6.00", "2.50", "27.00"]
    assert r["coerenza"]["ok"] is True


def test_i_prezzi_unitari_corretti_non_vengono_toccati(client: TestClient, estrattore: EstrattoreFinto) -> None:
    assert prezzi(estrai(client, estrattore)) == ["6.00", "2.50", "27.00"]


def test_senza_subtotale_dichiarato_i_prezzi_restano_come_estratti(client: TestClient, estrattore: EstrattoreFinto) -> None:
    r = estrai(client, estrattore, prodotti=[
        {"nome": "B", "quantita": 3, "dettagli": "", "prezzo_unitario": 7.50, "totale_riga": None},
    ], totali_dichiarati={"subtotale_prodotti": None, "totale": None})
    assert prezzi(r) == ["7.50"]


def test_la_valuta_mancante_diventa_euro(client: TestClient, estrattore: EstrattoreFinto) -> None:
    assert estrai(client, estrattore, valuta=None)["ordine"]["valuta"] == "EUR"


def test_uno_sconto_con_importo_positivo_diventa_altro(client: TestClient, estrattore: EstrattoreFinto) -> None:
    r = estrai(client, estrattore, costi_comuni=[
        {"descrizione": "Tasse di servizio", "importo": 0.85, "tipo": "sconto"},
        {"descrizione": "Coupon", "importo": -2.00, "tipo": "sconto"},
    ])
    assert [c["tipo"] for c in r["ordine"]["costi_comuni"]] == ["altro", "sconto"]


def test_campi_mancanti_o_strani_del_modello_non_bloccano_l_estrazione(client: TestClient, estrattore: EstrattoreFinto) -> None:
    r = estrai(client, estrattore, ordine=None, totali_dichiarati=None, prodotti=[
        {"nome": "A", "quantita": 0, "prezzo_unitario": 1.0},
    ], costi_comuni=[{"descrizione": "Dogana", "importo": 3.0, "tipo": "dazio"}])
    assert r["ordine"]["prodotti"][0]["quantita"] == 1
    assert r["ordine"]["prodotti"][0]["dettagli"] == ""
    assert r["ordine"]["costi_comuni"][0]["tipo"] == "altro"
    assert r["ordine"]["ordine"] == {"numero": None, "data": None, "venditore": None}


def test_un_prodotto_senza_prezzo_vale_zero(client: TestClient, estrattore: EstrattoreFinto) -> None:
    r = estrai(client, estrattore, prodotti=[
        {"nome": "A", "quantita": 1, "dettagli": "", "prezzo_unitario": None, "totale_riga": None},
    ])
    assert prezzi(r) == ["0.00"]


# --- Controllo di coerenza ---

def test_l_estrazione_riporta_che_i_totali_tornano(client: TestClient, estrattore: EstrattoreFinto) -> None:
    c = estrai(client, estrattore)["coerenza"]
    assert c == {
        "ok": True,
        "subtotale_calcolato": "67.50", "subtotale_dichiarato": "67.50", "differenza_subtotale": "0.00",
        "totale_calcolato": "80.30", "totale_dichiarato": "80.30", "differenza_totale": "0.00",
    }


def test_l_estrazione_segnala_un_subtotale_che_non_torna(client: TestClient, estrattore: EstrattoreFinto) -> None:
    c = estrai(client, estrattore, totali_dichiarati={"subtotale_prodotti": 70.00, "totale": 82.80})["coerenza"]
    assert c["ok"] is False
    assert c["differenza_subtotale"] == "-2.50"
    assert c["differenza_totale"] == "-2.50"


def test_l_estrazione_segnala_un_totale_che_non_torna(client: TestClient, estrattore: EstrattoreFinto) -> None:
    # manca un costo comune: subtotale giusto, totale no
    c = estrai(client, estrattore, costi_comuni=[{"descrizione": "Spedizione", "importo": 11.95, "tipo": "spedizione"}])["coerenza"]
    assert c["ok"] is False
    assert c["differenza_subtotale"] == "0.00"
    assert c["differenza_totale"] == "-0.85"


def test_senza_totali_dichiarati_la_coerenza_non_si_puo_verificare(client: TestClient, estrattore: EstrattoreFinto) -> None:
    c = estrai(client, estrattore, totali_dichiarati={"subtotale_prodotti": None, "totale": None})["coerenza"]
    assert c["ok"] is None
    assert c["differenza_subtotale"] is None and c["differenza_totale"] is None


def test_verifica_ricontrolla_un_ordine_corretto_a_mano(client: TestClient, estrattore: EstrattoreFinto) -> None:
    ordine = estrai(client, estrattore, costi_comuni=[{"descrizione": "Spedizione", "importo": 11.95, "tipo": "spedizione"}])["ordine"]
    ordine["costi_comuni"].append({"descrizione": "Tasse di servizio", "importo": "0.85", "tipo": "commissione"})
    r = client.post("/verifica", json=ordine)
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_un_totale_di_riga_non_divisibile_non_perde_centesimi(client: TestClient, estrattore: EstrattoreFinto) -> None:
    r = estrai(client, estrattore, prodotti=[
        {"nome": "Bustine", "quantita": 3, "dettagli": "", "prezzo_unitario": None, "totale_riga": 10.00},
    ], costi_comuni=[], totali_dichiarati={"subtotale_prodotti": 10.00, "totale": 10.00})
    assert r["coerenza"]["ok"] is True
    assegnazioni = [{"riga": 0, "persona": "Marco", "unita": 1}, {"riga": 0, "persona": "Anna", "unita": 2}]
    calcolo = client.post("/calcola", json={"ordine": r["ordine"], "assegnazioni": assegnazioni}).json()
    assert [p["totale"] for p in calcolo["persone"]] == ["3.33", "6.67"]
    assert calcolo["totale"] == "10.00"
