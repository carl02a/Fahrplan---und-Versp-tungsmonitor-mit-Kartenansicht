Abfahrtsplan von deutschen Bahnhöfen. Mit einer Visualisierung auf einer Karte des (Punkt zu Punkt) Streckenverlaufs
GFTS - Zip Datei von gtfs.de

Nähere  Erläuterung:
# GTFS-Abfahrtsmonitor mit Routenvisualisierung (Deutschland)

## 1. Projektbeschreibung

Dieses Projekt ist ein modular aufgebauter Abfahrts- und Routenmonitor für den öffentlichen Schienenverkehr in Deutschland.  
Es basiert auf dem internationalen **GTFS-Standard (General Transit Feed Specification)** und verarbeitet einen vollständigen deutschlandweiten GTFS-Fahrplandatensatz in ZIP-Form.

Ziel des Projekts ist es, reale Verkehrsdaten strukturiert zu analysieren, performant zu verarbeiten und benutzerfreundlich darzustellen. Dabei liegt der Fokus nicht auf Echtzeitdaten, sondern auf der korrekten Interpretation, Filterung und Visualisierung statischer Fahrplandaten.

Das Projekt wurde im Rahmen einer Informatik-Lehrveranstaltung entwickelt und legt besonderen Wert auf:

- saubere Modularisierung
- verständliche Datenflüsse
- Performance-Optimierung durch Caching
- realitätsnahe Datenverarbeitung
- nachvollziehbare Designentscheidungen

---

## 2. Motivation

Öffentliche Verkehrssysteme erzeugen große Mengen strukturierter Daten. Der GTFS-Standard stellt hierfür ein einheitliches Austauschformat bereit, wird jedoch in der Praxis häufig als „Black Box“ genutzt.

Die Motivation dieses Projekts ist es, den GTFS-Datensatz nicht nur zu konsumieren, sondern dessen interne Struktur, Abhängigkeiten und Herausforderungen explizit sichtbar zu machen. Besonders relevant sind dabei:

- sehr große Textdateien (z. B. `stop_times.txt`)
- komplexe Beziehungen zwischen Trips, Stops, Routes und Kalendern
- Laufzeitprobleme bei naiver Verarbeitung
- fehlende optionale Datenteile (z. B. `shapes.txt`)

Das Projekt versteht sich daher als Brücke zwischen theoretischer Datenmodellierung und praktischer Softwareentwicklung.

Als Vorbild dient bspw. der DB Navigator
---

## 3. Funktionsübersicht

Das Programm bietet folgende Kernfunktionen:

- Textbasierte Suche nach Haltestellen
- Auswahl eines konkreten Bahnhofs / Halts
- Ermittlung der nächsten Abfahrten für diesen Halt
- Berücksichtigung aktiver Fahrtage (Kalenderlogik)
- Aufbau einer Route auf Basis der Haltestellenreihenfolge
- Visualisierung der Route auf einer interaktiven OpenStreetMap-Karte
- Persistentes Caching zur Reduktion der Laufzeit bei Folgeaufrufen

---

## 4. Technische Architektur

Das Projekt ist strikt modular aufgebaut. Jede Datei übernimmt klar abgegrenzte Verantwortlichkeiten.

### 4.1 Modulübersicht

- **main.py**  
  Zentrale Einstiegspunkt-Datei. Orchestriert den gesamten Programmablauf und verbindet Benutzerinteraktion mit der Datenlogik.

- **cli.py**  
  Verantwortlich für sämtliche textbasierte Benutzereingaben und -ausgaben.

- **gtfs_zip.py**  
  Kapselt den Zugriff auf den GTFS-ZIP-Feed. Stellt Iteratoren bereit, um große CSV-Dateien speicherschonend zeilenweise zu lesen.

- **stops.py**  
  Lädt Haltestellen aus `stops.txt` und implementiert Such- und Filterfunktionen.

- **departures.py**  
  Ermittelt Abfahrten anhand von `stop_times.txt`, `trips.txt` und Kalenderdateien.

- **cache_db.py**  
  Implementiert ein persistentes Caching auf Basis von SQLite, um wiederholte teure Scans zu vermeiden.

- **route_map.py**  
  Erzeugt eine Kartenvisualisierung der Route mit Hilfe von Folium und OpenStreetMap.

- **models.py**  
  Enthält strukturierte Datenmodelle (z. B. für Stops, Trips, Departures).

- **config.py**  
  Zentrale Konfigurationsdatei für Pfade, Limits und Standardwerte.

---

## 5. Verwendeter Datenstandard: GTFS

GTFS (General Transit Feed Specification) ist ein international etablierter Standard zur Beschreibung öffentlicher Fahrpläne.

Im Projekt werden insbesondere folgende Dateien genutzt:

- `stops.txt` – Haltestellen mit Koordinaten
- `routes.txt` – Linien und Verkehrsarten
- `trips.txt` – einzelne Fahrten
- `stop_times.txt` – zeitliche Zuordnung von Trips zu Stops
- `calendar.txt` – reguläre Fahrtage
- `calendar_dates.txt` – Abweichungen (Feiertage etc.)

### 5.1 Fehlende shapes.txt

Der verwendete deutschlandweite GTFS-Feed enthält **keine `shapes.txt`**.  
Daher ist keine exakte Gleisgeometrie verfügbar.

**Konsequenz:**  
Die Routenvisualisierung erfolgt als Polyline über die Koordinaten der sequenziellen Haltestellen.  
Diese Darstellung ist standardkonform und korrekt auf Basis der verfügbaren Daten.

---

## 6. Performance und Caching

Eine naive Verarbeitung von `stop_times.txt` würde bei jedem Programmlauf mehrere hunderttausend Zeilen erneut scannen. Um dies zu vermeiden, wird ein persistenter Cache eingesetzt.

Eigenschaften des Cache-Systems:

- Pro Halt wird ein separater Cache-Eintrag erzeugt
- Beim ersten Zugriff erfolgt ein vollständiger Scan
- Folgezugriffe sind um Größenordnungen schneller
- Cache bleibt zwischen Programmläufen erhalten

Diese Architektur stellt einen bewussten Trade-off zwischen Speicherplatz und Laufzeit dar.

---

## 7. Kartenvisualisierung

Die Kartenvisualisierung erfolgt mit:

- **Folium** (Python-Bibliothek)
- **OpenStreetMap** als Kartenbasis

Die erzeugte Karte wird als lokale HTML-Datei gespeichert und automatisch im Browser geöffnet.

Dargestellt werden:
- Start- und Zielhaltestellen
- Zwischenhalte (optional)
- Verbindungslinie zwischen den Haltestellen

---

## 8. Installation und Ausführung

### Voraussetzungen
- Python ≥ 3.10
- Internetbrowser
- ca. 300 MB freier Speicherplatz für den GTFS-Feed

### Installation
```bash
pip install folium
```

### Vorbereitung
- GTFS-ZIP-Datei in `data/feed.zip` ablegen
- Datei **nicht entpacken**

### Start
```bash
python3 main.py
```

---

## 9. Beispielablauf

1. Programmstart
2. Eingabe eines Bahnhofnamens
3. Auswahl aus Trefferliste
4. Aufbau des Cache (nur beim ersten Mal)
5. Anzeige der nächsten Abfahrten
6. Auswahl einer Verbindung
7. Automatische Kartenanzeige im Browser

---

## 10. Teamarbeit und Aufgabenteilung

Dieses Projekt wurde von zwei Personen erstellt. 

-Person A
  Datenverarbeitung, GTFS-Parsing, Caching, Routenlogik, Backend-Architektur, Doku(ReadMe)

-Person B
  Benutzeroberfläche, Design, Usability, Dokumentation(README)

Die modulare Struktur erlaubt eine klare Trennung der Verantwortlichkeiten.

---

## 11. Einschränkungen und mögliche Erweiterungen

Bekannte Einschränkungen:
- keine Echtzeit-Verspätungsdaten
- keine Gleisgeometrie (fehlende shapes.txt)

Mögliche Erweiterungen:
- Integration von Echtzeitdaten
- Unterstützung von shapes.txt bei anderen Feeds
- grafische Benutzeroberfläche (GUI)
- Webbasierte Darstellung

---

## 12. Fazit

Das Projekt zeigt exemplarisch, wie reale, komplexe Verkehrsdaten mit überschaubaren Mitteln verarbeitet, analysiert und visualisiert werden können. Besonderer Wert wurde auf Nachvollziehbarkeit, Performance und saubere Softwarearchitektur gelegt.

Die Implementierung ist bewusst modular und erweiterbar gehalten und stellt eine solide Grundlage für weiterführende Arbeiten dar.