# config.py

# config.py
"""
config.py

Aufgabe:
    Zentrale Konfigurationsdatei des Projekts. Sie enthält Pfade, Limits und
    Standardwerte, die von mehreren Modulen gemeinsam genutzt werden.

Typische Inhalte:
    - Pfad zur GTFS-ZIP-Datei
    - Standard-Limits für Abfahrten
    - Cache- und Ausgabepfade
    - Debug-Optionen

Hinweise:
    - Änderungen an dieser Datei beeinflussen das gesamte Projektverhalten.
"""

GTFS_ZIP_PATH = "data/feed.zip"
CACHE_DB_PATH = "gtfs_cache.db"

DEFAULT_RESULTS_LIMIT = 12
DEFAULT_DEPARTURES_LIMIT = 12

MAP_FILE = "route_map.html"
MAP_ZOOM = 6
