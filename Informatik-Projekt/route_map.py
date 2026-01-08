# route_map.py

"""
route_map.py

Aufgabe:
    Dieses Modul ist für die Visualisierung von Routen zuständig. Es erzeugt
    eine interaktive Karte auf Basis von OpenStreetMap und zeichnet die Route
    einer ausgewählten Fahrt als Polyline.

Verwendete Bibliotheken:
    - folium
    - webbrowser

Zentrale Aufgaben:
    - Erzeugung einer HTML-Karte
    - Darstellung von Haltestellen-Markern
    - Zeichnen der Verbindungslinie zwischen Haltestellen

Hinweise:
    - Da der verwendete GTFS-Feed keine shapes.txt enthält, erfolgt die
      Darstellung Stop-zu-Stop anhand der Haltestellenkoordinaten.
"""

from typing import Dict, List, Tuple
import folium
import webbrowser

from models import Stop

def build_map_from_stop_ids(
    stops_by_id: Dict[str, Stop],
    ordered_stop_ids: List[str],
    out_file: str,
    zoom: int = 6
) -> None:
    coords: List[Tuple[float, float]] = []
    labels: List[str] = []

    for sid in ordered_stop_ids:
        s = stops_by_id.get(sid)
        if not s:
            continue
        coords.append((s.lat, s.lon))
        labels.append(s.stop_name)

    if not coords:
        print("Keine Koordinaten gefunden – Karte kann nicht erstellt werden.")
        return

    m = folium.Map(location=[coords[0][0], coords[0][1]], zoom_start=zoom)

    folium.PolyLine(coords, tooltip="Route").add_to(m)

    for (lat, lon), label in zip(coords, labels):
        folium.Marker([lat, lon], tooltip=label).add_to(m)

    m.save(out_file)
    print(f"Karte gespeichert: {out_file}")
    webbrowser.open(out_file)

    """
    Erstellt eine interaktive Karte (OpenStreetMap) und zeichnet die Route als Polyline.

    Zweck:
        Visualisiert eine Fahrt/Route anhand von Koordinaten aus stops.txt.
        Da der GTFS-Feed keine shapes.txt enthält, wird die Route Stop-zu-Stop gezeichnet.

    Parameter:
        stops_by_id (Dict[str, Stop]): Mapping stop_id -> Stop (enthält lat/lon).
        ordered_stop_ids (List[str]): Haltestellen in Reihenfolge der Route.
        out_file (str): Dateiname der erzeugten HTML-Karte.
        zoom (int): Start-Zoom der Karte.

    Ergebnis:
        - Speichert eine HTML-Datei mit Karte und Route.
        - Öffnet optional den Browser.

    Hinweise:
        - Marker können optional gesetzt werden (Start/Ziel oder alle Stops).
        - Für große Strecken kann die HTML-Datei sehr groß werden (normal bei Folium).
    """