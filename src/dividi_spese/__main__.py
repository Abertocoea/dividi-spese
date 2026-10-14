"""Avvio: `dividi-spese` avvia il server su 127.0.0.1 e apre il browser."""
import os
import threading
import webbrowser
from pathlib import Path

import uvicorn

from .app import crea_app
from .ollama import EstrattoreOllama

PORTA = 8765


def cartella_dati() -> Path:
    base = os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share"
    return Path(base) / "dividi-spese"


def main() -> None:
    app = crea_app(estrattore=EstrattoreOllama(), cartella_dati=cartella_dati())
    url = f"http://127.0.0.1:{PORTA}"
    if not os.environ.get("DIVIDI_SPESE_NO_BROWSER"):
        threading.Timer(1.0, webbrowser.open, args=[url]).start()
    print(f"Dividi Spese su {url}")
    uvicorn.run(app, host="127.0.0.1", port=PORTA, log_level="warning")


if __name__ == "__main__":
    main()
