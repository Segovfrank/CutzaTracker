import sys

import numpy as np

from ..image_processing import band_loader
from ..utils import json_utils
from .constants import NAMO_MAX_HM3, data_dir
from .labels import load_labels
from .measure import measure_month
from .model import predict

def estimate_month(year: int, month: int) -> list[float]:
    model = json_utils.read_json("model", data_dir)
    rows = measure_month(year, month)
    
    days = []
    for row in rows:
        days.append(row["date"])
    official = load_labels(days)
    
    estimates = []
    for row in rows:
        day = row["date"]
        if row["area_km2"] == "":
            print(f"{day}  skipped: only {row['clear_fraction']:.0%} of the lake is clear")
            continue
        estimate = float(predict(row["area_km2"], model["a"], model["b"]))
        line = f"{day}  {row['area_km2']:6.2f} km2  ->  {estimate:6.1f} hm3  {estimate / NAMO_MAX_HM3:6.1%}"
        if day in official:
            line += f"   CONAGUA {official[day]:6.1f} hm3  off by {estimate - official[day]:+6.1f}"
        print(line)
        estimates.append(estimate)
    return estimates

def main():
    year, month = int(sys.argv[1]), int(sys.argv[2])
    band_loader.configure_s3()
    estimates = estimate_month(year, month)
    if len(estimates) == 0:
        print(f"no clear scene in {year}-{month:02d}")
        return
    middle = float(np.median(estimates))
    print(f"{year}-{month:02d}: about {middle:.0f} hm3, {middle / NAMO_MAX_HM3:.0%} of NAMO (median of {len(estimates)} dates)")

if __name__ == "__main__":
    main()