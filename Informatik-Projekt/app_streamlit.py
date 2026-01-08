import streamlit as st
import folium
from streamlit_folium import folium_static

# Eure Module (Backend)
import stops
import departures
import cache_db

FEED_ZIP = "data/feed.zip"
DB_PATH = "gtfs_cache.db"

@st.cache_data(show_spinner=True)

def cached_departures(stop_id: str, limit: int):
    from calendar_ import active_service_ids
    from utils import today_date

    active_services = active_service_ids(FEED_ZIP, today_date())

    if not active_services:
        st.warning("Hinweis: Keine aktiven Services für HEUTE im Feed gefunden. Fallback ohne Kalenderfilter.")
        active_trip_route = departures.build_trip_route_map_all(FEED_ZIP)
    else:
        active_trip_route = departures.build_active_trip_route_map(FEED_ZIP, active_services)

    # 3) DB-Connection holen
    con = cache_db.connect(DB_PATH)
    cache_db.init_db(con)

    # 4) Abfahrten aus Cache holen
    return cache_db.get_next_departures_cached(con, stop_id, active_trip_route, limit)


st.set_page_config(layout="wide", page_title="GTFS Mobility Dashboard", page_icon="🚆")

st.title("🚆 GTFS Mobility Dashboard (Deutschland)")
st.write("APP LÄUFT ✅ (bis hierhin)")

# ---------------------------
# Helpers: kompatibel zu mehreren Backend-Varianten
# ---------------------------

def stop_display_name(s):
    # kompatibel zu Stop-Modellen mit name ODER stop_name
    return getattr(s, "name", None) or getattr(s, "stop_name", None) or str(getattr(s, "stop_id", "STOP"))

def _stop_obj_from_result(stops_dict, item):

    """
    Unterstützt 2 mögliche Formen:
    1) item ist Stop-Objekt mit .stop_id / .name / .lat / .lon
    2) item ist Tuple (stop_id, stop_name) -> Stop-Objekt aus stops_dict ziehen
    """
    # Fall 1: Stop-Objekt
    if hasattr(item, "stop_id") and hasattr(item, "lat") and hasattr(item, "lon"):
        return item

    # Fall 2: Tuple
    if isinstance(item, (tuple, list)) and len(item) >= 1:
        sid = item[0]
        return stops_dict.get(sid)

    return None


def _stop_label(item):
    """Erstellt Text für die Trefferliste."""
    if hasattr(item, "name"):
        return f"{item.name} (id={item.stop_id})"
    if isinstance(item, (tuple, list)) and len(item) >= 2:
        return f"{item[1]} (id={item[0]})"
    if isinstance(item, (tuple, list)) and len(item) == 1:
        return f"{item[0]}"
    return str(item)


def _dep_label(d):
    """Erstellt Text für Abfahrts-Auswahl."""
    # Deine Departure-Objekte könnten unterschiedliche Attribute haben
    time = getattr(d, "planned_time", None) or getattr(d, "departure_time", None) or "??:??"
    line = getattr(d, "line_name", None) or getattr(d, "route_name", None) or getattr(d, "route_id", None) or "Linie"
    dest = getattr(d, "destination", None) or ""
    delay = getattr(d, "delay_minutes", None)

    txt = f"{time} – {line}"
    if dest:
        txt += f" → {dest}"
    if delay is not None and delay > 0:
        txt += f" (+{delay} min)"
    return txt


def _route_coords_from_trip(stops_dict, trip_id):
    """
    Route-Koordinaten bauen (Stop-zu-Stop), kompatibel mit deinem jetzigen Stand:
    - nutzt cache_db.trip_stop_sequence(zip, trip_id)
    - wandelt stop_id -> (lat, lon) über stops_dict um
    """
    seq = cache_db.trip_stop_sequence(FEED_ZIP, trip_id)
    ordered_stop_ids = [sid for _, sid in seq]

    coords = []
    for sid in ordered_stop_ids:
        s = stops_dict.get(sid)
        if not s:
            continue
        coords.append((s.lat, s.lon))
    return coords


# ---------------------------
# Caching (Streamlit)
# ---------------------------

@st.cache_data(show_spinner=True)
def cached_load_stops():
    return stops.load_stops(FEED_ZIP)

STOPS_DICT = cached_load_stops()

# ---------------------------
# Sidebar: Stop-Suche
# ---------------------------

st.sidebar.header("Stationssuche (GTFS)")
query = st.sidebar.text_input("Bahnhof/Halt eingeben:", value="Mannheim")

results = stops.search_stops(STOPS_DICT, query, limit=25)

if not results:
    st.sidebar.warning("Keine Treffer. Bitte Suchbegriff ändern.")
    st.stop()

labels = [_stop_label(x) for x in results]
selected_idx = st.sidebar.selectbox("Treffer auswählen:", range(len(labels)), format_func=lambda i: labels[i])

selected_item = results[selected_idx]
selected_stop = _stop_obj_from_result(STOPS_DICT, selected_item)

if selected_stop is None:
    st.sidebar.error("Konnte Stop nicht auflösen (Format unerwartet).")
    st.stop()

st.sidebar.markdown("---")
st.sidebar.subheader("Ausgewählt:")
st.sidebar.write(f"**{stop_display_name(selected_stop)}**")
st.sidebar.caption(f"stop_id: {selected_stop.stop_id}")

# ---------------------------
# Hauptbereich
# ---------------------------

col1, col2 = st.columns([1, 2])

with col1:
    st.header("Nächste Abfahrten")
    deps = []
    try:
        deps = cached_departures(selected_stop.stop_id, limit=20)
    except Exception as e:
        st.error("Fehler beim Laden der Abfahrten aus GTFS:")
        st.code(str(e))
        st.stop()

    if not deps:
        st.info("Keine Abfahrten gefunden (Datum/Wochentag/Feed).")
        st.stop()

    dep_labels = [_dep_label(d) for d in deps]

dep_labels = [_dep_label(d) for d in deps]

selected_dep_idx = st.selectbox(
    "Fahrt auswählen:",
    list(range(len(dep_labels))),
    format_func=lambda i: dep_labels[i],
    index=0
)

if selected_dep_idx is None:
    st.stop()

selected_dep = deps[int(selected_dep_idx)]

trip_id = getattr(selected_dep, "trip_id", None)
if not trip_id:
    st.warning("Diese Abfahrt hat keine trip_id → keine Route möglich.")
    st.stop()

st.caption(f"trip_id: {trip_id}")

with col2:
    st.header("Streckenverlauf (Karte)")

    # Karte initialisieren auf den ausgewählten Stop
    m = folium.Map(location=[selected_stop.lat, selected_stop.lon], zoom_start=12, tiles="CartoDB dark_matter")

    with st.spinner("Route wird berechnet… (kann bei großen Feeds etwas dauern)"):
        coords = _route_coords_from_trip(STOPS_DICT, trip_id)

    if coords and len(coords) >= 2:
        folium.PolyLine(coords, weight=5, opacity=0.85).add_to(m)
        folium.Marker(coords[0], popup="Start", icon=folium.Icon(color="green")).add_to(m)
        folium.Marker(coords[-1], popup="Ende", icon=folium.Icon(color="red")).add_to(m)
    else:
        folium.Marker([selected_stop.lat, selected_stop.lon], popup=selected_stop.name).add_to(m)
        st.info("Für diese Fahrt konnten keine ausreichenden Route-Koordinaten ermittelt werden.")

    folium_static(m, width=900, height=520)

st.markdown("---")
st.caption("Hinweis: Der verwendete Deutschland-GTFS-Feed enthält keine shapes.txt → Route wird Stop-zu-Stop visualisiert.")