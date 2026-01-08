# departures.py  

"""
departures.py

Aufgabe:
    Dieses Modul ist für die Ermittlung von Abfahrten an einer bestimmten
    Haltestelle verantwortlich. Es verarbeitet GTFS-Daten aus stop_times.txt,
    trips.txt, routes.txt sowie Kalenderdateien, um zeitlich gültige Abfahrten
    zu bestimmen.

Verwendete GTFS-Dateien:
    - stop_times.txt
    - trips.txt
    - routes.txt
    - calendar.txt
    - calendar_dates.txt

Zentrale Aufgaben:
    - Filtern von Trips anhand aktiver service_id
    - Zuordnung von trip_id zu route_id
    - Ermittlung der nächsten Abfahrten für eine stop_id
    - Formatierung von Linien- und Routennamen

Hinweise:
    - Dieses Modul arbeitet eng mit calendar_.py zusammen.
    - Die Verarbeitung erfolgt zeilenweise, um große Datenmengen handhabbar zu machen.
"""

from typing import Dict, Set, List
from gtfs_zip import iter_rows
from models import Departure

def build_active_trip_route_map(zip_path: str, active_services: Set[str]) -> Dict[str, str]:
    """
    trip_id -> route_id nur für heute aktive services
    """
    m: Dict[str, str] = {}
    for row in iter_rows(zip_path, "trips.txt"):
        trip_id = (row.get("trip_id") or "").strip()
        service_id = (row.get("service_id") or "").strip()
        route_id = (row.get("route_id") or "").strip()
        if trip_id and route_id and service_id in active_services:
            m[trip_id] = route_id
    return m

    """
    Baut ein Mapping trip_id -> route_id für Trips, deren service_id heute aktiv ist.

    Zweck:
        Um Abfahrten an einem Stop zu ermitteln, braucht man trip_id aus stop_times.txt.
        Allerdings sollen nur Trips berücksichtigt werden, die heute gültig sind.
        Dieses Mapping ermöglicht schnelles Filtern: trip_id ist nur gültig,
        wenn es hier enthalten ist.

    Parameter:
        zip_path (str): Pfad zur GTFS-ZIP-Datei.
        active_services (Set[str]): Menge der service_id, die heute aktiv sind.

    Rückgabe:
        Dict[str, str]: Mapping trip_id -> route_id (nur aktive Trips).

    Hinweise:
        - trips.txt kann sehr groß sein, wird daher zeilenweise gestreamt.
        - route_id wird später genutzt, um Liniennamen aus routes.txt zu laden.
    """

def load_routes(zip_path: str) -> Dict[str, Dict[str, str]]:
    routes: Dict[str, Dict[str, str]] = {}
    for row in iter_rows(zip_path, "routes.txt"):
        rid = (row.get("route_id") or "").strip()
        if rid:
            routes[rid] = row
    return routes

    """
    Lädt routes.txt in ein Mapping route_id -> Zeile (Dictionary).

    Zweck:
        route_id alleine ist nicht benutzerfreundlich. Für die Anzeige (CLI/GUI)
        braucht man z. B. route_short_name und route_long_name.

    Parameter:
        zip_path (str): Pfad zur GTFS-ZIP-Datei.

    Rückgabe:
        Dict[str, Dict[str, str]]: Mapping route_id -> Routendaten (Spaltenwerte).
    """

def format_route_name(route_row: Dict[str, str]) -> str:
    short = (route_row.get("route_short_name") or "").strip()
    long = (route_row.get("route_long_name") or "").strip()
    if short and long:
        return f"{short} – {long}"
    return short or long or "Route"

from gtfs_zip import iter_rows

def build_trip_route_map_all(zip_path: str) -> dict[str, str]:
    """
    Fallback: baut trip_id -> route_id für ALLE Trips (ohne calendar-Filter).
    Nutzt man, wenn active_service_ids leer ist (Feed nicht für heutiges Datum gültig).
    """
    m: dict[str, str] = {}
    for row in iter_rows(zip_path, "trips.txt"):
        trip_id = (row.get("trip_id") or "").strip()
        route_id = (row.get("route_id") or "").strip()
        if trip_id and route_id:
            m[trip_id] = route_id
    return m

    """
    Formatiert eine Route/Line zu einem lesbaren Namen.

    Zweck:
        Routen können einen kurzen Namen (route_short_name) und/oder einen langen Namen
        (route_long_name) haben. Diese Funktion baut daraus eine sinnvolle Anzeige.

    Parameter:
        route_row (Dict[str, str]): Zeile aus routes.txt für eine route_id.

    Rückgabe:
        str: Anzeigename der Linie, z. B. "S3 – Germersheim ↔ Karlsruhe".

    Hinweise:
        - Falls Daten fehlen, wird ein Fallback-Name ("Route") verwendet.
    """