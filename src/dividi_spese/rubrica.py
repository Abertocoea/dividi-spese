"""Nomi usati di frequente, salvati in un file JSON nella cartella dati dell'utente."""
import json
from pathlib import Path


class NomeNonTrovato(KeyError):
    pass


class Rubrica:
    def __init__(self, cartella: Path) -> None:
        self._file = cartella / "rubrica.json"

    def nomi(self) -> list[str]:
        if not self._file.exists():
            return []
        return sorted(json.loads(self._file.read_text(encoding="utf-8")), key=str.casefold)

    def aggiungi(self, nome: str) -> None:
        nomi = self.nomi()
        if nome not in nomi:
            self._salva([*nomi, nome])

    def rinomina(self, vecchio: str, nuovo: str) -> None:
        nomi = self.nomi()
        if vecchio not in nomi:
            raise NomeNonTrovato(vecchio)
        self._salva([nuovo if n == vecchio else n for n in nomi])

    def elimina(self, nome: str) -> None:
        self._salva([n for n in self.nomi() if n != nome])

    def _salva(self, nomi: list[str]) -> None:
        self._file.parent.mkdir(parents=True, exist_ok=True)
        unici = sorted(set(nomi), key=str.casefold)
        self._file.write_text(json.dumps(unici, ensure_ascii=False, indent=2), encoding="utf-8")
