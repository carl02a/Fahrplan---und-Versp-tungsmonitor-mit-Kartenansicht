# stops.py

from typing import Dict, List, Tuple
from models import Stop
from gtfs_zip import iter_rows

def load_stops(zip_path: str) -> Dict[str, Stop]:
    stops: Dict[str, Stop] = {}
    for row in iter_rows(zip_path, "stops.txt"):
        sid = (row.get("stop_id") or "").strip()
        name = (row.get("stop_name") or "").strip()
        lat = row.get("stop_lat")
        lon = row.get("stop_lon")
        if not sid or not name or lat is None or lon is None:
            continue
        try:
            stops[sid] = Stop(sid, name, float(lat), float(lon))
        except ValueError:
            continue
    return stops

def search_stops(stops: Dict[str, Stop], query: str, limit: int = 10) -> List[Tuple[str, str]]:
    q = query.strip().lower()
    matches: List[Tuple[str, str]] = []
    for sid, s in stops.items():
        if q in s.stop_name.lower():
            matches.append((sid, s.stop_name))
    matches.sort(key=lambda x: (len(x[1]), x[1]))
    return matches[:limit]