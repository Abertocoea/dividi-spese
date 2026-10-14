# Dividi Spese

Web app locale che estrae i prodotti da un ordine (PDF o screenshot) con un modello Ollama, li assegna a persone e divide il totale. Specifica completa in `SPEC.md`.

## Dati personali

Gli ordini reali contengono nomi e indirizzi: non vanno mai committati (sono esclusi da `.gitignore`). Nei test e negli esempi usare solo dati anonimizzati.

## Agent skills

### Issue tracker

Issue e specifiche vivono nelle GitHub Issues di questo repository, gestite con la CLI `gh`. See `docs/agents/issue-tracker.md`.

### Triage labels

Le cinque etichette predefinite: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: un `GLOSSARY.md` e `docs/adr/` nella radice. See `docs/agents/domain.md`.
