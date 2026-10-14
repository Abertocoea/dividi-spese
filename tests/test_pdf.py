from typing import Any

import pymupdf
from fastapi.testclient import TestClient


def richiesta(criterio: str = "proporzionale") -> dict[str, Any]:
    return {
        "ordine": {
            "valuta": "EUR",
            "ordine": {"numero": "1000000001", "data": "2026-10-12", "venditore": "Venditore Esempio"},
            "prodotti": [
                {"nome": "Laghetto Bollente", "quantita": 1, "dettagli": "EN NM MH2", "prezzo_unitario": "100.00"},
                {"nome": "Fauceardente di Ossidiana", "quantita": 4, "dettagli": "IT NM MH2", "prezzo_unitario": "1.30"},
                {"nome": "Silenzio", "quantita": 1, "dettagli": "IT NM M10", "prezzo_unitario": "64.00"},
            ],
            "costi_comuni": [
                {"descrizione": "Spese di spedizione", "importo": "11.95", "tipo": "spedizione"},
                {"descrizione": "Tasse di servizio TRUST", "importo": "0.85", "tipo": "commissione"},
            ],
            "totali_dichiarati": {"subtotale_prodotti": "169.20", "totale": "182.00"},
        },
        "assegnazioni": [
            {"riga": 0, "persona": "Marco", "unita": 1},
            {"riga": 1, "persona": "Anna", "unita": 2},
            {"riga": 1, "persona": "Marco", "unita": 2},
            {"riga": 2, "persona": "Anna", "unita": 1},
        ],
        "criterio": criterio,
    }


def pagine(client: TestClient, corpo: dict[str, Any]) -> list[str]:
    r = client.post("/pdf", json=corpo)
    assert r.status_code == 200, r.text
    assert r.headers["content-type"] == "application/pdf"
    doc: Any = pymupdf.open(stream=r.content, filetype="pdf")
    return [p.get_text() for p in doc]


def test_il_riepilogo_ha_una_pagina_di_sintesi_e_una_pagina_per_persona(client: TestClient) -> None:
    testo = pagine(client, richiesta())
    assert len(testo) == 3
    assert "Marco" in testo[1] and "Anna" not in testo[1]
    assert "Anna" in testo[2] and "Marco" not in testo[2]


def test_la_sintesi_contiene_ordine_totali_per_persona_costi_e_criterio(client: TestClient) -> None:
    sintesi = pagine(client, richiesta())[0]
    for atteso in ("1000000001", "12/10/2026", "Venditore Esempio", "182,00 €",
                   "Spese di spedizione", "11,95 €", "Tasse di servizio TRUST", "0,85 €",
                   "proporzionale", "Marco", "Anna"):
        assert atteso in sintesi, atteso
    # Marco: 102,60 € di prodotti + 7,76 € di costi; Anna: 66,60 € + 5,04 €
    for atteso in ("102,60 €", "7,76 €", "110,36 €", "66,60 €", "5,04 €", "71,64 €"):
        assert atteso in sintesi, atteso


def test_la_sintesi_indica_il_criterio_in_parti_uguali(client: TestClient) -> None:
    assert "in parti uguali" in pagine(client, richiesta("parti_uguali"))[0]


def test_il_recap_di_una_persona_elenca_tutti_e_soli_i_suoi_prodotti(client: TestClient) -> None:
    recap_marco = pagine(client, richiesta())[1]
    assert "Laghetto Bollente" in recap_marco and "Fauceardente di Ossidiana" in recap_marco
    assert "Silenzio" not in recap_marco
    for atteso in ("100,00 €", "2,60 €", "102,60 €", "7,76 €", "110,36 €", "1000000001"):
        assert atteso in recap_marco, atteso


def test_il_recap_indica_le_unita_delle_righe_condivise(client: TestClient) -> None:
    recap_anna = pagine(client, richiesta())[2]
    assert "2 di 4" in recap_anna
    assert "1 di 1" not in recap_anna


def test_il_nome_del_file_contiene_numero_e_data_dell_ordine(client: TestClient) -> None:
    r = client.post("/pdf", json=richiesta())
    assert 'filename="riepilogo_1000000001_2026-10-12.pdf"' in r.headers["content-disposition"]


def test_senza_numero_e_data_il_file_ha_un_nome_generico(client: TestClient) -> None:
    corpo = richiesta()
    corpo["ordine"]["ordine"] = {"numero": None, "data": None, "venditore": None}
    r = client.post("/pdf", json=corpo)
    assert 'filename="riepilogo.pdf"' in r.headers["content-disposition"]


def test_il_pdf_non_si_genera_con_unita_non_assegnate(client: TestClient) -> None:
    corpo = richiesta()
    corpo["assegnazioni"].pop()
    assert client.post("/pdf", json=corpo).status_code == 422


def test_il_markup_nei_nomi_viene_stampato_come_testo(client: TestClient, tmp_path: Any) -> None:
    # Un nome estratto da un documento malevolo non deve poter includere file locali nel PDF
    corpo = richiesta()
    segreto = tmp_path / "segreto.png"
    corpo["ordine"]["prodotti"][0]["nome"] = f'<img src="{segreto}" width="10" height="10"/>Carta'
    corpo["ordine"]["prodotti"][0]["dettagli"] = "<b>NM</b> & foil"
    corpo["ordine"]["ordine"]["venditore"] = "<font color='red'>Venditore</font>"
    testo = pagine(client, corpo)
    assert f'<img src="{segreto}"' in testo[1].replace("\n", "")
    assert "<b>NM</b> & foil" in testo[1]
    assert "<font color='red'>Venditore</font>" in testo[0]
