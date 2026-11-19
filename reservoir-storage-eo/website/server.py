"""Local web UI for the storage estimate.

Run from the project folder:  python -m website.server
Then open http://localhost:8000
"""
import json
import statistics
import threading
from datetime import date
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import httpx

from scripts.image_processing import band_loader
from scripts.utils import json_utils
from scripts.water_level.constants import NAMO_MAX_HM3, data_dir
from scripts.water_level.labels import load_labels, read_labels
from scripts.water_level.measure import measure_month, read_measurements, save_measurements
from scripts.water_level.model import predict

SITE_DIR = Path(__file__).parent
PORT = 8000
FIRST_MONTH = (2019, 1)
# One month at a time: the S3 reads are heavy and measurements.csv is appended to
pipeline_lock = threading.Lock()


def parse_month(text: str) -> tuple[int, int]:
    # Input from the browser: only "YYYY-MM" inside the range we have data for
    try:
        year, month = (int(part) for part in text.split("-"))
    except ValueError:
        raise ValueError("month must look like 2025-10")
    today = date.today()
    if not 1 <= month <= 12 or not FIRST_MONTH <= (year, month) <= (today.year, today.month):
        raise ValueError(f"month must be between {FIRST_MONTH[0]}-{FIRST_MONTH[1]:02d} and {today:%Y-%m}")
    return year, month


def to_float(value) -> float | None:
    if value == "" or value is None:
        return None
    return float(value)


def load_model() -> dict:
    model = json_utils.read_json("model", data_dir)
    if "a" not in model:
        raise RuntimeError("model.json is missing: run python -m scripts.water_level.model first")
    return model


def month_scenes(year: int, month: int) -> tuple[list[dict], str]:
    key = f"{year}-{month:02d}"
    cached = [row for row in read_measurements() if row["date"].startswith(key)]
    if cached:
        return cached, "cache"
    with pipeline_lock:
        # Another request may have measured it while we waited
        cached = [row for row in read_measurements() if row["date"].startswith(key)]
        if cached:
            return cached, "cache"
        rows = measure_month(year, month)
        save_measurements(rows)
        return rows, "satellite"


def estimate(year: int, month: int) -> dict:
    model = load_model()
    rows, source = month_scenes(year, month)

    days = []
    for row in rows:
        days.append(row["date"])
    try:
        official = load_labels(days)
        conagua_error = None
    except httpx.HTTPError as error:
        official = {}
        conagua_error = str(error)

    scenes = []
    estimates = []
    reported = []
    for row in rows:
        area = to_float(row["area_km2"])
        storage = None
        if area is not None:
            storage = float(predict(area, model["a"], model["b"]))
            estimates.append(storage)
        conagua = official.get(row["date"])
        if conagua is not None:
            reported.append(conagua)
        scenes.append({
            "date": row["date"],
            "clear_fraction": to_float(row["clear_fraction"]),
            "area_km2": area,
            "estimate_hm3": storage,
            "conagua_hm3": conagua,
        })

    return {
        "month": f"{year}-{month:02d}",
        "source": source,
        "namo_hm3": NAMO_MAX_HM3,
        "model": model,
        "scenes": scenes,
        "estimate_hm3": statistics.median(estimates) if estimates else None,
        "conagua_hm3": statistics.median(reported) if reported else None,
        "conagua_error": conagua_error,
    }


def history() -> dict:
    # Monthly medians from what is already measured and cached; no network calls
    model = load_model()
    labels = read_labels()
    estimates_by_month = {}
    conagua_by_month = {}
    for row in read_measurements():
        key = row["date"][:7]
        area = to_float(row["area_km2"])
        if area is not None:
            estimates_by_month.setdefault(key, []).append(float(predict(area, model["a"], model["b"])))
        label = labels.get(row["date"])
        if label and label["storage_hm3"] != "":
            conagua_by_month.setdefault(key, []).append(float(label["storage_hm3"]))

    months = []
    if estimates_by_month:
        year, month = FIRST_MONTH
        last = max(estimates_by_month)
        while f"{year}-{month:02d}" <= last:
            months.append(f"{year}-{month:02d}")
            year, month = (year + 1, 1) if month == 12 else (year, month + 1)

    def medians(by_month: dict) -> list[float | None]:
        out = []
        for key in months:
            values = by_month.get(key)
            out.append(statistics.median(values) if values else None)
        return out

    return {
        "months": months,
        "estimate_hm3": medians(estimates_by_month),
        "conagua_hm3": medians(conagua_by_month),
        "latest": months[-1] if months else None,
        "namo_hm3": NAMO_MAX_HM3,
        "model": model,
    }


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(SITE_DIR), **kwargs)

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/api/history":
            self.run(history)
        elif url.path == "/api/estimate":
            query = parse_qs(url.query)
            try:
                year, month = parse_month(query.get("month", [""])[0])
            except ValueError as error:
                self.send_json({"error": str(error)}, 400)
                return
            self.run(lambda: estimate(year, month))
        elif url.path == "/Project_Overview.md":
            # Lives in the project root, outside the served folder
            body = (SITE_DIR.parent / "Project_Overview.md").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif url.path.endswith(".py"):
            self.send_error(404)
        else:
            super().do_GET()

    def run(self, job):
        try:
            self.send_json(job(), 200)
        except Exception as error:  # report pipeline failures to the page instead of dropping the connection
            self.log_error("API error: %r", error)
            self.send_json({"error": str(error)}, 500)

    def send_json(self, data: dict, status: int):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    band_loader.configure_s3()
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Serving on http://localhost:{PORT}")
    server.serve_forever()
