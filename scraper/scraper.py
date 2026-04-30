"""
scraper.py - VERSIONE DEBUG
Dumpa la risposta completa di ScrapingBot per la pagina negozio
cosi vediamo esattamente cosa contiene e come estrarre gli URL.
"""

import json, os, urllib.request, base64
from datetime import datetime, timezone

ACCOUNTS = [
    ("SavYanmar94",  "Yl5MgMO0oULolQpbXSl4IOoz1"),
    ("Domi28",       "tEBA2RkLkIzi0I6mFn3yhE80D"),
    ("Genny23",      "TDQZbqp0jLJxcvRn8hAKCrDxx"),
    ("Nasoni23",     "aR50QSv23t5nLzS1GU2ofGCVA"),
    ("LamacMak92",   "18uZGwmI8rIPXBd0w3UyPQVPd"),
    ("Lidwef32",     "w6Ns04tg2aYcIEONc50h93UUF"),
]
SCRAPING_BOT_API = "http://api.scraping-bot.io/scrape/retail"
SHOP_URL  = "https://impresapiu.subito.it/shops/54233-el-principe-di-bavaro-biagio"
BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_FILE = os.path.join(BASE_DIR, "cars.json")
STATE_FILE= os.path.join(BASE_DIR, "scraper", "state.json")
DEBUG_FILE= os.path.join(BASE_DIR, "scraper", "debug_response.json")

def load_state():
    try:
        with open(STATE_FILE) as f: return json.load(f)
    except: return {"account_index": 0, "credits_used": {a[0]: 0 for a in ACCOUNTS}}

def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f: json.dump(state, f, indent=2)

def sbot_call(url, account, use_chrome=True):
    user, pwd = account
    auth = base64.b64encode(f"{user}:{pwd}".encode()).decode()
    payload = json.dumps({
        "url": url,
        "options": {
            "useChrome": use_chrome,
            "premiumProxy": True,
            "proxyCountry": "IT",
            "waitForNetworkRequests": use_chrome,
        }
    }).encode()
    req = urllib.request.Request(
        SCRAPING_BOT_API, data=payload, method="POST",
        headers={"Authorization": f"Basic {auth}", "Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode())

def scrape():
    print(f"\n{'='*60}")
    print(f"AVVIO DEBUG: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"{'='*60}\n")

    state = load_state()
    account = ACCOUNTS[state.get("account_index", 0)]
    print(f"Account: {account[0]}")
    print(f"URL: {SHOP_URL}\n")

    print("Chiamata ScrapingBot con useChrome=True...")
    try:
        resp = sbot_call(SHOP_URL, account, use_chrome=True)
        state["credits_used"][account[0]] = state["credits_used"].get(account[0], 0) + 25
        save_state(state)
    except Exception as e:
        print(f"ERRORE: {e}")
        return

    # Salva risposta completa per analisi
    with open(DEBUG_FILE, "w") as f:
        json.dump(resp, f, indent=2, ensure_ascii=False)
    print(f"Risposta salvata in debug_response.json")

    d = resp.get("data", resp)

    # Mostra tutti i campi disponibili
    print(f"\nCAMPI nella risposta:")
    for key, val in d.items():
        if isinstance(val, str):
            print(f"  {key}: (stringa, {len(val)} chars) → {val[:100]}")
        elif isinstance(val, list):
            print(f"  {key}: (lista, {len(val)} elementi)")
            if val and isinstance(val[0], dict):
                print(f"    Primo elemento: {list(val[0].keys())}")
                print(f"    Valore: {str(val[0])[:150]}")
            elif val:
                print(f"    Primo: {str(val[0])[:100]}")
        elif val is None:
            print(f"  {key}: null")
        else:
            print(f"  {key}: {val}")

    # Cerca URL Subito nell'HTML
    html = d.get("siteHtml","") or d.get("html","") or ""
    if html:
        import re
        urls = re.findall(r'https://www\.subito\.it/auto/[^\s"\'<>]+\.htm', html)
        urls = list(dict.fromkeys(urls))
        print(f"\nURL /auto/ trovati nell'HTML: {len(urls)}")
        for u in urls[:5]: print(f"  {u}")
    else:
        print("\nsiteHtml: vuoto o assente")

    # Cerca anche URL impresapiu
    if html:
        import re
        urls2 = re.findall(r'href=["\']([^"\']*subito[^"\']*)["\']', html)
        print(f"\nTutti gli href con 'subito': {len(urls2)}")
        for u in urls2[:10]: print(f"  {u}")

    print(f"\nCrediti {account[0]}: {state['credits_used'].get(account[0],0)}/500")
    print(f"\n{'='*60}")
    print("DEBUG COMPLETATO — controlla il log sopra e debug_response.json")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    scrape()
