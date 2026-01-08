# main.py
"""
main.py

Aufgabe:
    Zentrale Einstiegspunkt-Datei des Programms. Dieses Modul koordiniert
    den gesamten Ablauf von der Benutzereingabe über die Datenverarbeitung
    bis hin zur Ausgabe und Kartenvisualisierung.

Zentrale Aufgaben:
    - Start des Programms
    - Aufruf der CLI oder UI
    - Verbindung der einzelnen Module
    - Steuerung des Programmflusses

Hinweise:
    - Diese Datei enthält möglichst wenig Fachlogik.
    - Sie dient primär der Orchestrierung.
"""
# main.py
print("MAIN STARTET")
from config import GTFS_ZIP_PATH, CACHE_DB_PATH, DEFAULT_RESULTS_LIMIT, DEFAULT_DEPARTURES_LIMIT, MAP_FILE, MAP_ZOOM
from utils import today_date
from cli import header, choose_from_list, ask_yes_no
from stops import load_stops, search_stops
from calendar_ import active_service_ids
from departures import build_active_trip_route_map, load_routes, format_route_name
from cache_db import connect, init_db, has_cached_stop, build_cache_for_stop, get_next_departures_cached, trip_stop_sequence
from route_map import build_map_from_stop_ids

def main():
    header("GTFS Abfahrtsmonitor (Deutschland-Feed)")

    print("1) Lade stops.txt ...")
    stops_by_id = load_stops(GTFS_ZIP_PATH)
    print(f"   Stops geladen: {len(stops_by_id)}")

    query = input("\nBahnhof/Halt suchen (z.B. 'Mannheim', 'Karlsruhe', 'Berlin Hbf'): ").strip()
    hits = search_stops(stops_by_id, query, limit=DEFAULT_RESULTS_LIMIT)

    if not hits:
        print("Keine Treffer. Tipp: kürzer suchen (z.B. nur 'Berlin').")
        return

    idx = choose_from_list(hits, "Nummer wählen:")
    if idx == -1:
        print("Ungültige Auswahl.")
        return

    stop_id, stop_name = hits[idx]
    header(f"Gewählt: {stop_name}")

    # heutige Services
    d = today_date()
    print("2) Bestimme heute gültige services ...")
    services = active_service_ids(GTFS_ZIP_PATH, d)
    print(f"   aktive service_ids: {len(services)}")

    print("3) Baue trip->route Map (nur aktive Trips) ...")
    active_trip_route = build_active_trip_route_map(GTFS_ZIP_PATH, services)
    print(f"   aktive trips: {len(active_trip_route)}")

    # Cache vorbereiten
    con = connect(CACHE_DB_PATH)
    init_db(con)

    if not has_cached_stop(con, stop_id):
        print("\n4) Cache für diesen Bahnhof existiert noch nicht.")
        print("   Ich scanne stop_times.txt EINMAL für diesen stop_id.")
        print("   Das kann (je nach Bahnhof) ein bisschen dauern, danach ist es schnell.")
        inserted = build_cache_for_stop(GTFS_ZIP_PATH, con, stop_id)
        print(f"   Cache-Zeilen gespeichert: {inserted}")
    else:
        print("\n4) Cache vorhanden – Abfahrten werden schnell geladen.")

    # Abfahrten
    print("\n5) Nächste Abfahrten:")
    deps = get_next_departures_cached(con, stop_id, active_trip_route, limit=DEFAULT_DEPARTURES_LIMIT)

    if not deps:
        print("Keine Abfahrten gefunden. (Kann am Datum/Wochentag/Feed liegen.)")
        return

    routes = load_routes(GTFS_ZIP_PATH)

    for i, dep in enumerate(deps, start=1):
        rrow = routes.get(dep.route_id, {})
        rname = format_route_name(rrow)
        print(f"{i:2d}. {dep.departure_time}  {rname}  (trip_id={dep.trip_id})")

    # Karte
    if not ask_yes_no("\nRoute auf Karte anzeigen?"):
        return

    n = input("Welche Nummer (z.B. 1): ").strip()
    if not n.isdigit() or not (1 <= int(n) <= len(deps)):
        print("Ungültige Nummer.")
        return

    chosen = deps[int(n) - 1]
    header("Karte wird erstellt")

    seq = trip_stop_sequence(GTFS_ZIP_PATH, chosen.trip_id)
    ordered_stop_ids = [sid for _, sid in seq]

    build_map_from_stop_ids(
        stops_by_id=stops_by_id,
        ordered_stop_ids=ordered_stop_ids,
        out_file=MAP_FILE,
        zoom=MAP_ZOOM
    )

if __name__ == "__main__":
    main()
print("MAIN ENDE")

