"""
converti.py - El Principe Garage
Converte il JSON esportato da Octoparse nel formato cars.json
usato dal sito.

USO:
  1. Esporta il task Octoparse come JSON
  2. Salva il file come octoparse_export.json nella stessa cartella
  3. Esegui: python converti.py
  4. Carica il cars.json generato su GitHub
"""

import json, re, sys, os
from datetime import datetime, timezone

INPUT  = "octoparse_export.json"
OUTPUT = "cars.json"

def clean(s):
    return (s or "").strip().replace("\n","").replace("\r","").strip()

def extract_id(url):
    m = re.search(r'-(\d+)\.htm', url or "")
    return m.group(1) if m else ""

def parse_date(raw):
    """Converte '27 Apr, 12:45' in '27 Apr', 'Ieri, 17:45' in 'Ieri' ecc."""
    raw = clean(raw)
    if not raw: return ""
    # Prende solo la parte data (prima della virgola o tutto)
    part = raw.split(",")[0].strip()
    # Normalizza "Oggi" e "Ieri"
    if part.lower() == "oggi": return "Oggi"
    if part.lower() == "ieri": return "Ieri"
    return part

def convert(input_file, output_file):
    print(f"Leggo: {input_file}")
    with open(input_file, encoding="utf-8") as f:
        data = json.load(f)

    # Octoparse può esportare lista diretta o oggetto con chiave "dataList"
    if isinstance(data, list):
        rows = data
    elif isinstance(data, dict):
        rows = data.get("dataList", data.get("data", []))
    else:
        print("Formato non riconosciuto")
        sys.exit(1)

    print(f"Righe trovate: {len(rows)}")

    cars = []
    for row in rows:
        url   = clean(row.get("Field",""))
        title = clean(row.get("Field1",""))
        if not url or not title:
            print(f"  SKIP riga senza url/titolo: {row}")
            continue

        car_id = extract_id(url)
        img    = clean(row.get("Image",""))
        # Upgrade qualità immagine: bigthumbs → large
        img = img.replace("bigthumbs-auto","large-auto").replace("thumbs-auto","large-auto")

        cars.append({
            "id":           car_id,
            "url":          url,
            "title":        title,
            "price":        clean(row.get("Price","")),
            "imageUrl":     img,
            "localImage":   "",          # vuoto: il sito usa imageUrl direttamente
            "publishDate":  parse_date(row.get("Title","")),
            "km":           clean(row.get("item_extra_data","")),
            "year":         clean(row.get("item_extra_data2","")),
            "fuel":         clean(row.get("item_extra_data3","")),
            "transmission": clean(row.get("item_extra_data4","")),
        })
        print(f"  OK: {title} | {clean(row.get('Price',''))} | img: {'SI' if img else 'NO'}")

    output = {
        "success": True,
        "updated": datetime.now(timezone.utc).isoformat(),
        "count":   len(cars),
        "cars":    cars,
    }
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\nSalvato: {output_file} ({len(cars)} auto)")
    print("Ora carica cars.json su GitHub — il sito si aggiorna automaticamente.")

if __name__ == "__main__":
    inp = sys.argv[1] if len(sys.argv) > 1 else INPUT
    out = sys.argv[2] if len(sys.argv) > 2 else OUTPUT
    if not os.path.exists(inp):
        print(f"File non trovato: {inp}")
        print(f"Uso: python converti.py [file_octoparse.json] [output.json]")
        sys.exit(1)
    convert(inp, out)
