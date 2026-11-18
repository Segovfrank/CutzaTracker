import csv
import sys
import time

import numpy as np


from ..image_processing import band_loader
from .constants import data_dir
from .extent import clear_fraction, load_extent
from .scenes import load_month
from .water import area_km2, water_mask


measurements_csv = data_dir / "measurements.csv"
FIELDS = ["date", "area_km2", "clear_fraction", "threshold"]
MIN_CLEAR = 0.95

def measure_scene(ndwi: np.ndarray, clear: np.ndarray, extent: np.ndarray) -> dict:
    fraction = round(clear_fraction(clear, extent), 4)
    if fraction < MIN_CLEAR:
        return { "area_km2": "", "clear_fraction": fraction, "threshold": "" }
    lake, threshold = water_mask(ndwi, clear)
    return { "area_km2": round(area_km2(lake), 3), "clear_fraction": fraction, "threshold": round(threshold, 3) }

def measure_month(year: int, month: int) -> list[dict]:
    loaded = load_month(year, month)
    if loaded is None:
        return []
    ndwi, clear = loaded
    extent = load_extent()
    
    rows = []
    for t in ndwi.time.values:
        row = {"date": np.datetime_as_string(t, unit="D")}
        measurement = measure_scene(ndwi.sel(time=t).values, clear.sel(time=t).values, extent)
        row.update(measurement)
        rows.append(row)
    return rows

def read_measurements() -> list[dict]:
    rows = []
    if not measurements_csv.exists():
        return rows
    
    with open(measurements_csv, newline="") as file:
        for row in csv.DictReader(file):
            rows.append(row)
    return rows

def save_measurements(rows: list[dict]) -> None:
    is_new = not measurements_csv.exists()
    with open(measurements_csv, "a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        if is_new:
            writer.writeheader()
        writer.writerows(rows)
        
def next_month(year: int, month: int) -> tuple[int, int]:
    if month == 12:
        return year + 1, 1
    return year, month + 1

def main():
    numbers = []
    for text in sys.argv[1:]:
        numbers.append(int(text))
    year, month = numbers[0], numbers[1]
    last = (year, month)
    if len(numbers) == 4:
        last = (numbers[2], numbers[3])
        
    band_loader.configure_s3()
    done = set()
    for row in read_measurements():
        date = row["date"][:7] # yyyy-mm format
        done.add(date)
    
    while (year, month) <= last:
        key = f"{year}-{month:02d}"
        if key in done:
            print(f"{key}  already measured")
        else:
            start = time.time()
            rows = measure_month(year, month)
            save_measurements(rows)
            measured = 0
            for row in rows:
                if row["area_km2"] != "":
                    measured += 1
            print(f"{key}  {len(rows)} scenes, {measured} measured  ({time.time() - start:.0f} s)", flush=True)
        year, month = next_month(year, month)
        
if __name__ == "__main__":
    main()