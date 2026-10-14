"""Estrattore che usa un modello locale tramite l'API HTTP di Ollama."""
import base64
import json
from importlib.resources import files
from typing import Any

from typing import get_args

import httpx

from .estrazione import MODELLO_PREDEFINITO, ContenutoDocumento, ErroreOllama, ModelloNonInstallato, OllamaNonRaggiungibile
from .modelli import TipoCosto

SYSTEM_PROMPT = files(__package__).joinpath("prompt_estrazione.txt").read_text(encoding="utf-8")

_testo = {"type": "string"}
_testo_o_null = {"type": ["string", "null"]}
_numero_o_null = {"type": ["number", "null"]}
SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "valuta": _testo_o_null,
        "ordine": {
            "type": "object",
            "properties": {"numero": _testo_o_null, "data": _testo_o_null, "venditore": _testo_o_null},
            "required": ["numero", "data", "venditore"],
        },
        "prodotti": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "nome": _testo,
                    "quantita": {"type": "integer"},
                    "dettagli": _testo,
                    "prezzo_unitario": _numero_o_null,
                    "totale_riga": _numero_o_null,
                },
                "required": ["nome", "quantita", "dettagli", "prezzo_unitario", "totale_riga"],
            },
        },
        "costi_comuni": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "descrizione": _testo,
                    "importo": {"type": "number"},
                    "tipo": {"enum": list(get_args(TipoCosto))},
                },
                "required": ["descrizione", "importo", "tipo"],
            },
        },
        "totali_dichiarati": {
            "type": "object",
            "properties": {"subtotale_prodotti": _numero_o_null, "totale": _numero_o_null},
            "required": ["subtotale_prodotti", "totale"],
        },
    },
    "required": ["valuta", "ordine", "prodotti", "costi_comuni", "totali_dichiarati"],
}

# Il contesto predefinito di Ollama (4096 token) non basta per ordini lunghi o Excel grandi.
NUM_CTX = 16384
AVVISO_CPU = "Il modello {} non sta tutto nella memoria della GPU: l'estrazione sarà lenta. Chiudi altri programmi che usano la GPU o scegli un modello più piccolo."


class EstrattoreOllama:
    def __init__(self, url: str = "http://localhost:11434", timeout: float = 600) -> None:
        self._http = httpx.Client(base_url=url, timeout=timeout)

    def estrai(self, contenuto: ContenutoDocumento, modello: str | None) -> tuple[dict[str, Any], list[str]]:
        modello = modello or MODELLO_PREDEFINITO
        if modello not in self._installati():
            raise ModelloNonInstallato(modello)
        self._scarica_altri_modelli(modello)

        messaggio: dict[str, Any] = {"role": "user"}
        if contenuto.testo is not None:
            messaggio["content"] = contenuto.testo
        else:
            messaggio["content"] = "Extract the order in the image." if len(contenuto.immagini) == 1 else "Extract the order in the images (one per page)."
            messaggio["images"] = [base64.b64encode(i).decode() for i in contenuto.immagini]

        risposta = self._richiesta("POST", "/api/chat", json={
            "model": modello,
            "messages": [{"role": "system", "content": SYSTEM_PROMPT}, messaggio],
            "format": SCHEMA,
            "stream": False,
            "think": False,
            "options": {"temperature": 0, "num_ctx": NUM_CTX},
        })
        grezzo: dict[str, Any] = json.loads(risposta["message"]["content"])
        return grezzo, self._avvisi(modello)

    def modelli(self) -> list[str]:
        con_visione = [
            m for m in self._installati()
            if "vision" in self._richiesta("POST", "/api/show", json={"model": m}).get("capabilities", [])
        ]
        return sorted(con_visione, key=lambda m: (m != MODELLO_PREDEFINITO, m))

    def _installati(self) -> list[str]:
        return [m["name"] for m in self._richiesta("GET", "/api/tags").get("models", [])]

    def _scarica_altri_modelli(self, modello: str) -> None:
        """Due modelli in memoria insieme costringono Ollama a spostarne parte sulla CPU (~5 volte più lento)."""
        for caricato in self._richiesta("GET", "/api/ps").get("models", []):
            if caricato.get("name") != modello:
                self._richiesta("POST", "/api/generate", json={"model": caricato["name"], "keep_alive": 0})

    def _avvisi(self, modello: str) -> list[str]:
        for m in self._richiesta("GET", "/api/ps").get("models", []):
            if m.get("name") == modello and m.get("size_vram", 0) < m.get("size", 0):
                return [AVVISO_CPU.format(modello)]
        return []

    def _richiesta(self, metodo: str, percorso: str, **kwargs: Any) -> dict[str, Any]:
        try:
            r = self._http.request(metodo, percorso, **kwargs)
        except httpx.TimeoutException as e:
            raise ErroreOllama(f"Ollama non ha risposto entro {self._http.timeout.read:.0f} s") from e
        except httpx.TransportError as e:
            raise OllamaNonRaggiungibile() from e
        if r.is_error:
            try:
                dettaglio = r.json().get("error", r.text)
            except ValueError:
                dettaglio = r.text
            raise ErroreOllama(f"Errore di Ollama: {dettaglio}")
        dati: dict[str, Any] = r.json()
        return dati
