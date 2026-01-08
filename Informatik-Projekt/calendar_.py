# calendar_.py

"""
calendar_.py

Aufgabe:
    Dieses Modul bestimmt, welche Fahrplan-Services (service_id) an einem
    bestimmten Datum aktiv sind. Grundlage sind die GTFS-Dateien calendar.txt
    und calendar_dates.txt.

Verwendete GTFS-Dateien:
    - calendar.txt
    - calendar_dates.txt

Zentrale Aufgaben:
    - Ermittlung regulärer Fahrtage (Wochentage)
    - Berücksichtigung von Ausnahmen (Feiertage, Sonderfahrten)
    - Zusammenführung beider Kalenderquellen

Hinweise:
    - Die Logik orientiert sich strikt am GTFS-Standard.
    - Das Ergebnis ist eine Menge aktiver service_id für ein Datum.
"""

from datetime import date
from typing import Set
from gtfs_zip import iter_rows, has_file
from utils import yyyymmdd, weekday_key

def active_service_ids(zip_path: str, d: date) -> Set[str]:
    active: Set[str] = set()
    day = yyyymmdd(d)
    wk = weekday_key(d)

    # calendar.txt
    for row in iter_rows(zip_path, "calendar.txt"):
        sid = (row.get("service_id") or "").strip()
        start = (row.get("start_date") or "").strip()
        end = (row.get("end_date") or "").strip()
        if not sid or not start or not end:
            continue
        if not (start <= day <= end):
            continue
        if (row.get(wk) or "0").strip() == "1":
            active.add(sid)

    # calendar_dates.txt (optional)
    if has_file(zip_path, "calendar_dates.txt"):
        for row in iter_rows(zip_path, "calendar_dates.txt"):
            sid = (row.get("service_id") or "").strip()
            dt = (row.get("date") or "").strip()
            ex = (row.get("exception_type") or "").strip()  # 1 add, 2 remove
            if dt != day or not sid:
                continue
            if ex == "1":
                active.add(sid)
            elif ex == "2":
                active.discard(sid)

    return active

    """
    Ermittelt alle service_id, die an einem bestimmten Datum aktiv sind.

    Zweck:
        GTFS trennt Fahrten (trips) von Fahrtagen (service_id).
        Damit Abfahrten "heute" korrekt gefiltert werden, muss zuerst bestimmt werden,
        welche service_id für das heutige Datum gültig ist.

    Verwendete GTFS-Dateien:
        - calendar.txt (reguläre Fahrtage)
        - calendar_dates.txt (Ausnahmen: zusätzliche oder entfernte Fahrtage)

    Parameter:
        zip_path (str): Pfad zur GTFS-ZIP-Datei.
        d (date): Datum, für das aktive Services ermittelt werden sollen.

    Rückgabe:
        Set[str]: Menge aktiver service_id.

    Besonderheiten:
        - calendar_dates kann services hinzufügen (exception_type=1) oder entfernen (2).
        - Vergleich YYYYMMDD als String ist hier ausreichend (lexikografisch passend).
    """