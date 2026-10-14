"""Divisione di un ordine tra persone. Modulo puro: lavora in centesimi interi."""
from decimal import ROUND_HALF_UP, Decimal

from .modelli import CENT, ProdottoAssegnato, QuotaPersona, Ripartizione, RichiestaCalcolo


class AssegnazioniNonValide(ValueError):
    """Le unità assegnate non coprono esattamente le quantità delle righe."""


def centesimi(importo: Decimal) -> int:
    return int((importo / CENT).quantize(Decimal(1), rounding=ROUND_HALF_UP))


def da_centesimi(cent: int) -> Decimal:
    return (Decimal(cent) * CENT).quantize(CENT)


def resto_maggiore(totale: int, pesi: list[int]) -> list[int]:
    """Divide `totale` centesimi in parti proporzionali ai pesi; la somma è esattamente `totale`.

    I centesimi avanzati dall'arrotondamento per difetto vanno alle parti con il resto maggiore
    (a parità di resto, a quella che viene prima).
    """
    segno = -1 if totale < 0 else 1
    totale = abs(totale)
    somma_pesi = sum(pesi)
    if somma_pesi == 0:
        pesi, somma_pesi = [1] * len(pesi), len(pesi)
    quote = [totale * p // somma_pesi for p in pesi]
    resti = [totale * p % somma_pesi for p in pesi]
    for i in sorted(range(len(pesi)), key=lambda i: -resti[i])[: totale - sum(quote)]:
        quote[i] += 1
    return [segno * q for q in quote]


def ripartisci(richiesta: RichiestaCalcolo) -> Ripartizione:
    ordine = richiesta.ordine
    _verifica_assegnazioni(richiesta)

    persone: dict[str, list[ProdottoAssegnato]] = {}
    for a in richiesta.assegnazioni:
        p = ordine.prodotti[a.riga]
        persone.setdefault(a.persona, []).append(
            ProdottoAssegnato(
                riga=a.riga,
                nome=p.nome,
                dettagli=p.dettagli,
                unita=a.unita,
                unita_riga=p.quantita,
                prezzo_unitario=p.prezzo_unitario,
                totale=da_centesimi(centesimi(a.unita * p.prezzo_unitario)),
            )
        )

    nomi = list(persone)
    subtotali = [sum(centesimi(x.totale) for x in persone[n]) for n in nomi]
    costi = sum(centesimi(c.importo) for c in ordine.costi_comuni)
    pesi = subtotali if richiesta.criterio == "proporzionale" else [1] * len(nomi)
    quote = resto_maggiore(costi, pesi)

    return Ripartizione(
        criterio=richiesta.criterio,
        persone=[
            QuotaPersona(
                nome=n,
                prodotti=sorted(persone[n], key=lambda x: x.riga),
                subtotale=da_centesimi(s),
                quota_costi_comuni=da_centesimi(q),
                totale=da_centesimi(s + q),
            )
            for n, s, q in zip(nomi, subtotali, quote)
        ],
        subtotale_prodotti=da_centesimi(sum(subtotali)),
        costi_comuni=da_centesimi(costi),
        totale=da_centesimi(sum(subtotali) + costi),
    )


def _verifica_assegnazioni(richiesta: RichiestaCalcolo) -> None:
    prodotti = richiesta.ordine.prodotti
    assegnate = [0] * len(prodotti)
    for a in richiesta.assegnazioni:
        if a.riga >= len(prodotti):
            raise AssegnazioniNonValide(f"La riga {a.riga} non esiste")
        assegnate[a.riga] += a.unita
    errori = [
        f"{p.nome}: {n} unità assegnate su {p.quantita}"
        for p, n in zip(prodotti, assegnate)
        if n != p.quantita
    ]
    if errori:
        raise AssegnazioniNonValide("; ".join(errori))
