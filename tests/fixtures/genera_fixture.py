"""Genera copie CSV/Excel anonimizzate dell'ordine di riferimento (solo prodotti e importi)."""
import csv, re, sys
from decimal import Decimal
from openpyxl import Workbook
from openpyxl.styles import Font

testo, out = open(sys.argv[1]).read(), sys.argv[2]
riga = re.compile(r"^(\d+) (.+?)\s{2,}(\d+) ([A-Z]{2}) (\w+)\s+(\w+)\s+([A-Z])(\s+Foil)?\s+([\d,]+) EUR$")
prodotti = []
for l in testo.splitlines():
    m = riga.match(l.strip())
    if m:
        q, nome, num, lingua, cond, esp, rar, foil, prezzo = m.groups()
        dettagli = f"#{num} {lingua} {cond} {esp} {rar}" + (" Foil" if foil else "")
        prodotti.append((int(q), nome.strip(), dettagli, Decimal(prezzo.replace(",", "."))))
costi = [("Spese di spedizione", Decimal("11.95")), ("Tasse di servizio TRUST", Decimal("0.85"))]
sub = sum(q * p for q, _, _, p in prodotti); tot = sub + sum(c for _, c in costi)
assert (len(prodotti), sum(q for q, *_ in prodotti), sub, tot) == (17, 24, Decimal("169.20"), Decimal("182.00")), (len(prodotti), sub)
it = lambda d: f"{d:.2f}".replace(".", ",")

# 1) CSV italiano: separatore ";", virgola decimale, prezzo unitario, riepilogo in fondo
with open(f"{out}/ordine_it.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f, delimiter=";")
    w.writerow(["Quantità", "Prodotto", "Dettagli", "Prezzo unitario (EUR)"])
    for q, n, d, p in prodotti: w.writerow([q, n, d, it(p)])
    w.writerow([]); w.writerow(["", "Valore dell'oggetto", "", it(sub)])
    for n, c in costi: w.writerow(["", n, "", it(c)])
    w.writerow(["", "Totale", "", it(tot)])

# 2) CSV inglese: separatore ",", punto decimale, colonne in ordine diverso e SOLO totale di riga
with open(f"{out}/ordine_en.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["Item", "Details", "Qty", "Line total"])
    for q, n, d, p in prodotti: w.writerow([n, d, q, f"{q * p:.2f}"])
    w.writerow(["Subtotal", "", "", f"{sub:.2f}"])
    w.writerow(["Shipping", "", "", "11.95"]); w.writerow(["Service fee", "", "", "0.85"])
    w.writerow(["Total", "", "", f"{tot:.2f}"])

# 3) Excel con due fogli: prodotti (numeri veri) e riepilogo costi
wb = Workbook(); ws = wb.active; ws.title = "Prodotti"
ws.append(["Qtà", "Descrizione", "Dettagli", "Prezzo unitario", "Totale riga"])
for q, n, d, p in prodotti: ws.append([q, n, d, float(p), float(q * p)])
ws2 = wb.create_sheet("Riepilogo")
ws2.append(["Voce", "Importo"]); ws2.append(["Valore dell'oggetto", float(sub)])
for n, c in costi: ws2.append([n, float(c)])
ws2.append(["Totale", float(tot)])
for s in (ws, ws2):
    for c in s[1]: c.font = Font(bold=True)
    for col in ("D", "E", "B"):
        for c in s[col][1:]:
            if isinstance(c.value, float): c.number_format = '#,##0.00 "€"'
wb.save(f"{out}/ordine.xlsx")

# 4) Atteso, per i test
import json
json.dump({"righe": 17, "unita": 24, "subtotale_prodotti": 169.20, "costi_comuni": [11.95, 0.85], "totale": 182.00},
          open(f"{out}/ordine_atteso.json", "w"), indent=2)
print("ok", len(prodotti), sub, tot)
