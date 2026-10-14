"""Conversione del file caricato in ciò che il modello riceve."""
import csv
import io
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Any

import openpyxl
import pymupdf
from pydantic import BaseModel

from .estrazione import ContenutoDocumento
from .formato import numero_italiano

FORMATI = "PDF, PNG, JPG, WebP, CSV, XLSX"
IMMAGINI = {"png", "jpg", "jpeg", "webp"}
# Sotto questa soglia di caratteri un PDF è considerato scansionato.
MIN_CARATTERI_TESTO = 20
SIMBOLI_VALUTA = ("€", "$", "£")


class FormatoNonSupportato(ValueError):
    def __init__(self, estensione: str) -> None:
        super().__init__(f"Formato .{estensione} non supportato. Formati accettati: {FORMATI}")


class FileIlleggibile(ValueError):
    pass


class Foglio(BaseModel):
    """Tabella originale di un CSV o di un foglio Excel, per l'anteprima."""

    nome: str
    righe: list[list[str]]


@dataclass
class DocumentoConvertito:
    contenuto: ContenutoDocumento
    anteprima: list[Foglio] = field(default_factory=list)


def converti(nome: str, dati: bytes) -> DocumentoConvertito:
    estensione = nome.rsplit(".", 1)[-1].lower() if "." in nome else ""
    if estensione == "pdf":
        return DocumentoConvertito(_pdf(dati))
    if estensione in IMMAGINI:
        return DocumentoConvertito(ContenutoDocumento(immagini=[dati]))
    if estensione == "csv":
        return _tabelle([Foglio(nome=nome, righe=_csv(dati))], intestazioni=False)
    if estensione == "xlsx":
        return _tabelle(_xlsx(dati), intestazioni=True)
    raise FormatoNonSupportato(estensione)


def _pdf(dati: bytes) -> ContenutoDocumento:
    try:
        # pymupdf ha annotazioni di tipo incomplete (Document non risulta iterabile)
        doc: Any = pymupdf.open(stream=dati, filetype="pdf")  # type: ignore[no-untyped-call]
    except Exception as e:
        raise FileIlleggibile("PDF illeggibile") from e
    testo = "\n".join(pagina.get_text(sort=True) for pagina in doc)
    if len(testo.strip()) >= MIN_CARATTERI_TESTO:
        return ContenutoDocumento(testo=testo)
    return ContenutoDocumento(immagini=[pagina.get_pixmap(dpi=150).tobytes("png") for pagina in doc])


def _tabelle(fogli: list[Foglio], intestazioni: bool) -> DocumentoConvertito:
    blocchi = []
    for f in fogli:
        righe = "\n".join(" | ".join(r) for r in f.righe)
        blocchi.append(f"## Sheet: {f.nome}\n{righe}" if intestazioni else righe)
    return DocumentoConvertito(ContenutoDocumento(testo="\n\n".join(blocchi)), anteprima=fogli)


def _csv(dati: bytes) -> list[list[str]]:
    try:
        testo = dati.decode("utf-8-sig")
    except UnicodeDecodeError:
        testo = dati.decode("cp1252", errors="replace")
    campione = testo[:4096]
    try:
        dialetto: type[csv.Dialect] | csv.Dialect = csv.Sniffer().sniff(campione, delimiters=",;\t|")
    except csv.Error:
        dialetto = csv.excel
    righe = [r for r in csv.reader(io.StringIO(testo), dialetto) if any(c.strip() for c in r)]
    if not righe:
        raise FileIlleggibile("CSV illeggibile o vuoto")
    return righe


def _xlsx(dati: bytes) -> list[Foglio]:
    try:
        libro = openpyxl.load_workbook(io.BytesIO(dati), data_only=True)
    except Exception as e:
        raise FileIlleggibile("File Excel illeggibile") from e
    fogli = []
    for ws in libro.worksheets:
        righe = []
        for riga in ws.iter_rows():
            celle = [_cella(c.value, c.number_format) for c in riga]
            while celle and not celle[-1]:
                celle.pop()
            if celle:
                righe.append(celle)
        fogli.append(Foglio(nome=ws.title, righe=righe))
    return fogli


def _cella(valore: object, formato: str) -> str:
    """Testo della cella come appare in Excel (formato italiano), conservando il simbolo di valuta."""
    if valore is None:
        return ""
    if isinstance(valore, datetime | date):
        return valore.strftime("%Y-%m-%d")
    if isinstance(valore, int | float | Decimal) and not isinstance(valore, bool):
        if formato == "General":
            if isinstance(valore, int) or float(valore).is_integer():
                return str(int(valore))
            return numero_italiano(Decimal(str(valore)), decimali=2, migliaia=False)
        sezione = formato.split(";")[0]
        cifre_decimali = re.search(r"\.([0#]+)", sezione)
        testo = numero_italiano(
            Decimal(str(valore)),
            decimali=len(cifre_decimali.group(1)) if cifre_decimali else 0,
            migliaia="," in sezione.split(".")[0],
        )
        simbolo = next((s for s in SIMBOLI_VALUTA if s in sezione), None)
        return f"{testo} {simbolo}" if simbolo else testo
    return str(valore)
