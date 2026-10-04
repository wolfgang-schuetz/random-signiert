#!/usr/bin/env python3
"""Ruft alle `minutenabstand` Minuten `anzahl_zahlen` signierte Zufallszahlen
von Random.org ab (generateSignedIntegers) und protokolliert sie.

Ausgabe:
  <ordner>/<name_datei_protokoll>   komplettes CSV-Protokoll
  <ordner>/daten/JJJJ-MM-TT.jsonl   Rohantworten (zum Verifizieren der Signatur)
"""
import csv, json, sys, time, urllib.request
from datetime import datetime, timedelta
from pathlib import Path

CONFIG = Path(__file__).with_name("config_man6_signiert.txt")
URL = "https://api.random.org/json-rpc/4/invoke"
SPALTEN = ["ID", "Datum", "Zeit", "SerialNumber", "CompletionTime",
           "Zufallszahlen", "Signatur", "HashedApiKey"]


def lade_config():
    cfg = {}
    for zeile in CONFIG.read_text(encoding="utf-8").splitlines():
        if "=" in zeile and not zeile.lstrip().startswith("#"):
            k, v = zeile.split("=", 1)
            cfg[k.strip()] = v.strip()
    return cfg


def log(msg):
    print(f"{datetime.now():%Y-%m-%d %H:%M:%S} {msg}", flush=True)


def naechster_slot(abstand):
    """Zeitpunkt des nächsten Abrufs: gezählt ab Ortszeit-Mitternacht (00:00, 00:08 …).
    Um Mitternacht beginnt die Zählung neu, auch an Tagen mit Zeitumstellung."""
    heute = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    k = int((time.time() - heute.timestamp()) // abstand) + 1
    morgen = (heute + timedelta(days=1)).timestamp()
    return min(heute.timestamp() + k * abstand, morgen)


def abrufen(cfg, n):
    body = {"jsonrpc": "2.0", "id": int(time.time()), "method": "generateSignedIntegers",
            "params": {"apiKey": cfg["api"], "n": n,
                       "min": int(cfg["intervall_beginn"]), "max": int(cfg["intervall_ende"]),
                       "replacement": True}}
    req = urllib.request.Request(URL, json.dumps(body).encode(),
                                 {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        antwort = json.load(r)
    if "error" in antwort:
        raise RuntimeError(antwort["error"])
    return antwort["result"]


def naechste_id(csv_pfad):
    if not csv_pfad.exists():
        return 1
    with csv_pfad.open(encoding="utf-8") as f:
        return max(sum(1 for _ in f) - 1, 0) + 1


def speichern(cfg, result, jetzt):
    ordner = Path(cfg["name_pfad_Ordner"])
    csv_pfad = ordner / cfg["name_datei_protokoll"]
    (ordner / "daten").mkdir(exist_ok=True)
    neu = not csv_pfad.exists() or csv_pfad.stat().st_size == 0
    rnd = result["random"]
    with csv_pfad.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if neu:
            w.writerow(SPALTEN)
        w.writerow([naechste_id(csv_pfad) if not neu else 1, f"{jetzt:%Y-%m-%d}", f"{jetzt:%H:%M:%S}",
                    rnd["serialNumber"], rnd["completionTime"],
                    " ".join(map(str, rnd["data"])), result["signature"], rnd["hashedApiKey"]])
    with (ordner / "daten" / f"{jetzt:%Y-%m-%d}.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps({"random": rnd, "signature": result["signature"]},
                           ensure_ascii=False) + "\n")


def main():
    cfg = lade_config()
    n, abstand = int(cfg["anzahl_zahlen"]), int(cfg["minutenabstand"]) * 60
    pro_tag = 86400 // abstand * n
    if pro_tag > int(cfg["kontingent_zufallszahlen_taeglich"]):
        sys.exit(f"Bedarf {pro_tag} Zahlen/Tag übersteigt Kontingent")
    log(f"Start: {n} Zahlen alle {abstand // 60} min ({pro_tag}/Tag)")
    while True:
        # auf den nächsten Slot warten (ab Ortszeit-Mitternacht gezählt)
        time.sleep(max(naechster_slot(abstand) - time.time(), 0))
        jetzt = datetime.now()
        try:
            res = abrufen(cfg, n)
            speichern(cfg, res, jetzt)
            log(f"OK serial={res['random']['serialNumber']} "
                f"bitsLeft={res.get('bitsLeft')} requestsLeft={res.get('requestsLeft')}")
            time.sleep(res.get("advisoryDelay", 0) / 1000)
        except Exception as e:  # Fehler überspringen, nächster Slot versucht es erneut
            log(f"FEHLER: {e}")


if __name__ == "__main__":
    main()
