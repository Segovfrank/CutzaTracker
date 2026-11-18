import csv

import httpx

from .constants import DAM_ID, NAMO_MAX_HM3, data_dir

SINA_URL = "https://sinav30.conagua.gob.mx:8080/PresasPG/presas/reporte/"
labels_csv = data_dir / "labels.csv"
FIELDS = ["date", "storage_hm3", "elevation_m"]

def fetch_water_level(client: httpx.Client, day: str) -> dict:
    response = client.get(SINA_URL + day)
    response.raise_for_status()
    for dam in response.json():
        if dam["clavesih"] == DAM_ID:
            return { "date": day, "storage_hm3": dam["almacenaactual"], "elevation_m": dam["elevacionactual"] }
    # This means no report of that particular day
    return { "date": day, "storage_hm3": "", "elevation_m": "" }

# Load from cache
def read_labels() -> dict[str, dict]:
    labels = {}
    if not labels_csv.exists():
        return labels
    with open(labels_csv, newline="") as file:
        # Get the labels as a dict of string
        for row in csv.DictReader(file):
            labels[row["date"]] = row
    return labels

def save_labels(rows: list[dict]):
    data_dir.mkdir(parents=True, exist_ok=True)
    is_new = not labels_csv.exists()
    with open(labels_csv, "a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        if is_new:
            writer.writeheader()
        writer.writerows(rows)
        
def load_labels(days: list[str]) -> dict[str, float]:
    known = read_labels()
    missing = []
    for day in days:
        if day not in known:
            missing.append(day)
            
    if len(missing) > 0:
        fetched = []
        with httpx.Client(timeout=30) as client:
            for day in missing:
                row = fetch_water_level(client, day)
                fetched.append(row)
                known[day] = row
            save_labels(fetched)
            print(f"fetched {len(fetched)} labels from SINA")
        
    storage = {}
    for day in days:
        value = known[day]["storage_hm3"]
        if value != "":
            storage[day] = float(value)
    return storage

if __name__ == "__main__":
    days = ["2024-01-31", "2024-06-26", "2025-04-23", "2025-10-27"]
    storage = load_labels(days)
    for day in days:
        if day in storage:
            print(f"{day}  {storage[day]:7.2f} hm3  {storage[day] / NAMO_MAX_HM3:6.1%} of NAMO")
        else:
            print(f"{day}  no SINA report")