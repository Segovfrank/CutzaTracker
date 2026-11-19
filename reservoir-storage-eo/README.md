# reservoir-storage-eo

## Description

Estimate how much water is stored in the reservoirs of Mexico City's Cutzamala System, starting with **Valle de Bravo**, from Sentinel-2 satellite images. The satellite measures the lake's surface area. An area–volume curve, `V = a · A^b`, turns that area into stored volume. The curve is fitted and validated against CONAGUA's official SINA records.

## Objective

Learn the fundamentals of geospatial science and Earth observation (bands, STAC, the Copernicus API) by building something useful: an estimate of Valle de Bravo's storage, since CONAGUA's SINA API has published no data after April 23, 2025.

## Conclusion

Satellite imagery is more robust than I expected: reflectance, NDWI and a simple fitted curve are enough to estimate the reservoir's storage, with no ML model needed. The key was filtering the data, so only days with at least 95% of the lake clear are measured.

The full story (scope, roadmap, how each step was verified, learnings, and how AI was used) is in [Project_Overview.md](Project_Overview.md).

## Pipeline

```
Copernicus STAC ─► sentinel/          search Sentinel-2 L2A over the lake, cached by month
                ─► image_processing/  bands → reflectance → NDWI, cloud mask (SCL)
                ─► water_level/       water mask → area km² → measurements.csv
CONAGUA SINA    ─► water_level/labels.py   official storage → labels.csv
measurements + labels ─► water_level/model.py     fit V = a · A^b → model.json
new month             ─► water_level/estimate.py  storage hm³ and % of NAMO
```

## Project organization

```
├── docs/
│   ├── collection-fetch-hld.canvas   <- How Sentinel collections are fetched and cached
│   └── api_usage/                    <- Copernicus STAC and CONAGUA SINA API notes and samples
├── scripts/
│   ├── sentinel/          <- STAC search client and month cache
│   ├── image_processing/  <- Band loading, reflectance, NDWI, renders
│   ├── water_level/       <- Water area, SINA labels, area–volume model, estimates
│   └── utils/             <- Date and JSON helpers
├── website/               <- Web UI: server.py plus the page
├── Project_Overview.md    <- Objective, roadmap, verification, learnings
├── env-template           <- Copy to .env and add your Copernicus keys
├── requirements.txt       <- Runtime dependencies
├── requirements-dev.txt   <- Runtime + ruff and pytest
└── pyproject.toml         <- Project metadata and ruff settings
```

Each `scripts/*/data/` folder holds that stage's cache and outputs. They're gitignored.

## Setup

You need Python 3.11 and Copernicus Data Space S3 keys. Run everything from this folder (`reservoir-storage-eo`); the virtual environment lives one folder up, at the repo root.

1. Create the virtual environment and install the requirements:

   ```powershell
   py -3.11 -m venv ..\.venv
   ..\.venv\Scripts\python -m pip install -r requirements.txt       # to run the project
   ..\.venv\Scripts\python -m pip install -r requirements-dev.txt   # optional: adds ruff and pytest
   ```

2. Add your Copernicus S3 keys. Copy `env-template` to `.env` and fill in `ENDPOINT`, `ACCESS_KEY` and `SECRET_KEY`. `.env` is gitignored; never commit it.

   ```powershell
   Copy-Item env-template .env
   ```

## Run

Run the steps in order. Each one caches its results in its stage's `data/` folder, so running it again only does the new work.

| Step | Command | What it does | Time |
|------|---------|--------------|------|
| 1. Measure | `..\.venv\Scripts\python -m scripts.water_level.measure 2019 1 2025 10` | Measures the lake's water area in every Sentinel-2 pass from Jan 2019 to Oct 2025 → `measurements.csv`. Months already measured are skipped. | Minutes per new month |
| 2. Fit | `..\.venv\Scripts\python -m scripts.water_level.model` | Downloads CONAGUA's storage for the measured dates, fits `V = a · A^b` and prints its test error → `model.json` | Seconds |
| 3. Estimate | `..\.venv\Scripts\python -m scripts.water_level.estimate 2025 10` | Estimates one month's storage and % of NAMO | Seconds if measured |
| 4. Website | `..\.venv\Scripts\python -m website.server` | Opens the web UI at http://localhost:8000: pick a month and see its estimate. Stop it with Ctrl+C. | — |

Step 1 needs the `.env` keys. Steps 3 and 4 need `model.json` from step 2. The website measures new months by itself, the same way step 1 does.
