from datetime import datetime, timezone

def parse(date: str) -> datetime:
    # Python 3.10 does not accept the trailing Z from iso date
    return datetime.fromisoformat(date.replace("Z", "+00:00"))

def to_stac_date(date: datetime) -> str:
    return date.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def get_latest_date(date_a: str, date_b) -> str:
    date_a_iso = parse(date_a)
    date_b_iso = parse(date_b)
    if date_a_iso > date_b_iso:
        return date_a
    else:
        return date_b
