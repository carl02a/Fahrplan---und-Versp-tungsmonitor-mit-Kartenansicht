# gtfs_zip.py

"""
gtfs_zip.py

Aufgabe:
    Dieses Modul kapselt den Zugriff auf den GTFS-Datensatz, der als ZIP-Datei
    vorliegt. Es stellt Hilfsfunktionen bereit, um CSV-Dateien innerhalb der ZIP
    speicherschonend zeilenweise zu lesen.

Verwendete Technologien:
    - zipfile
    - csv

Zentrale Aufgaben:
    - Streaming-Zugriff auf GTFS-Dateien
    - Vermeidung vollständigen Entpackens in den Arbeitsspeicher
    - Vereinheitlichter Zugriff auf unterschiedliche GTFS-Dateien

Hinweise:
    - Alle anderen Module greifen indirekt über dieses Modul auf GTFS-Daten zu.
"""

import csv
import zipfile
from typing import Dict, Iterator

def iter_rows(zip_path: str, filename: str) -> Iterator[Dict[str, str]]:
    with zipfile.ZipFile(zip_path, "r") as z:
        with z.open(filename, "r") as f:
            text_iter = (line.decode("utf-8-sig") for line in f)
            reader = csv.DictReader(text_iter)
            for row in reader:
                yield row

    """
    Liest eine GTFS-CSV-Datei direkt aus einer ZIP-Datei zeilenweise aus.

    Zweck:
        GTFS-Feeds können sehr groß sein. Statt Dateien zu entpacken oder vollständig
        in den RAM zu laden, wird hier ein Iterator verwendet, der Zeilen nacheinander
        liefert (Streaming).

    Parameter:
        zip_path (str): Pfad zur GTFS-ZIP-Datei (z. B. "data/feed.zip").
        filename (str): Name der GTFS-Datei innerhalb der ZIP (z. B. "stops.txt").

    Rückgabe:
        Iterator[Dict[str, str]]: Jede Zeile als Dictionary (Spaltenname -> Wert).

    Besonderheiten:
        - utf-8-sig entfernt ein mögliches BOM am Dateianfang.
        - Sehr RAM-schonend, da nicht alles auf einmal geladen wird.
    """

def has_file(zip_path: str, filename: str) -> bool:
    with zipfile.ZipFile(zip_path, "r") as z:
        return filename in z.namelist()
    
    """
    Prüft, ob eine bestimmte Datei innerhalb der GTFS-ZIP existiert.

    Zweck:
        Einige GTFS-Dateien sind optional (z. B. calendar_dates.txt, shapes.txt).
        Diese Funktion ermöglicht Feature-Fallbacks abhängig von der Verfügbarkeit.

    Parameter:
        zip_path (str): Pfad zur GTFS-ZIP.
        filename (str): Name der Datei in der ZIP (z. B. "calendar_dates.txt").

    Rückgabe:
        bool: True, wenn die Datei vorhanden ist, sonst False.
    """
    