# cli.py

"""
cli.py

Aufgabe:
    Dieses Modul stellt die textbasierte Benutzerschnittstelle bereit.
    Es verarbeitet Nutzereingaben und formatiert Ausgaben für die Konsole.

Zentrale Aufgaben:
    - Abfrage von Texteingaben (z. B. Bahnhofssuche)
    - Anzeige von Auswahllisten
    - Darstellung von Abfahrtsinformationen

Hinweise:
    - Dieses Modul enthält bewusst keine Fachlogik.
    - Es fungiert ausschließlich als Schnittstelle zwischen Nutzer und Backend.
"""

from typing import List, Tuple

def header(title: str) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

def choose_from_list(options: List[Tuple[str, str]], prompt: str) -> int:
    """
    options: list of (id, name)
    Returns index (0-based) or -1 if invalid
    """
    print()
    for i, (_, name) in enumerate(options, start=1):
        print(f"{i:2d}. {name}")
    val = input(f"\n{prompt} ").strip()
    if not val.isdigit():
        return -1
    idx = int(val) - 1
    if idx < 0 or idx >= len(options):
        return -1
    return idx

def ask_yes_no(prompt: str) -> bool:
    v = input(prompt + " (y/n): ").strip().lower()
    return v == "y"