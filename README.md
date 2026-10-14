# Dividi Spese

Web app locale per dividere un ordine online tra più persone. Carichi il PDF, uno screenshot, un CSV o un Excel dell'ordine; un modello AI locale (Ollama) estrae prodotti e costi comuni; assegni ogni prodotto a una persona e l'app calcola quanto deve pagare ciascuno, con un PDF di riepilogo da condividere.

Tutto gira sul tuo computer: nessun dato viene inviato a servizi esterni.

## Requisiti

- Python 3.12+
- [Ollama](https://ollama.com) avviato, con un modello con visione:

  ```
  ollama pull qwen3.5:9b-q4_K_M
  ```

## Avvio

```
python3 -m venv .venv
.venv/bin/pip install -e .
.venv/bin/dividi-spese
```

Si apre il browser su http://127.0.0.1:8765. La rubrica dei nomi è salvata in `~/.local/share/dividi-spese/`.

## Sviluppo

```
.venv/bin/pip install -e '.[dev]'
.venv/bin/pytest            # test veloci, Ollama sostituito da un finto
.venv/bin/pytest -m lento   # estrazione reale con Ollama sui file di esempio
.venv/bin/mypy
```

Per includere nel test lento anche PDF e screenshot di un ordine reale (esclusi da git), mettili come `ordine.pdf` / `ordine.png` in una cartella e indica `DIVIDI_SPESE_ESEMPI=<cartella>`. `DIVIDI_SPESE_MODELLO` sceglie il modello da provare.

La specifica completa è in [SPEC.md](SPEC.md).
