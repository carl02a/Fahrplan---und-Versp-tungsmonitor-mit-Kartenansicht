# models.py

from dataclasses import dataclass

@dataclass(frozen=True)
class Stop:
    stop_id: str
    stop_name: str
    lat: float
    lon: float

@dataclass(frozen=True)
class Departure:
    trip_id: str
    route_id: str
    departure_time: str
    stop_sequence: int