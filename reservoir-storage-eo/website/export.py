"""Export the showcase as static JSON for GitHub Pages (no Python runs there).

Run from the project folder:  python -m website.export
Writes website/data/history.json and website/data/months/YYYY-MM.json, the same data /api/history and
/api/estimate return. Only months already in measurements.csv are exported: this never measures.
"""
import json

from scripts.water_level.measure import read_measurements
from website.server import SITE_DIR, estimate, history

SHOWCASE_FROM = "2025-01"
out_dir = SITE_DIR / "data"


def write(path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def main():
    measured = set()
    for row in read_measurements():
        key = row["date"][:7]
        if key >= SHOWCASE_FROM:
            measured.add(key)

    months = sorted(measured)
    for key in months:
        year, month = (int(part) for part in key.split("-"))
        write(out_dir / "months" / f"{key}.json", estimate(year, month))
        print(f"{key}  exported")

    data = history()
    data["showcase_months"] = months
    write(out_dir / "history.json", data)
    print(f"{len(months)} months exported to {out_dir}")


if __name__ == "__main__":
    main()
