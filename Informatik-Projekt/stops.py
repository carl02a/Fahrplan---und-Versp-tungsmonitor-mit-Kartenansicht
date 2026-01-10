# stops.py

"""
stops.py

Aufgabe:
    Dieses Modul verarbeitet Haltestelleninformationen aus dem GTFS-Feed
    (Datei: stops.txt). Es stellt Funktionen bereit, um Haltestellen zu laden
    und textbasiert zu durchsuchen.

Verwendete GTFS-Dateien:
    - stops.txt

Zentrale Aufgaben:
    - Laden aller Haltestellen mit Name und Koordinaten
    - Aufbau von Suchstrukturen
    - Textbasierte Suche nach Haltestellennamen

Hinweise:
    - Haltestellen ohne Koordinaten werden ignoriert.
    - Die Suche ist bewusst einfach gehalten (Substring-Suche).
"""

from typing import Dict, List, Tuple
from models import Stop
from gtfs_zip import iter_rows

def load_stops(zip_path: str) -> Dict[str, Stop]:
    stops: Dict[str, Stop] = {}
    for row in iter_rows(zip_path, "stops.txt"):
        sid = (row.get("stop_id") or "").strip()
        name = (row.get("stop_name") or "").strip()
        lat = row.get("stop_lat")
        lon = row.get("stop_lon")
        if not sid or not name or lat is None or lon is None:
            continue
        try:
            stops[sid] = Stop(sid, name, float(lat), float(lon))
        except ValueError:
            continue
    return stops

# stops.py
def child_stop_ids(stops_by_id, parent_id):
    return [
        s.stop_id
        for s in stops_by_id.values()
        if getattr(s, "parent_station", None) == parent_id
    ]

    """
    Lädt alle Haltestellen (Stops) aus stops.txt und baut ein Mapping stop_id -> Stop.

    Zweck:
        Die Stop-Tabelle ist die Grundlage für:
        - Stationssuche (Benutzer tippt "Mannheim", "Basel", ...)
        - Koordinaten (lat/lon) für die Kartenvisualisierung

    Parameter:
        zip_path (str): Pfad zur GTFS-ZIP-Datei.

    Rückgabe:
        Dict[str, Stop]: Mapping von stop_id auf Stop-Objekt (Name + Koordinaten).

    Besonderheiten:
        - Ungültige Datensätze (fehlende Koordinaten oder leere Namen) werden ignoriert.
        - Koordinaten werden in float konvertiert.
    """

def search_stops(stops: Dict[str, Stop], query: str, limit: int = 10) -> List[Tuple[str, str]]:
    q = query.strip().lower()
    matches: List[Tuple[str, str]] = []
    for sid, s in stops.items():
        if q in s.stop_name.lower():
            matches.append((sid, s.stop_name))
    matches.sort(key=lambda x: (len(x[1]), x[1]))
    return matches[:limit]

    """
    Sucht Haltestellen anhand eines Textfragments (Substring-Suche).

    Zweck:
        Benutzerfreundliche Suche nach Stationen ohne komplizierte Indizes.
        Beispiel: Query "mann" findet "Mannheim Hbf", "Mannheim ARENA/Maimarkt", ...

    Parameter:
        stops (Dict[str, Stop]): Mapping stop_id -> Stop.
        query (str): Suchtext, z. B. "Mannheim".
        limit (int): Maximalzahl an Treffern, die zurückgegeben werden.

    Rückgabe:
        List[Tuple[str, str]] oder List[Stop] (je nach Implementierung):
            Trefferliste, meist sortiert nach Einfachheit/Relevanz.

    Hinweise:
        - Absichtlich simpel (Substring), da GTFS extrem viele Stops enthalten kann.
        - Sortierung kann z. B. nach Namenslänge erfolgen.
    """