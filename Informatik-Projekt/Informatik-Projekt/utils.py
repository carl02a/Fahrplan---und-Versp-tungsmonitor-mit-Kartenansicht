# utils.py

from datetime import date, datetime

WEEKDAY_KEYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

def today_date() -> date:
    return date.today()

def yyyymmdd(d: date) -> str:
    return f"{d.year:04d}{d.month:02d}{d.day:02d}"

def weekday_key(d: date) -> str:
    return WEEKDAY_KEYS[d.weekday()]

def now_seconds() -> int:
    n = datetime.now()
    return n.hour * 3600 + n.minute * 60 + n.second

def parse_gtfs_time_to_seconds(t: str) -> int: # GFTS kann mehr als 24:00:00 enthalten
    hh, mm, ss = t.split(":")
    return int(hh) * 3600 + int(mm) * 60 + int(ss)

def format_seconds_hhmm(sec: int) -> str:
    hh = sec // 3600
    mm = (sec % 3600) // 60
    return f"{hh:02d}:{mm:02d}"
