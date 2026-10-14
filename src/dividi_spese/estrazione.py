"""Estrazione di un ordine da un documento tramite un modello AI."""
from dataclasses import dataclass, field
from typing import Any, Protocol

MODELLO_PREDEFINITO = "qwen3.5:9b-q4_K_M"


@dataclass
class ContenutoDocumento:
    """Ciò che viene inviato al modello: testo (PDF con testo, CSV, Excel) oppure immagini PNG/JPG."""

    testo: str | None = None
    immagini: list[bytes] = field(default_factory=list)


class OllamaNonRaggiungibile(RuntimeError):
    def __init__(self) -> None:
        super().__init__("Ollama non è raggiungibile su localhost:11434. Avvialo con: ollama serve")


class ErroreOllama(RuntimeError):
    """Ollama ha risposto con un errore (es. memoria insufficiente) o non ha risposto in tempo."""


class ModelloNonInstallato(RuntimeError):
    def __init__(self, modello: str) -> None:
        super().__init__(f"Il modello {modello} non è installato. Esegui: ollama pull {modello}")
        self.modello = modello


class Estrattore(Protocol):
    def estrai(self, contenuto: ContenutoDocumento, modello: str | None) -> tuple[dict[str, Any], list[str]]:
        """Restituisce l'output grezzo del modello e gli eventuali avvisi (es. modello non tutto su GPU)."""
        ...

    def modelli(self) -> list[str]:
        """Modelli installati con capacità di visione."""
        ...
