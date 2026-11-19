# reservoir-storage-eo

## Description

Estimate how much water is stored in **Valle de Bravo**, the most important reservoir of Mexico City's Cutzamala System, from Sentinel-2 satellite images.

**No machine learning is used.** The estimate comes from image processing and one mathematical formula:

1. Sentinel-2 images of the lake are loaded from Copernicus, only inside the lake's bounding box, and converted to reflectance.
2. Days where clouds hide more than 5% of the lake are dropped.
3. NDWI (from the green and near-infrared bands) separates water from land. Otsu's method picks the cutoff, and the largest connected water region is the lake. Its pixels give the surface area in km².
4. An area–volume curve, `V = a · A^b`, turns that area into stored volume (hm³). `a` and `b` are two numbers fitted with a straight line in log space on dates where CONAGUA's SINA reported the storage. The curve is then tested on later dates (mean absolute error).

## Objective

Learn fundamental concepts of geospatial science and Earth observation: Python libraries and satellite imagery, including bands, STAC and the Copernicus API. It also provides a way to estimate the reservoir's storage, as the SINA API stopped providing data after April 23, 2025.

Due to time constraints, only Valle de Bravo is implemented, not the rest of the Cutzamala System.

## Conclusion

Imagery is more robust than I thought: using reflectance and other algorithms you can calculate and estimate sizes. There's no need for ML models for everything; a mathematical model was enough to make the calculations needed. Data also needs filters and gates, so only clean (clear) days are measured.

The full story (scope, roadmap, how each step was verified, learnings, and how AI was used) is in [Project_Overview.md](Project_Overview.md).

## Pipeline

```
Copernicus STAC ─► sentinel/          search Sentinel-2 L2A over the lake, cached by month
                ─► image_processing/  bands → reflectance → NDWI, cloud mask (SCL)
                ─► water_level/       water mask → area km² → measurements.csv
CONAGUA SINA    ─► water_level/labels.py   official storage → labels.csv
measurements + labels ─► water_level/model.py     fit the curve V = a · A^b → model.json (a and b)
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

## Getting started

A walkthrough from a fresh clone to the website running. The commands are for Windows PowerShell.

### 0. What you need

- **Python 3.11.** Check with `py -3.11 --version`. If it's missing, install it from [python.org](https://www.python.org/downloads/).
- **A free Copernicus Data Space account**, to download Sentinel-2 bands. Register at [dataspace.copernicus.eu](https://dataspace.copernicus.eu/).

### 1. Go to the project folder

The repo has an outer folder (the repo root) and this project folder inside it. **Every command below runs from the project folder**, `reservoir-storage-eo`:

```powershell
cd <repo root>\reservoir-storage-eo
```

### 2. Create the virtual environment

A virtual environment keeps this project's libraries apart from the rest of your computer. It goes one folder up, at the repo root:

```powershell
py -3.11 -m venv ..\.venv
```

This creates `..\.venv`. Commands below call its Python directly as `..\.venv\Scripts\python`, so you don't need to activate it.

### 3. Install the requirements

```powershell
..\.venv\Scripts\python -m pip install -r requirements.txt
```

`requirements.txt` has everything needed to run the project (pystac and odc-stac for the images, httpx for the APIs, scikit-image for Otsu, and so on). To work on the code, install `requirements-dev.txt` instead; it adds ruff (linter) and pytest.

Check it worked:

```powershell
..\.venv\Scripts\python -c "import odc.stac, skimage; print('ok')"
```

### 4. Add your Copernicus keys to `.env`

The images are read from Copernicus's S3 storage, which needs S3 keys (different from your login password).

1. Generate an access key and a secret key in the Copernicus Data Space S3 keys manager (signed in with your account). Save the secret: it's shown only once.
2. Copy the template to `.env`:

   ```powershell
   Copy-Item env-template .env
   ```

3. Open `.env` and fill in the three values:

   ```
   ENDPOINT=eodata.dataspace.copernicus.eu
   ACCESS_KEY=<your access key>
   SECRET_KEY=<your secret key>
   ```

`.env` is gitignored. Never commit it or share it.

### 5. Measure the lake

```powershell
..\.venv\Scripts\python -m scripts.water_level.measure 2019 1 2025 10
```

For every month from January 2019 to October 2025, this finds the Sentinel-2 passes over the lake, drops the cloudy ones and measures the water area. Results go to `scripts/water_level/data/measurements.csv`, one month at a time.

This is the slow step: a few minutes per month, so a few hours for the full range. You can stop it with Ctrl+C at any time. Running the same command again skips the months already measured and carries on.

The fit in step 6 tests on dates from 2024 onwards, so measure both before and after January 2024.

### 6. Fit the area–volume curve

```powershell
..\.venv\Scripts\python -m scripts.water_level.model
```

This downloads CONAGUA's reported storage for each measured date (cached in `labels.csv`), fits `V = a · A^b` on the dates before 2024, and prints its error on the dates after. The two numbers go to `scripts/water_level/data/model.json`. Takes seconds.

### 7. Run the website

```powershell
..\.venv\Scripts\python -m website.server
```

Open http://localhost:8000, pick a month and click **Estimate**. Months you measured in step 5 show instantly. A new month is measured on the spot, which takes a few minutes. Stop the server with Ctrl+C.

### Troubleshooting

- **`No module named scripts`**: you're not in the project folder. `cd` into `reservoir-storage-eo` and run it again.
- **Access denied / 403 reading bands**: `.env` is missing, or the keys are wrong or expired. Check step 4.
- **`model.json is missing`** on the website: run step 6 first.
- **Empty chart on the website**: no months measured yet. Run step 5.

## Commands at a glance

Once set up, these are the commands, in order. Each one caches its results in its stage's `data/` folder, so running it again only does the new work.

| Step | Command | What it does | Time |
|------|---------|--------------|------|
| 1. Measure | `..\.venv\Scripts\python -m scripts.water_level.measure 2019 1 2025 10` | Measures the lake's water area in every Sentinel-2 pass from Jan 2019 to Oct 2025 → `measurements.csv`. Months already measured are skipped. | Minutes per new month |
| 2. Fit | `..\.venv\Scripts\python -m scripts.water_level.model` | Downloads CONAGUA's storage for the measured dates, fits the curve `V = a · A^b` and prints its test error → `model.json` (just `a` and `b`) | Seconds |
| 3. Estimate | `..\.venv\Scripts\python -m scripts.water_level.estimate 2025 10` | Estimates one month's storage and % of NAMO | Seconds if measured |
| 4. Website | `..\.venv\Scripts\python -m website.server` | Opens the web UI at http://localhost:8000: pick a month and see its estimate. Stop it with Ctrl+C. | — |

Measuring needs the `.env` keys. Estimating and the website need `model.json` from the fit. The website measures new months by itself, the same way the Measure step does.
