# models.py

"""
models.py

Aufgabe:
    Dieses Modul definiert strukturierte Datenmodelle für das Projekt.
    Es verwendet Dataclasses, um komplexe Datensätze übersichtlich und
    typsicher darzustellen.

Zentrale Datenmodelle:
    - Stop
    - Departure
    - Route (optional)

Vorteile:
    - Verbesserte Lesbarkeit
    - Klare Trennung von Daten und Logik
    - Einheitliche Datenrepräsentation im gesamten Projekt
"""

from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class Stop:
    stop_id: str
    stop_name: str
    lat: float
    lon: float
    parent_station: Optional[str] = None
    location_type: Optional[int] = None  # 0=platform/stop, 1=station (oft Parent)

@dataclass(frozen=True)
class Departure:
    trip_id: str
    route_id: str
    departure_time: str
    stop_sequence: int

    # Anzeigenfelder
    route_name: str | None = None
    headsign: str | None = None