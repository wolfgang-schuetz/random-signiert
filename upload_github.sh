#!/usr/bin/env bash
# Veröffentlicht die Daten des heutigen Tages auf GitHub (Aufruf täglich 23:58).
set -euo pipefail
cd "$(dirname "$0")"
tag=$(date +%F)
# Tages-CSV aus dem Gesamtprotokoll ableiten (Kopfzeile + Zeilen des Tages).
# Auch für verpasste Tage (Rechner war um 23:58 aus): fehlende Tabellen werden nachgeholt.
proto=$(grep '^name_datei_protokoll=' config_man6_signiert.txt | cut -d= -f2)
for d in $(awk -F, 'NR>1 {print $2}' "$proto" | sort -u); do
  if [ "$d" = "$tag" ] || [ ! -f "daten/$d.csv" ]; then
    { head -n1 "$proto"; awk -F, -v d="$d" 'NR>1 && $2==d' "$proto"; } > "daten/$d.csv"
  fi
done
git add daten
if git diff --cached --quiet; then echo "Nichts zu committen"; exit 0; fi
git commit -m "Zufallszahlen $tag"
# Änderungen von GitHub (z. B. README, am anderen Rechner bearbeitet) zuerst holen
git pull --rebase --autostash origin main
git push origin HEAD
