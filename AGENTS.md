# Dividi Spese

Web app locale che estrae i prodotti da un ordine (PDF o screenshot) con un modello Ollama, li assegna a persone e divide il totale. Specifica completa in `SPEC.md`.

## Comandi

- Installazione: `python3 -m venv .venv && .venv/bin/pip install -e '.[dev]'`
- Test veloci: `.venv/bin/pytest` (Ollama sostituito da `EstrattoreFinto` in `tests/conftest.py`)
- Test lenti con Ollama reale: `.venv/bin/pytest -m lento` (vedi `README.md` per i file privati)
- Typecheck: `.venv/bin/mypy`
- Avvio: `.venv/bin/dividi-spese`

I test passano solo dall'API HTTP (`crea_app`): non testare i moduli interni direttamente.

## Dati personali

Gli ordini reali contengono nomi e indirizzi: non vanno mai committati (sono esclusi da `.gitignore`). Nei test e negli esempi usare solo dati anonimizzati.

## Agent skills

### Issue tracker

Issue e specifiche vivono nelle GitHub Issues di questo repository, gestite con la CLI `gh`. See `docs/agents/issue-tracker.md`.

### Triage labels

Le cinque etichette predefinite: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: un `GLOSSARY.md` e `docs/adr/` nella radice. See `docs/agents/domain.md`.
