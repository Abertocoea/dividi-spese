# Dividi Spese — Specifica

## Problem Statement

Quando faccio un ordine online insieme ad altre persone (per esempio un ordine di carte su Cardmarket con 24 articoli), devo capire quanto deve pagare ciascuno. Oggi lo faccio a mano: ricopio i prodotti dalla ricevuta, segno di chi è ciascuno, sommo gli importi e poi provo a dividere spedizione, commissioni e assicurazioni in modo equo. È lento, si sbaglia facilmente (soprattutto con righe da più unità o arrotondamenti che non tornano al centesimo) e alla fine non ho un documento chiaro da mandare agli altri.

Inoltre non voglio caricare le mie ricevute, con nomi e indirizzi, su servizi esterni.

## Solution

Una web app che gira sul mio computer. Carico il PDF, lo screenshot oppure un file CSV o Excel dell'ordine e un modello AI locale (Ollama, sulla mia GPU) ricostruisce l'elenco dei prodotti e dei costi comuni. L'app controlla che i totali estratti coincidano con quelli del documento. Io correggo eventuali errori, scelgo le persone dalla rubrica, assegno ogni prodotto (o singole unità) a una persona e scelgo se dividere i costi comuni in parti uguali o in proporzione alla spesa di ciascuno. Premendo "Calcola" vedo quanto deve pagare ognuno, con la somma che torna esattamente al totale dell'ordine, e posso esportare un unico PDF di riepilogo, con l'elenco dei prodotti di ciascuno da far confermare ai diretti interessati. Nessun dato lascia il computer.

## User Stories

### Caricamento
1. Come utente, voglio caricare un PDF dell'ordine trascinandolo nella pagina, così da iniziare senza passaggi intermedi.
2. Come utente, voglio caricare uno screenshot (PNG, JPG, WebP) del carrello, così da poter dividere anche ordini di cui non ho il PDF.
3. Come utente, voglio caricare un file CSV o Excel (.xlsx) con l'elenco dei prodotti, così da usare gli export dei siti e i fogli che preparo io.
4. Come utente, voglio che un file Excel con più fogli venga letto per intero, così da non perdere prodotti che stanno su un foglio diverso dal primo.
5. Come utente, voglio scegliere il file anche con un normale selettore di file, così da non dipendere dal drag & drop.
6. Come utente, voglio vedere un'anteprima del documento accanto ai dati estratti (per CSV ed Excel, la tabella originale), così da confrontarli a colpo d'occhio.
7. Come utente, voglio un messaggio chiaro se carico un formato non supportato, così da sapere cosa caricare.

### Estrazione con AI locale
8. Come utente, voglio che l'app estragga automaticamente le righe prodotto con quantità, nome, prezzo unitario e dettagli, così da non doverle ricopiare.
9. Come utente, voglio che l'app riconosca separatamente i costi comuni (spedizione, commissioni, tasse di servizio, polizze, assicurazioni), così da non assegnarli per errore a una persona.
10. Come utente, voglio che l'app legga anche il subtotale e il totale dichiarati nel documento, così da poter verificare l'estrazione.
11. Come utente, voglio che l'estrazione avvenga interamente sul mio computer, così da non condividere i miei dati con servizi esterni.
12. Come utente, voglio vedere un indicatore di avanzamento durante l'estrazione, così da sapere che l'app sta lavorando.
13. Come utente, voglio che l'estrazione di un ordine di una pagina richieda meno di un minuto, così da usare l'app senza attese lunghe.
14. Come utente, voglio che i PDF con testo selezionabile vengano letti come testo, così da avere il risultato più affidabile.
15. Come utente, voglio che l'AI riconosca da sola le colonne di un CSV o Excel (nome, quantità, prezzo) anche se hanno intestazioni diverse da file a file, così da non doverle mappare a mano.
16. Come utente, voglio che nei CSV vengano riconosciuti separatore (virgola o punto e virgola) e formato dei numeri (1.234,56 o 1,234.56), così da importare file italiani e stranieri senza errori.
17. Come utente, voglio che i PDF scansionati vengano comunque letti tramite il modello con visione, così da non essere bloccato da ricevute senza testo.
18. Come utente, voglio che i costi comuni da 0 € vengano scartati, così da non avere righe inutili.
19. Come utente, voglio scegliere il modello Ollama da usare tra quelli installati con capacità di visione, così da poter provare un modello migliore.
20. Come utente, voglio un messaggio chiaro con il comando da eseguire se Ollama non è avviato o il modello non è installato, così da risolvere il problema da solo.

### Verifica e correzione
21. Come utente, voglio un avviso evidente quando la somma dei prodotti non coincide con il subtotale dichiarato, così da accorgermi degli errori del modello.
22. Come utente, voglio un avviso quando subtotale più costi comuni non coincide con il totale dichiarato, così da sapere che manca o avanza qualcosa.
23. Come utente, voglio vedere di quanto differiscono i totali, così da capire subito dove cercare l'errore.
24. Come utente, voglio che il controllo dei totali si aggiorni a ogni mia modifica, così da sapere quando i dati sono di nuovo corretti.
25. Come utente, voglio modificare nome, quantità, prezzo e dettagli di una riga, così da correggere gli errori di estrazione.
26. Come utente, voglio aggiungere una riga mancante a mano, così da completare l'elenco.
27. Come utente, voglio eliminare una riga, così da togliere voci estratte per sbaglio.
28. Come utente, voglio spostare una riga da "prodotto" a "costo comune" e viceversa, così da correggere una classificazione sbagliata.
29. Come utente, voglio premere "Riprova estrazione", eventualmente con un altro modello, così da non dover correggere tutto a mano.
30. Come utente, voglio poter procedere al calcolo anche se i totali non tornano, così da non essere bloccato da piccole differenze che accetto.
31. Come utente, voglio che gli sconti o coupon presenti nell'ordine siano trattati come costi comuni negativi, così da distribuire anche il risparmio.

### Persone e rubrica
32. Come utente, voglio scegliere le persone dell'ordine dalla rubrica dei nomi usati di frequente, così da non riscriverli ogni volta.
33. Come utente, voglio aggiungere una persona nuova scrivendone il nome, così da includere chi non è ancora in rubrica.
34. Come utente, voglio che i nomi nuovi vengano salvati automaticamente in rubrica, così da ritrovarli al prossimo ordine.
35. Come utente, voglio rinominare o eliminare un nome dalla rubrica, così da tenerla in ordine.
36. Come utente, voglio che la rubrica resti salvata anche dopo aver chiuso e riaperto l'app, così da non perderla.
37. Come utente, voglio che ogni persona abbia un colore, così da riconoscere a colpo d'occhio le assegnazioni nella tabella.
38. Come utente, voglio togliere una persona dall'ordine corrente, così che i suoi prodotti tornino da assegnare.

### Assegnazione
39. Come utente, voglio assegnare una riga prodotto a una persona con un clic, così da taggare velocemente.
40. Come utente, voglio dividere le unità di una riga con quantità maggiore di 1 tra più persone (es. 4× → 2 a Marco e 2 ad Anna), così da gestire acquisti condivisi della stessa carta.
41. Come utente, voglio selezionare più righe e assegnarle tutte alla stessa persona, così da risparmiare tempo sugli ordini lunghi.
42. Come utente, voglio vedere quante unità restano da assegnare, così da sapere quanto manca.
43. Come utente, voglio cambiare l'assegnazione di una riga in qualsiasi momento, così da correggere un errore.
44. Come utente, voglio vedere il subtotale parziale di ciascuna persona mentre assegno, così da avere un'idea immediata.

### Calcolo
45. Come utente, voglio scegliere se dividere i costi comuni in proporzione alla spesa in prodotti di ciascuno oppure in parti uguali, così da applicare il criterio concordato con gli altri.
46. Come utente, voglio che il criterio proporzionale sia quello predefinito, così da avere la divisione più equa senza pensarci.
47. Come utente, voglio che nella divisione in parti uguali contino solo le persone con almeno un prodotto, così che chi non ha comprato nulla non paghi la spedizione.
48. Come utente, voglio che il pulsante "Calcola" sia attivo solo quando tutte le unità sono assegnate, così da non ottenere un risultato incompleto.
49. Come utente, voglio che gli importi siano arrotondati al centesimo e che la loro somma sia esattamente il totale dell'ordine, così che nessuno debba coprire un centesimo mancante.
50. Come utente, voglio vedere per ogni persona subtotale prodotti, quota dei costi comuni e totale da pagare, così da capire da dove viene la cifra.
51. Come utente, voglio cambiare criterio e vedere subito il nuovo risultato, così da confrontare le due divisioni.

### PDF di riepilogo
52. Come utente, voglio esportare un unico PDF con il riepilogo, così da mandarlo agli altri partecipanti.
53. Come utente, voglio che il PDF contenga numero e data dell'ordine, venditore e totale, così da identificare l'ordine.
54. Come utente, voglio una tabella con persona, subtotale, quota dei costi comuni e totale, così che ognuno trovi subito la propria cifra.
55. Come utente, voglio nel PDF un recap per ogni persona con l'elenco dei prodotti che ha preso (quantità, nome, dettagli, prezzo unitario e totale di riga), così da avere una seconda conferma dai diretti interessati.
56. Come partecipante all'ordine, voglio che il mio recap mostri anche subtotale prodotti, quota dei costi comuni e totale da pagare, così da verificare la mia cifra senza leggere il resto del documento.
57. Come utente, voglio che ogni recap inizi su una nuova pagina, così da poter mandare a ciascuno solo la sua pagina (screenshot o stampa) pur avendo un unico PDF.
58. Come partecipante all'ordine, voglio che nel recap le righe divise con altre persone indichino quante unità sono mie su quante totali (es. "2 di 4"), così da capire le assegnazioni condivise.
59. Come utente, voglio che il PDF elenchi i costi comuni e il criterio di ripartizione usato, così che la divisione sia trasparente.
60. Come utente, voglio che il file abbia un nome con numero e data dell'ordine, così da ritrovarlo facilmente.

### Generale
61. Come utente, voglio l'interfaccia in italiano e gli importi in formato italiano (1.234,56 €), così da leggerli senza ambiguità.
62. Come utente, voglio avviare l'app con un solo comando che apre il browser, così da usarla senza configurazioni.
63. Come utente, voglio che l'app sia raggiungibile solo dal mio computer, così che nessuno in rete possa vedere i miei ordini.
## Implementation Decisions

### Architettura
- **Web app locale**: backend Python con FastAPI, frontend web servito dallo stesso backend. Il server ascolta solo su `127.0.0.1`. Un unico comando avvia il server e apre il browser.
- **Nessun servizio esterno**: l'unica dipendenza di rete è Ollama in locale (`localhost:11434`).

### Moduli
- **Ripartizione** (modulo puro, senza dipendenze da UI, AI o HTTP). Riceve prodotti, costi comuni, assegnazioni e criterio; restituisce per ogni persona subtotale, quota dei costi comuni e totale. Contiene le regole di calcolo e di arrotondamento.
- **Estrazione**. Interfaccia `Estrattore` che riceve un documento (byte + tipo) e restituisce un `OrdineEstratto`. Implementazione predefinita basata su Ollama. Al suo interno:
  - sceglie il percorso in base al documento: PDF con testo → testo estratto con PyMuPDF mantenendo il layout; PDF scansionato → pagine renderizzate in PNG a 150 dpi; immagine → inviata così com'è; CSV/Excel → letti con pandas (openpyxl per `.xlsx`, rilevamento automatico di separatore e codifica per CSV), tutti i fogli convertiti in tabella testuale (un'intestazione `## Sheet: <nome>` per foglio, celle separate da ` | `, importi formattati come nella cella così da conservare il simbolo di valuta) e inviati sul **percorso testo**, così che sia il modello a riconoscere colonne, righe prodotto e costi comuni;
  - chiama `/api/chat` di Ollama con il system prompt in inglese (vedi sotto), il documento nel messaggio utente, `format` = JSON Schema (structured outputs), `temperature: 0`, `num_ctx: 16384` (il default di 4096 token non basta per ordini lunghi o Excel grandi), thinking disattivato;
  - **normalizza** l'output in modo deterministico: scarta i costi comuni da 0 €; ricava il prezzo unitario da `totale_riga / quantita` quando manca; se Σ quantità × prezzo unitario non coincide con il subtotale dichiarato ma Σ prezzi sì, i prezzi erano totali di riga e vengono divisi per la quantità; la valuta mancante prende il valore predefinito (EUR); un costo di `tipo` `sconto` con importo positivo diventa `altro`.
  - Il modello copia, il codice calcola: nessun calcolo è affidato al modello.
- **Controllo di coerenza**: funzione pura che confronta i dati (estratti o corretti) con i totali dichiarati e restituisce le differenze.
- **Rubrica**: persistenza dei nomi in un file locale nella cartella dati dell'utente (JSON o SQLite).
- **Riepilogo PDF**: genera un unico documento (WeasyPrint o ReportLab) a partire dall'ordine e dal risultato della ripartizione. Struttura:
  1. pagina di sintesi: dati dell'ordine, tabella persona | subtotale | quota costi comuni | totale, elenco dei costi comuni e criterio di ripartizione;
  2. un **recap per persona**, ognuno su una nuova pagina: nome, elenco dei prodotti presi (quantità, nome, dettagli, prezzo unitario, totale di riga; per le righe condivise "N di M" unità), subtotale, quota dei costi comuni, totale da pagare, riferimento all'ordine.
- **API HTTP**: unico punto di ingresso usato dal frontend; compone i moduli sopra.

### Contratti API
- `POST /estrai`: file caricato (+ modello opzionale) → `OrdineEstratto` + esito del controllo di coerenza. Errori distinti per: formato non supportato (accettati: PDF, PNG, JPG, WebP, CSV, XLSX), file CSV/Excel illeggibile, Ollama non raggiungibile, modello non installato (con il comando `ollama pull …` da suggerire).
- `POST /verifica`: ordine (eventualmente corretto) → esito del controllo di coerenza.
- `POST /calcola`: ordine + assegnazioni + criterio → ripartizione per persona. Rifiuta la richiesta se ci sono unità non assegnate o assegnate in eccesso.
- `POST /pdf`: ordine + assegnazioni + criterio + metadati → file PDF.
- `GET /rubrica`, `POST /rubrica`, `PUT /rubrica/{nome}`, `DELETE /rubrica/{nome}`.
- `GET /modelli`: modelli Ollama installati con capacità `vision`.

Lo stato dell'ordine in lavorazione vive nel frontend; il backend non ha sessioni.

### Forma dei dati estratti
Output del modello, validato con le prove su PDF, immagine, CSV ed Excel:

```json
{
  "valuta": "EUR",
  "ordine": { "numero": "1000000001", "data": "2026-10-12", "venditore": "Venditore Esempio" },
  "prodotti": [
    { "nome": "Negazione Ostinata", "quantita": 3, "dettagli": "EN NM KTK U",
      "prezzo_unitario": 2.50, "totale_riga": null }
  ],
  "costi_comuni": [
    { "descrizione": "Spese di spedizione", "importo": 11.95, "tipo": "spedizione" },
    { "descrizione": "Tasse di servizio TRUST", "importo": 0.85, "tipo": "commissione" }
  ],
  "totali_dichiarati": { "subtotale_prodotti": 169.20, "totale": 182.00 }
}
```

- `valuta`, i campi di `ordine`, `prezzo_unitario`, `totale_riga` e i `totali_dichiarati` possono essere `null`.
- `tipo` del costo comune: `spedizione`, `commissione`, `assicurazione`, `sconto`, `altro`.
- Dopo la normalizzazione ogni prodotto ha sempre un prezzo unitario: è la forma dell'`OrdineEstratto` restituito dall'API.

### System prompt
In inglese, perché i modelli piccoli seguono meglio istruzioni in inglese. Le chiavi JSON restano in italiano come nel resto del dominio. Testo validato nelle prove:

```text
You extract structured data from a purchase order, receipt or shopping cart. The input is the text of a PDF, a table converted from a CSV/Excel file, or an image.

Copy values exactly as they appear in the document. Never calculate, never invent.

Rules:
- "prodotti": one entry per product line, in document order. Never merge or split lines.
  - "quantita": the number of units on that line (integer, 1 if not shown).
  - "nome": the product name only, without quantity or price.
  - "dettagli": other attributes on the line (language, condition, edition, size, color, foil...), or "" if none.
  - "prezzo_unitario": the price of one unit, if the document shows it. Otherwise null.
  - "totale_riga": the line total, if the document shows it as a separate value or as the only price of a line labelled as a total (e.g. "Line total", "Totale riga"). Otherwise null.
  - If a line has a single price column with no label saying it is a total, it is the unit price.
- "totali_dichiarati": the totals printed in the document. "subtotale_prodotti" is the value of the items before charges (e.g. "Subtotal", "Valore dell'oggetto", "Items"); "totale" is the grand total paid (e.g. "Total", "Totale"). null if not shown.
- "costi_comuni": order-level charges added on top of the items: shipping, service fees, taxes, commissions, insurance. Discounts and coupons have a NEGATIVE "importo". Skip charges of 0.
  - "tipo": one of "spedizione", "commissione", "assicurazione", "sconto", "altro".
  - Subtotals and totals are NEVER charges: rows like "Subtotal", "Valore dell'oggetto", "Total", "Totale" go only in "totali_dichiarati".
- "ordine": order number, date (YYYY-MM-DD) and seller, or null if not shown.
- "valuta": the ISO currency code only if the document shows a currency (symbol, code or column header). Otherwise null.
- For tables, identify columns by their meaning, not their position; headers may be in any language. Summary rows usually come after the product rows.
- Numbers are plain decimals with a dot ("1.234,56" becomes 1234.56).
```

Un'**assegnazione** lega una riga prodotto a una persona per un certo numero di unità; la somma delle unità assegnate di una riga deve essere uguale alla sua quantità.

### Regole di calcolo
- `subtotale_p = Σ (unità assegnate a p × prezzo unitario)`
- **Proporzionale** (predefinito): `costi_comuni_p = Σ costi comuni × subtotale_p / Σ subtotali`
- **Parti uguali**: `costi_comuni_p = Σ costi comuni / numero di persone con almeno un'unità`
- `totale_p = subtotale_p + costi_comuni_p`
- Gli importi si gestiscono in **centesimi interi** (o `Decimal`), mai in float.
- **Arrotondamento** al centesimo con il metodo del resto maggiore: la somma dei totali è esattamente subtotale + costi comuni.
- Sconti = costi comuni negativi, ripartiti con lo stesso criterio.

Esempio di riferimento (costi comuni 12,80 €; Marco 100,00 €, Anna 69,20 €):
- proporzionale → Marco 107,57 €, Anna 74,43 €
- parti uguali → Marco 106,40 €, Anna 75,60 €

### Modello AI
Prove del 14/10/2026 su RTX 3060 12 GB. "Corretto" = 17 righe, 24 unità, subtotale 169,20 €, costi comuni 11,95 € + 0,85 €, totale 182,00 €.

Prima tornata, prompt minimo senza system prompt:

| Modello | Dal testo | Dall'immagine |
|---|---|---|
| `qwen3.5` 4B (variante abliterated) | ✅ corretto (22 s) | ✅ corretto (16 s), con un costo spurio da 0 € |
| `qwen3.5:9b-q4_K_M` | ✅ corretto, 2 prove su 2 (~25 s) | ✅ corretto, 2 prove su 2 (~26 s) |
| `gemma4` e2b | ✅ corretto (28 s) | ❌ quantità errate, subtotale scambiato per costo |
| `gemma-4` e4b (abliterated) | non provato | ❌ quantità perse, totale scambiato per costo |

Seconda tornata, `qwen3.5:9b-q4_K_M` con system prompt e schema definitivi, contesto 16384:

| Formato | Risultato |
|---|---|
| PDF (testo) | ✅ corretto (~30 s) |
| Screenshot | ✅ corretto (~32 s) |
| CSV italiano (`;`, virgola decimale, prezzo unitario) | ✅ corretto |
| CSV inglese (`,`, solo totale di riga, nessuna valuta) | ✅ corretto **grazie alla normalizzazione**: il modello mette il totale di riga in `prezzo_unitario` |
| Excel a due fogli | ✅ corretto |

Stessa tornata con `qwen3.5:4b-q4_K_M`: importi **corretti su tutti e cinque i formati** (~22 s ciascuno, 3,6 GB di VRAM), anche il CSV inglese senza bisogno della normalizzazione. Classifica però in modo incoerente la tassa di servizio da 0,85 € (`altro`, `commissione` o `sconto` a seconda del formato), mentre il 9B la classifica sempre come `commissione`.

Lezioni dalle prove, già incorporate in prompt e normalizzazione:
- se il prompt chiede al modello di dividere il totale di riga per la quantità, il modello divide anche prezzi che erano già unitari (subtotale 130,30 € invece di 169,20 €);
- nelle tabelle le righe di riepilogo ("Valore dell'oggetto", "Subtotal") venivano prese per costi comuni finché il prompt non lo ha escluso esplicitamente;
- senza una regola esplicita il modello inventa la valuta (`USD` per un CSV senza valuta);
- il 9B occupa 5,6 GB di VRAM, interamente su GPU;
- se un altro modello è ancora in memoria, Ollama carica il nuovo in parte sulla CPU e l'estrazione passa da ~22 s a 90-130 s (osservato con il 4B caricato mentre il 9B era ancora attivo).

Modello predefinito: **`qwen3.5:9b-q4_K_M`**: gli importi sono corretti come con il 4B, ma classifica i costi in modo coerente, e costa solo ~8 s in più per estrazione. Il 4B resta l'alternativa veloce, selezionabile dalle impostazioni.

Gestione della memoria GPU: quando cambia modello, l'app scarica quello precedente (`keep_alive: 0`) prima di caricare il nuovo. Dopo il caricamento controlla con `/api/ps` che il modello sia interamente su GPU e, in caso contrario, mostra un avviso sulla lentezza prevista.

### Interfaccia
- Layout a due colonne: anteprima del documento a sinistra, tabella delle righe a destra; su schermi stretti le colonne vanno una sotto l'altra.
- Persone come etichette colorate; assegnazione per riga, divisione delle unità per righe con quantità > 1, selezione multipla.
- Banner del controllo di coerenza sempre visibile, con le differenze.
- Selettore del criterio di ripartizione accanto al pulsante "Calcola".

## Testing Decisions

- **Cosa è un buon test**: verifica il comportamento osservabile dall'esterno (richiesta HTTP → risposta), non come è implementato. I test non devono rompersi se si riorganizzano i moduli interni.
- **Un solo punto di test: l'API HTTP**, chiamata con il client di test di FastAPI. Ollama è sostituito da un **`Estrattore` finto** che restituisce un `OrdineEstratto` prefissato, iniettato tramite le dipendenze di FastAPI. La rubrica usa una cartella temporanea.
- Comportamenti da coprire attraverso l'API:
  - **Estrazione**: formato non supportato; Ollama non raggiungibile; modello mancante; esito del controllo di coerenza (totali corretti, subtotale sbagliato, totale sbagliato, differenze riportate); scarto dei costi da 0 €.
  - **Calcolo**: entrambi i criteri sull'esempio di riferimento; somma esatta al centesimo in casi con resti (es. 10,00 € di costi tra 3 persone); unità divise tra più persone; persone senza prodotti escluse dalle parti uguali; sconti negativi; rifiuto con unità non assegnate o assegnate in eccesso.
  - **Rubrica**: aggiunta, rinomina, eliminazione, persistenza tra un'istanza e l'altra dell'app.
  - **Estrazione da CSV/Excel**: con l'`Estrattore` finto si verifica che il file venga accettato e convertito; la lettura reale (separatore `;` e numeri all'italiana, Excel con più fogli, file corrotto) si testa attraverso l'API con i file di esempio anonimizzati.
  - **Normalizzazione**: con l'`Estrattore` finto che restituisce output "grezzi" del modello si verifica attraverso l'API: costi da 0 € scartati, prezzo unitario ricavato da `totale_riga`, totali di riga messi per errore in `prezzo_unitario` corretti grazie al subtotale dichiarato, valuta mancante → EUR.
  - **PDF**: la risposta è un PDF valido; il testo estratto contiene la sintesi (nomi, totali per persona, criterio usato) e, per ogni persona, un recap su una pagina propria con tutti e soli i suoi prodotti, compresa l'indicazione "N di M" per le righe condivise.
- **Test lento opzionale** (escluso dalla suite normale, attivato con un marker): estrazione reale con Ollama su PDF, screenshot, i due CSV e l'Excel di riferimento; deve restituire 17 righe, 24 unità, subtotale 169,20 €, costi comuni 11,95 € + 0,85 €, totale 182,00 €. Serve anche per confrontare i modelli.
- **File di esempio** in `tests/fixtures/` (anonimizzati: solo prodotti e importi, nessun nome, indirizzo o numero d'ordine): `ordine_it.csv`, `ordine_en.csv`, `ordine.xlsx` e `ordine_atteso.json` con i valori attesi. Il PDF e lo screenshot reali restano fuori da git; il test lento li cerca in una cartella locale indicata da variabile d'ambiente e si salta se mancano. Lo script che genera le copie è in `tests/fixtures/`.
- **Prior art**: il progetto è nuovo, non ci sono test esistenti. Strumenti: pytest e il client di test di FastAPI.
- L'interfaccia non ha test automatici in v1.

## Out of Scope

- Più documenti nello stesso calcolo.
- Gestione di pagamenti o saldi tra persone nel tempo (stile Splitwise).
- Conversione tra valute.
- Account utente, hosting online, accesso da altri dispositivi in rete.
- Modelli AI in cloud.
- Salvataggio e riapertura di un ordine in lavorazione (possibile v2).
- Test automatici dell'interfaccia nel browser.

## Further Notes

- Il PDF di riferimento è un ordine Cardmarket reale (1 pagina, 17 righe, 24 unità). Contiene nomi e indirizzi reali, quindi è **escluso da git** (`.gitignore`). Per i test nel repository serve una versione anonimizzata con gli stessi prodotti e importi.
- I modelli Gemma hanno restituito dati sbagliati senza segnalare errori: il controllo di coerenza è la garanzia principale sulla qualità dell'estrazione, non un extra.
- Il progetto non è un repository git e non ha un issue tracker: questa spec vive in `SPEC.md`.
