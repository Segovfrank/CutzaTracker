# reservoir-storage-eo

Estimates the water stored in Valle de Bravo, the main reservoir of Mexico City's Cutzamala System, from Sentinel-2 satellite images. The [live site](https://segovfrank.github.io/CutzaTracker/) shows estimates from January 2025 to today.

## How it works

1. Load Sentinel-2 images of the lake from Copernicus and convert them to reflectance.
2. Skip days where clouds cover more than 5% of the lake.
3. Separate water from land with NDWI and Otsu's threshold, then measure the lake's area in km².
4. Convert the area to volume (hm³) with `V = a · A^b`, fitted against CONAGUA's reported storage.

## Objective

Learn fundamental concepts of geospatial science and Earth observation: Python libraries and satellite imagery, including bands, STAC and the Copernicus API. It also provides a way to estimate the reservoir's storage, as the SINA API stopped providing data after April 23, 2025.

Due to time constraints, only Valle de Bravo is implemented, not the rest of the Cutzamala System.

## Conclusion

Imagery is more robust than I thought: using reflectance and other algorithms you can calculate and estimate sizes. There's no need for ML models for everything; a mathematical model was enough to make the calculations needed. Data also needs filters and gates, so only clean (clear) days are measured.

The full story (scope, roadmap, how each step was verified, learnings, and how AI was used) is in [Project_Overview.md](reservoir-storage-eo/Project_Overview.md).

I set the direction and objective, and I implemented the STAC search and caching myself. From the band loader onwards I used AI (Claude) to help implement it and teach me the concepts. The website was built by AI.

## Pipeline

```
Copernicus STAC ─► sentinel/          search Sentinel-2 L2A over the lake, cached by month
                ─► image_processing/  bands → reflectance → NDWI, cloud mask (SCL)
                ─► water_level/       water mask → area km² → measurements.csv
CONAGUA SINA    ─► water_level/labels.py   official storage → labels.csv
measurements + labels ─► water_level/model.py     fit the curve V = a · A^b → model.json (a and b)
new month             ─► water_level/estimate.py  storage hm³ and % of NAMO
```

## Running it yourself

You need Python 3.11 and a free [Copernicus Data Space](https://dataspace.copernicus.eu/) account. From PowerShell:

```powershell
cd reservoir-storage-eo
py -3.11 -m venv ..\.venv
..\.venv\Scripts\python -m pip install -r requirements.txt
Copy-Item env-template .env   # then add your Copernicus S3 access and secret keys

..\.venv\Scripts\python -m scripts.water_level.measure 2019 1 2025 10   # measure the lake area
..\.venv\Scripts\python -m scripts.water_level.model                    # fit V = a · A^b
..\.venv\Scripts\python -m scripts.water_level.estimate 2025 10         # estimate one month
..\.venv\Scripts\python -m website.server                               # open http://localhost:8000
```

Measuring takes a few minutes per month. You can stop it with Ctrl+C and rerun it to continue. The fit is tested on dates from 2024 on, so measure months before and after January 2024.
