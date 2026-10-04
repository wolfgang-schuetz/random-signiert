# random-signiert

Signierte Zufallszahlen von [RANDOM.ORG](https://www.random.org), alle 8 Minuten abgerufen und täglich hier veröffentlicht – Datengrundlage für ein privates Bewusstseinsexperiment.

*English summary: Cryptographically signed random integers from RANDOM.ORG, retrieved every 8 minutes and published daily on GitHub as the data basis for a private consciousness-and-matter experiment. The unmodified signed responses are stored so that anyone can verify their authenticity. This is a private project, not a peer-reviewed study.*

> **Hinweis zu RANDOM.ORG:** Die Zufallszahlen stammen von RANDOM.ORG und wurden mit deren Erlaubnis veröffentlicht. RANDOM.ORG steht nicht hinter diesem Experiment, seiner Methodik oder seinen Schlussfolgerungen und unterstützt sie nicht. Die Nutzung des Dienstes ist keine Stellungnahme dieser Institution.

Dies ist ein privates Projekt, keine begutachtete Studie. Hintergründe zum Experiment: <https://wolfgang-schuetz.pages.dev>

## Inhaltsverzeichnis

- [Worum geht es?](#worum-geht-es)
- [Wie funktioniert es?](#wie-funktioniert-es)
- [Inhalt des Repositorys](#inhalt-des-repositorys)
- [Datenformat](#datenformat)
- [Signatur prüfen](#signatur-prüfen)
- [Chronik](#chronik)
- [Selbst einrichten](#selbst-einrichten)
- [Einschränkungen und Hinweise](#einschränkungen-und-hinweise)
- [Lizenz](#lizenz)
- [Kontakt](#kontakt)

## Worum geht es?

Untersucht wird, ob sich in den Ausgaben eines Zufallszahlengenerators ein Einfluss gezielter mentaler Absicht zeigt. Die Daten werden fortlaufend und nachprüfbar dokumentiert, die Auswertung erfolgt getrennt davon. Es handelt sich um eine Hypothesenprüfung; dieses Repository behauptet kein Ergebnis.

Damit nachträglich niemand behaupten kann, die Zahlen seien verändert oder später ausgesucht worden, werden sie

1. von RANDOM.ORG **kryptografisch signiert** geliefert und
2. **täglich** öffentlich auf GitHub abgelegt. Der Zeitstempel der Commits dokumentiert, wann die Daten veröffentlicht wurden.

## Wie funktioniert es?

| Eigenschaft | Wert |
|---|---|
| Quelle | RANDOM.ORG, Methode `generateSignedIntegers` (JSON-RPC API v4) |
| Zahlen pro Abruf | 100 |
| Wertebereich | 1 bis 100 (ganze Zahlen, mit Zurücklegen) |
| Abstand | seit 2026-10-04 alle 8 Minuten, ab 00:00 Uhr gezählt (00:00, 00:08 … 00:56, 01:04 …), also 180 Abrufe pro Tag; zuvor alle 5 Minuten (siehe [Chronik](#chronik)) |
| Veröffentlichung | täglich um 23:58 Uhr (Ortszeit MESZ/MEZ) per systemd-Timer |
| Programmiersprache | Python 3 (nur Standardbibliothek) |

Ablauf:

1. Ein Dienst (`random-signiert.service`) ruft zu jedem Zeitpunkt 100 Zahlen samt Signatur bei RANDOM.ORG ab.
2. Jede Antwort wird unverändert als Rohdatensatz gespeichert und zusätzlich in ein CSV-Protokoll geschrieben.
3. Um 23:58 Uhr erstellt `upload_github.sh` die Tabelle des Tages und lädt den Ordner `daten/` nach GitHub hoch.

**Warum 8 Minuten?** Der API-Key hat ein Tageskontingent von 250.000 Bit. Ein Abruf kostet etwa 1.328 Bit. Bei 5 Minuten Abstand (288 Abrufe, ca. 382.000 Bit) war das Kontingent vor Tagesende aufgebraucht. Bei 8 Minuten (180 Abrufe, ca. 239.000 Bit) reicht es für den ganzen Tag. RANDOM.ORG setzt das Tageskontingent um 00:00 Uhr UTC zurück (02:00 Uhr MESZ bzw. 01:00 Uhr MEZ), nicht um Mitternacht Ortszeit.

## Inhalt des Repositorys

```
daten/
  JJJJ-MM-TT.csv     lesbare Tabelle eines Tages
  JJJJ-MM-TT.jsonl   unveränderte Rohantworten von RANDOM.ORG (eine pro Zeile)
random_signiert.py   Skript für den Abruf
upload_github.sh     täglicher Upload
README.md            diese Datei
```

Nicht veröffentlicht werden die Konfigurationsdatei mit dem API-Key und das lokale Gesamtprotokoll.

## Datenformat

**CSV** (`daten/JJJJ-MM-TT.csv`), eine Zeile pro Abruf:

| Spalte           | Bedeutung                                                             |
| ---------------- | --------------------------------------------------------------------- |
| `ID`             | laufende Nummer im lokalen Gesamtprotokoll                            |
| `Datum`, `Zeit`  | lokaler Zeitpunkt des Abrufs (Ortszeit, Systemuhr des Rechners)       |
| `SerialNumber`   | fortlaufende Nummer, die RANDOM.ORG jeder Antwort gibt                |
| `CompletionTime` | Zeitpunkt, den RANDOM.ORG als Fertigstellung der Antwort meldet (UTC) |
| `Zufallszahlen`  | die 100 Zahlen, durch Leerzeichen getrennt                            |
| `Signatur`       | Signatur von RANDOM.ORG (Base64)                                      |
| `HashedApiKey`   | Hash des verwendeten API-Keys (der Key selbst bleibt geheim)          |

**JSONL** (`daten/JJJJ-MM-TT.jsonl`): pro Zeile ein Objekt `{"random": {...}, "signature": "..."}`. Das ist genau das, was RANDOM.ORG geliefert hat, und die Grundlage für die Signaturprüfung.

**Für Auswertungen** bitte `CompletionTime` (UTC) verwenden. `Datum` und `Zeit` sind Ortszeit; bei der Umstellung von Sommer- auf Winterzeit (2026-10-25) wird die Stunde 02:00–03:00 doppelt durchlaufen. Die Zählung der 8 Minuten beginnt um 00:00 Uhr Ortszeit immer neu; an den Tagen der Zeitumstellung hat der Tag 23 bzw. 25 Stunden und damit 172 bzw. 188 Abrufe.

## Signatur prüfen

RANDOM.ORG signiert jede Antwort mit einem privaten Schlüssel. Wer die Echtheit prüfen möchte, kann das mit der Methode `verifySignature` der RANDOM.ORG-API tun. Dafür werden das Objekt `random` und die `signature` aus einer Zeile der `.jsonl`-Datei gesendet. RANDOM.ORG antwortet mit `authenticity: true` oder `false`. Dazu wird ein eigener API-Key von RANDOM.ORG benötigt.

Dokumentation: <https://api.random.org/json-rpc/4/signing>

Beispiel (Python 3, nur Standardbibliothek):

```python
import json, urllib.request

API_KEY = "IHR-API-KEY"
DATEI = "daten/2026-10-03.jsonl"

with open(DATEI, encoding="utf-8") as f:
    for nummer, zeile in enumerate(f, 1):
        antwort = json.loads(zeile)
        anfrage = {
            "jsonrpc": "2.0",
            "method": "verifySignature",
            "params": {
                "apiKey": API_KEY,
                "random": antwort["random"],
                "signature": antwort["signature"],
            },
            "id": nummer,
        }
        req = urllib.request.Request(
            "https://api.random.org/json-rpc/4/invoke",
            data=json.dumps(anfrage).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req) as r:
            ergebnis = json.load(r)["result"]["authenticity"]
        print(nummer, ergebnis)
```

Hinweis: Das Beispiel wurde nicht mit dem Original-Key des Projekts getestet; bei Abweichungen gilt die Dokumentation von RANDOM.ORG. Die Seriennummern (`SerialNumber`) laufen fortlaufend. Lücken können auch durch Testabrufe mit demselben API-Key entstehen und müssen nicht auf fehlende Daten hindeuten.

## Chronik

Änderungen am Verfahren und bekannte Ausfälle. Bitte bei Auswertungen berücksichtigen.

| Datum                                           | Ereignis                                                                                                                                                                                                                                                                      |
| ----------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-02                                      | Bitte an Random.org, die Lizenz umzustellen. Zuvor wurden Zufallszahlen mit anderem API-Key auf Basis der Developer-Lizenz unsigniert abgerufen. Weiterhin wurde Random.org gebeten, die Generierung der Zufallszahlen zum Zeitpunkt des jeweiligen Abrufes zu gewährleisten. |
| 2026-10-03                                      | Start der signierten Abrufe, Abstand 5 Minuten                                                                                                                                                                                                                                |
| 2026-10-03, 18:45 Uhr bis 2026-10-04, 02:05 Uhr | Keine Abrufe: Tageskontingent bei RANDOM.ORG erschöpft (Rücksetzung um 02:00 Uhr MESZ)                                                                                                                                                                                                                        |
| 2026-10-04                                      | Umstellung von 5 auf 8 Minuten Abstand, damit das Tageskontingent reicht (Bruch im Zeitraster): letzter 5-Minuten-Abruf 10:00 Uhr, erster 8-Minuten-Abruf 10:08 Uhr                                                                                                                                                                                |

## Selbst einrichten

Voraussetzungen: Linux mit systemd, Python 3, git, ein eigener RANDOM.ORG-API-Key.

1. Repository klonen.
2. Konfigurationsdatei `config_man6_signiert.txt` anlegen (wird nicht ins Repository übernommen; „man6“ ist das interne Projektkürzel des Experiments):

   ```
   # Obergrenze in Zufallszahlen pro Tag als Schutz im Skript, nicht das Bit-Kontingent von RANDOM.ORG
   kontingent_zufallszahlen_taeglich=35000
   intervall_beginn=1
   intervall_ende=100
   minutenabstand=8
   anzahl_zahlen=100
   name_datei_protokoll=random_man6_signiert_protokoll.csv
   name_pfad_Ordner=/Pfad/zum/Repository
   api=IHR-API-KEY
   upload_uhrzeit=23:58
   ```
3. Den Abruf als systemd-Benutzerdienst und den Upload als Timer einrichten.
4. Der Abstand muss so gewählt sein, dass das Tageskontingent des API-Keys für den ganzen Tag reicht (siehe [Wie funktioniert es?](#wie-funktioniert-es)).

## Einschränkungen und Hinweise

**Zeitpunkt der Generierung.** RANDOM.ORG konnte bisher nicht garantieren, dass die Zufallszahlen erst **zum Zeitpunkt des Abrufs generiert** werden. Es ist daher nicht ausgeschlossen, dass Zahlen bereits vorher erzeugt wurden. Der Zeitstempel (`CompletionTime`) in der signierten Antwort belegt den Zeitpunkt der Auslieferung, aber nicht zwingend den der Erzeugung. RANDOM.ORG wurde am 2. Oktober 2026 gebeten, die Zahlen künftig zum Zeitpunkt des Abrufs zu generieren.

**Keine Stellungnahme von RANDOM.ORG.** Die Nutzung des Dienstes stellt keine öffentliche Stellungnahme dieser Institution dar. RANDOM.ORG macht sich die Methodik dieses Experiments weder zu eigen noch bestätigt oder unterstützt es sie. Die Veröffentlichung der unveränderten signierten Antworten erfolgt mit Erlaubnis von RANDOM.ORG (E-Mail vom 1. Oktober 2026).

**Weitere Hinweise**

- Dies ist ein privates Projekt und keine wissenschaftlich begutachtete Studie.
- Lücken in den Daten sind möglich, zum Beispiel wenn der Rechner ausgeschaltet war, das Internet ausfiel oder das Tageskontingent aufgebraucht war. Fehlende Abrufe werden nicht nachgeholt. Bekannte Lücken stehen in der [Chronik](#chronik).
- Ist der Rechner zur Upload-Zeit aus, werden die Daten beim nächsten regulären Upload nachgereicht. Der Commit-Zeitstempel ist dann entsprechend später.
- Der Datensatz enthält den Vermerk von RANDOM.ORG, der API-Key sei „licensed strictly for development and testing only“. Die Veröffentlichung erfolgt mit der oben genannten Erlaubnis von RANDOM.ORG.

## Lizenz

- **Code** (`random_signiert.py`, `upload_github.sh`): MIT-Lizenz (Datei `LICENSE`). Sie gilt nur für die Skripte, nicht für die Daten in `daten/`.
- **Daten** (`daten/`): Die Zufallszahlen stammen von RANDOM.ORG und werden mit deren Erlaubnis veröffentlicht. Eine Weiterverwendung ist nur mit Quellenangabe (RANDOM.ORG, <https://www.random.org>) möglich; es gelten die [Nutzungsbedingungen von RANDOM.ORG](https://www.random.org/terms/). Eine weitergehende Lizenz (z. B. CC BY) wird hier nicht vergeben.

## Kontakt

Wolfgang Schütz · GitHub: [@wolfgang-schuetz](https://github.com/wolfgang-schuetz) · Homepage: <https://wolfgang-schuetz.pages.dev>

Fragen oder Hinweise bitte über die [Issues](https://github.com/wolfgang-schuetz/random-signiert/issues) dieses Repositorys.
