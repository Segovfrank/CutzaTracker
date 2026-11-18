# reservoir-storage-eo

## Description

Estimate how much water is stored in the reservoirs of Mexico City's Cutzamala System, starting with **Valle de Bravo**, from Sentinel-2 satellite images. The satellite measures the lake's surface area. An area–volume curve, `V = a · A^b`, turns that area into stored volume. The curve is fitted and validated against CONAGUA's official SINA records.

## Objectives

1. **Estimate reservoir storage from satellite imagery.** Estimate Valle de Bravo's stored volume (hm³) from its Sentinel-2 water surface area (km²), calibrated and validated against SINA records (2019 to April 2025).
2. **Fill the public data gap.** SINA has no data after April 23, 2025.
3. **Learn by doing:** Copernicus, STAC and image processing, applied to a real estimation model.

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
├── requirements.txt       <- Runtime dependencies
├── requirements-dev.txt   <- Runtime + ruff and pytest
└── pyproject.toml         <- Project metadata and ruff settings
```

Each `scripts/*/data/` folder holds that stage's cache and outputs. They're gitignored.

## Setup

The virtual environment lives one folder up, at the repo root.

```powershell
py -3.11 -m venv ..\.venv
..\.venv\Scripts\python -m pip install -r requirements-dev.txt
```

Reading bands from Copernicus S3 needs keys in `.env` (`ENDPOINT`, `ACCESS_KEY`, `SECRET_KEY`).

## Run

From this folder:

```powershell
..\.venv\Scripts\python -m scripts.water_level.measure 2019 1 2025 10   # measure lake area per scene
..\.venv\Scripts\python -m scripts.water_level.model                    # fit and test the curve
..\.venv\Scripts\python -m scripts.water_level.estimate 2025 10         # estimate one month
```
