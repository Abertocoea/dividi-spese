"""API HTTP: unico punto di ingresso del frontend."""
from importlib.resources import files
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, Request, Response, UploadFile
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.middleware.base import RequestResponseEndpoint
from pydantic import BaseModel, Field, field_validator

from .coerenza import Coerenza, verifica
from .documenti import FileIlleggibile, Foglio, FormatoNonSupportato, converti
from .estrazione import MODELLO_PREDEFINITO, ErroreOllama, Estrattore, ModelloNonInstallato, OllamaNonRaggiungibile
from .modelli import OrdineEstratto, Ripartizione, RichiestaCalcolo
from .normalizzazione import normalizza
from . import riepilogo_pdf
from .rubrica import NomeNonTrovato, Rubrica
from .ripartizione import AssegnazioniNonValide, ripartisci


class RispostaEstrazione(BaseModel):
    ordine: OrdineEstratto
    coerenza: Coerenza
    anteprima: list[Foglio]
    avvisi: list[str]


class ElencoModelli(BaseModel):
    modelli: list[str]
    predefinito: str


class Nome(BaseModel):
    nome: str = Field(min_length=1)

    @field_validator("nome", mode="before")
    @classmethod
    def _senza_spazi(cls, v: object) -> object:
        return v.strip() if isinstance(v, str) else v


class ElencoNomi(BaseModel):
    nomi: list[str]


HOST_LOCALI = ["127.0.0.1", "localhost"]


def crea_app(estrattore: Estrattore, cartella_dati: Path) -> FastAPI:
    app = FastAPI(title="Dividi Spese")
    # Il server è raggiungibile da qualsiasi pagina aperta nel browser: si accettano solo richieste
    # indirizzate a localhost (contro il DNS rebinding) e provenienti dalla pagina dell'app (contro il CSRF).
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=HOST_LOCALI)

    @app.middleware("http")
    async def solo_dalla_pagina_dell_app(request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Origin deve coincidere esattamente (porta compresa) con l'indirizzo dell'app: un'altra app su
        # localhost:3000 o una pagina con "Origin: null" non è la pagina dell'app.
        origine = request.headers.get("origin")
        propria = f"{request.url.scheme}://{request.headers.get('host', '')}"
        da_altro_sito = request.headers.get("sec-fetch-site") in ("cross-site", "same-site")
        if (origine is not None and origine != propria) or da_altro_sito:
            return JSONResponse({"detail": "Richiesta da un altro sito rifiutata"}, status_code=403)
        return await call_next(request)

    rubrica = Rubrica(cartella_dati)

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    def pagina() -> str:
        return files(__package__).joinpath("static/index.html").read_text(encoding="utf-8")

    @app.post("/estrai")
    def estrai(file: UploadFile = File(), modello: str | None = Form(None)) -> RispostaEstrazione:
        try:
            documento = converti(file.filename or "", file.file.read())
        except FormatoNonSupportato as e:
            raise HTTPException(415, str(e)) from e
        except FileIlleggibile as e:
            raise HTTPException(422, str(e)) from e
        try:
            grezzo, avvisi = estrattore.estrai(documento.contenuto, modello)
        except OllamaNonRaggiungibile as e:
            raise HTTPException(503, str(e)) from e
        except ModelloNonInstallato as e:
            raise HTTPException(424, str(e)) from e
        except ErroreOllama as e:
            raise HTTPException(502, str(e)) from e
        ordine = normalizza(grezzo)
        return RispostaEstrazione(ordine=ordine, coerenza=verifica(ordine), anteprima=documento.anteprima, avvisi=avvisi)

    @app.get("/modelli")
    def modelli() -> ElencoModelli:
        try:
            return ElencoModelli(modelli=estrattore.modelli(), predefinito=MODELLO_PREDEFINITO)
        except OllamaNonRaggiungibile as e:
            raise HTTPException(503, str(e)) from e

    @app.post("/verifica")
    def verifica_ordine(ordine: OrdineEstratto) -> Coerenza:
        return verifica(ordine)

    @app.post("/calcola")
    def calcola(richiesta: RichiestaCalcolo) -> Ripartizione:
        return _ripartisci(richiesta)

    @app.post("/pdf")
    def pdf(richiesta: RichiestaCalcolo) -> Response:
        ripartizione = _ripartisci(richiesta)
        return Response(
            riepilogo_pdf.genera(richiesta.ordine, ripartizione),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{riepilogo_pdf.nome_file(richiesta.ordine)}"'},
        )

    @app.get("/rubrica")
    def leggi_rubrica() -> ElencoNomi:
        return ElencoNomi(nomi=rubrica.nomi())

    @app.post("/rubrica")
    def aggiungi_nome(nome: Nome) -> ElencoNomi:
        rubrica.aggiungi(nome.nome)
        return ElencoNomi(nomi=rubrica.nomi())

    @app.put("/rubrica/{vecchio}")
    def rinomina_nome(vecchio: str, nome: Nome) -> ElencoNomi:
        try:
            rubrica.rinomina(vecchio, nome.nome)
        except NomeNonTrovato as e:
            raise HTTPException(404, f"{vecchio} non è in rubrica") from e
        return ElencoNomi(nomi=rubrica.nomi())

    @app.delete("/rubrica/{nome}")
    def elimina_nome(nome: str) -> ElencoNomi:
        rubrica.elimina(nome)
        return ElencoNomi(nomi=rubrica.nomi())

    return app


def _ripartisci(richiesta: RichiestaCalcolo) -> Ripartizione:
    try:
        return ripartisci(richiesta)
    except AssegnazioniNonValide as e:
        raise HTTPException(422, str(e)) from e
