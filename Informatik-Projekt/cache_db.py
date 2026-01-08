# cache_db.py

"""
cache_db.py

Aufgabe:
    Dieses Modul implementiert ein persistentes Cache-System zur
    Performance-Optimierung. Es speichert Abfahrtsinformationen für einzelne
    Haltestellen lokal, um wiederholte Scans großer GTFS-Dateien zu vermeiden.

Verwendete Technologien:
    - SQLite (lokale Datenbank)
    - Python sqlite3-Modul

Zentrale Aufgaben:
    - Aufbau eines Caches pro stop_id
    - Persistente Speicherung zwischen Programmläufen
    - Schnelle Abfrage von Abfahrten nach Zeit

Hinweise:
    - Beim ersten Zugriff auf eine Haltestelle wird ein vollständiger Scan durchgeführt.
    - Folgezugriffe sind deutlich schneller.
"""

import sqlite3
from typing import Dict, List, Tuple, Set

from gtfs_zip import iter_rows
from utils import parse_gtfs_time_to_seconds, now_seconds
from models import Departure

def connect(db_path: str) -> sqlite3.Connection:
    con = sqlite3.connect(db_path)
    con.execute("PRAGMA journal_mode=WAL;")
    con.execute("PRAGMA synchronous=NORMAL;")
    return con

def init_db(con: sqlite3.Connection) -> None:
    con.execute("""
    CREATE TABLE IF NOT EXISTS stop_times_cache (
    stop_id TEXT NOT NULL,
    trip_id TEXT NOT NULL,
    departure_time TEXT NOT NULL,
    departure_sec INTEGER NOT NULL,
    stop_sequence INTEGER NOT NULL,

    route_name TEXT,
    headsign TEXT
);
    """)
    con.execute("CREATE INDEX IF NOT EXISTS idx_stop_depsec ON stop_times_cache(stop_id, departure_sec);")
    con.execute("CREATE INDEX IF NOT EXISTS idx_stop_trip ON stop_times_cache(stop_id, trip_id);")
    con.commit()

def has_cached_stop(con: sqlite3.Connection, stop_id: str) -> bool:
    cur = con.execute("SELECT 1 FROM stop_times_cache WHERE stop_id=? LIMIT 1;", (stop_id,))
    return cur.fetchone() is not None

def build_cache_for_stop(zip_path: str, con: sqlite3.Connection, stop_id: str) -> int:
    """
    Scannt EINMAL die riesige stop_times.txt und speichert NUR Zeilen für stop_id.
    Das dauert beim ersten Mal ein bisschen, danach ist es schnell.
    """
    con.execute("DELETE FROM stop_times_cache WHERE stop_id=?;", (stop_id,))
    con.commit()

    rows_to_insert: List[Tuple[str, str, str, int, int]] = []
    trips = {
    r["trip_id"]: r
    for r in iter_rows(zip_path, "trips.txt")
}

    routes = {
    r["route_id"]: r
    for r in iter_rows(zip_path, "routes.txt")
}
    
    count = 0

    for row in iter_rows(zip_path, "stop_times.txt"):
        sid = (row.get("stop_id") or "").strip()
        if sid != stop_id:
            continue

        trip_id = (row.get("trip_id") or "").strip()
        dep_time = (row.get("departure_time") or "").strip()
        seq = (row.get("stop_sequence") or "").strip()
        if not trip_id or not dep_time or not seq.isdigit():
            continue

        dep_sec = parse_gtfs_time_to_seconds(dep_time)
        trip = trips.get(trip_id, {})
        route_id = trip.get("route_id")
        route = routes.get(route_id, {})

        route_name = (
            route.get("route_short_name")
            or route.get("route_long_name")
            or route_id
)

        headsign = trip.get("trip_headsign")

        rows_to_insert.append((
            stop_id,
            trip_id,
            dep_time,
            dep_sec,
            int(seq),
            route_name or "",
            headsign or ""
))
        count += 1

        # Batch insert, damit’s nicht langsam ist
        if len(rows_to_insert) >= 5000:
            con.executemany(
                "INSERT INTO stop_times_cache(stop_id,trip_id,departure_time,departure_sec,stop_sequence,route_name,headsign)) VALUES (?,?,?,?,?,?,?);",
                rows_to_insert
            )
            con.commit()
            rows_to_insert.clear()

    if rows_to_insert:
        con.executemany(
            "INSERT INTO stop_times_cache(stop_id,trip_id,departure_time,departure_sec,stop_sequence,route_name,headsign) VALUES (?,?,?,?,?,?,?);",
            rows_to_insert
        )
        con.commit()

    return count

def get_next_departures_cached(
    con: sqlite3.Connection,
    stop_id: str,
    active_trip_route: Dict[str, str],
    limit: int = 10
) -> List[Departure]:
    """
    Holt nächste Abfahrten ab 'jetzt' aus dem Cache.
    Filtert gleichzeitig auf heute aktive trip_ids.
    """
    now_sec = now_seconds()

    # Wir holen erstmal mehr als limit, weil wir danach nach active trips filtern.
    cur = con.execute(
    """
    SELECT
        trip_id,
        departure_time,
        departure_sec,
        stop_sequence,
        route_name,
        headsign
    FROM stop_times_cache
    WHERE stop_id=?
      AND departure_sec>=?
    ORDER BY departure_sec ASC
    LIMIT ?;
    """,
    (stop_id, now_sec, limit * 20)
)
    result: List[Departure] = []
    for trip_id, dep_time, dep_sec, seq, route_name, headsign in cur.fetchall():
        route_id = active_trip_route.get(trip_id)
        if not route_id:
            continue
        result.append(
            Departure(
                trip_id=trip_id,
                route_id=route_id,
                departure_time=dep_time,
                stop_sequence=seq,
                route_name=route_name,
                headsign=headsign))
        if len(result) >= limit:
            break

    return result

def trip_stop_sequence(zip_path: str, trip_id: str) -> List[Tuple[int, str]]:
    """
    Für die Karte: Stop-Reihenfolge eines trips (Stop-IDs).
    (Das ist kleiner als stop_times für Stop; hier scannen wir stop_times erneut,
     aber nur für eine trip_id – das ist okay.)
    """
    seq: List[Tuple[int, str]] = []
    for row in iter_rows(zip_path, "stop_times.txt"):
        tid = (row.get("trip_id") or "").strip()
        if tid != trip_id:
            continue
        stop_id = (row.get("stop_id") or "").strip()
        sseq = (row.get("stop_sequence") or "").strip()
        if stop_id and sseq.isdigit():
            seq.append((int(sseq), stop_id))
    seq.sort(key=lambda x: x[0])
    return seq