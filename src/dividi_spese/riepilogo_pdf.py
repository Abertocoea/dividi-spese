"""PDF di riepilogo: una pagina di sintesi e un recap per persona, ognuno su una pagina propria."""
import io
import re
from datetime import date
from collections.abc import Sequence
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Flowable, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .formato import euro
from .modelli import OrdineEstratto, QuotaPersona, Ripartizione

CRITERI = {
    "proporzionale": "in proporzione alla spesa in prodotti di ciascuno",
    "parti_uguali": "in parti uguali tra le persone con almeno un prodotto",
}

_stili = getSampleStyleSheet()
TITOLO = _stili["Title"]
SOTTOTITOLO = _stili["Heading2"]
TESTO = _stili["BodyText"]
PICCOLO = ParagraphStyle("piccolo", parent=TESTO, fontSize=8, textColor=colors.grey)


def nome_file(ordine: OrdineEstratto) -> str:
    parti = [re.sub(r"[^\w-]", "", p) for p in (ordine.ordine.numero, ordine.ordine.data) if p]
    return "_".join(["riepilogo", *[p for p in parti if p]]) + ".pdf"


def genera(ordine: OrdineEstratto, ripartizione: Ripartizione) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, title="Riepilogo spese", leftMargin=18 * mm, rightMargin=18 * mm)
    elementi = _sintesi(ordine, ripartizione)
    for persona in ripartizione.persone:
        elementi += [PageBreak(), *_recap(ordine, persona)]
    doc.build(elementi)
    return buffer.getvalue()


def _intestazione_ordine(ordine: OrdineEstratto) -> str:
    dati = ordine.ordine
    parti = []
    if dati.numero:
        parti.append(f"Ordine n. {dati.numero}")
    if dati.data:
        parti.append(f"del {_data(dati.data)}")
    if dati.venditore:
        parti.append(f"· venditore {dati.venditore}")
    return " ".join(parti) or "Ordine"


def _data(iso: str) -> str:
    try:
        return date.fromisoformat(iso).strftime("%d/%m/%Y")
    except ValueError:
        return iso


def _sintesi(ordine: OrdineEstratto, ripartizione: Ripartizione) -> list[Flowable]:
    righe = [["Persona", "Prodotti", "Costi comuni", "Da pagare"]]
    righe += [[p.nome, euro(p.subtotale), euro(p.quota_costi_comuni), euro(p.totale)] for p in ripartizione.persone]
    righe.append(["Totale", euro(ripartizione.subtotale_prodotti), euro(ripartizione.costi_comuni), euro(ripartizione.totale)])

    costi = [[c.descrizione, euro(c.importo)] for c in ordine.costi_comuni] or [["Nessun costo comune", ""]]
    return [
        Paragraph("Riepilogo spese", TITOLO),
        Paragraph(_intestazione_ordine(ordine), TESTO),
        Paragraph(f"Totale dell'ordine: <b>{euro(ripartizione.totale)}</b>", TESTO),
        Spacer(1, 6 * mm),
        _tabella(righe, larghezze=[60, 38, 38, 38], totale=True),
        Spacer(1, 8 * mm),
        Paragraph("Costi comuni", SOTTOTITOLO),
        _tabella(costi, larghezze=[136, 38], intestazione=False),
        Spacer(1, 4 * mm),
        Paragraph(f"Criterio di ripartizione ({ripartizione.criterio}): costi comuni divisi {CRITERI[ripartizione.criterio]}.", TESTO),
    ]


def _recap(ordine: OrdineEstratto, persona: QuotaPersona) -> list[Flowable]:
    righe: list[list[Any]] = [["Qtà", "Prodotto", "Dettagli", "Prezzo", "Totale"]]
    for prodotto in persona.prodotti:
        unita = prodotto.unita
        quantita = f"{unita} di {prodotto.unita_riga}" if unita != prodotto.unita_riga else str(unita)
        righe.append([quantita, Paragraph(prodotto.nome, TESTO), Paragraph(prodotto.dettagli, PICCOLO), euro(prodotto.prezzo_unitario), euro(prodotto.totale)])
    conti = [
        ["Subtotale prodotti", euro(persona.subtotale)],
        ["Quota costi comuni", euro(persona.quota_costi_comuni)],
        ["Totale da pagare", euro(persona.totale)],
    ]
    return [
        Paragraph(f"Recap di {persona.nome}", TITOLO),
        Paragraph(_intestazione_ordine(ordine), TESTO),
        Paragraph("Controlla che questi siano i prodotti che hai preso.", PICCOLO),
        Spacer(1, 6 * mm),
        _tabella(righe, larghezze=[18, 70, 42, 22, 22]),
        Spacer(1, 6 * mm),
        _tabella(conti, larghezze=[136, 38], intestazione=False, totale=True),
    ]


def _tabella(righe: Sequence[list[Any]], larghezze: list[int], intestazione: bool = True, totale: bool = False) -> Table:
    t = Table(righe, colWidths=[w * mm for w in larghezze], repeatRows=1 if intestazione else 0)
    stile: list[Any] = [
        ("ALIGN", (-1, 0), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.lightgrey),
    ]
    if intestazione:
        stile += [("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("LINEBELOW", (0, 0), (-1, 0), 0.75, colors.black)]
        if len(larghezze) > 2:
            stile.append(("ALIGN", (-3, 0), (-1, -1), "RIGHT"))
    if totale:
        stile += [("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"), ("LINEABOVE", (0, -1), (-1, -1), 0.75, colors.black)]
    t.setStyle(TableStyle(stile))
    return t
