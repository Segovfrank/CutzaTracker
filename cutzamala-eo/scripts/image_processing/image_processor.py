import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from pystac import ItemCollection
import xarray as xr

from . import band_loader, indices, probe, reflectance, render
from .constants import LAKE_CENTER, RGB, RGB_N, renders_dir
from .item_collection_loader import load_collection

# Sentinel-2 pixel at 10m resolution
PIXEL_AREA_M2 = 10 * 10 
SCL = "SCL_20m"
# no data, defective, cloud shadow, cloud med, cloud, high, cirrus
BAD_SCL = [0, 1, 3, 8, 9, 10]
MIN_CLEAR = 0.95 # Threshold to discard an area

def clear_mask(scl: xr.DataArray) -> xr.DataArray:
    is_bad = scl.isin(BAD_SCL) # Check every pixel (filter according to the values in BAD_SCL)
    return ~is_bad

# ODC-Stac stacks the dates on the time axis, pixel aligned

def load_month_reflectance(items: ItemCollection) -> tuple[xr.Dataset, xr.DataArray]:
    asset = reflectance.shared_asset(items, "B04_10m")
    raw = band_loader.load_bands(items.items, RGB_N + [SCL])
    refl = reflectance.to_reflectance(raw[RGB_N], asset)
    clear = clear_mask(raw[SCL])
    return refl, clear

def save_date_images(one: xr.Dataset, water: xr.DataArray, day: str, output: Path) -> list[Path]:
    rgb_path = output / f"rgb_{day}.png"
    false_path = output / f"false_{day}.png"
    ndwi_path = output / f"ndwi_{day}.png"
    
    plt.imsave(rgb_path, render.to_rgb(one))
    plt.imsave(false_path, render.false_color(one))
    #vmin and vmax keep colors normalized between dates
    plt.imsave(ndwi_path, water.values, cmap="RdBu", vmin=-1, vmax=1)
    
    return [rgb_path, false_path, ndwi_path]

def log_date(one: xr.Dataset, water: xr.DataArray, clear: xr.DataArray, day: str):
    lon, lat = LAKE_CENTER
    lake_nir = probe.sample(one, lon, lat)["B08_10m"]
    
    clear_share = float(clear.mean())
    if clear_share < MIN_CLEAR:
        print(f"{day}  lake NIR {lake_nir:.3f}  clear {clear_share:6.1%}  too cloudy to measure")
        return
    
    is_water = (water > 0) & clear
    water_pixels = int(is_water.sum())
    km2 = water_pixels * PIXEL_AREA_M2 / 1_000_000
    
    print(f"{day}  lake NIR {lake_nir:.3f}  clear {clear_share:6.1%}  NDWI>0 {km2:5.2f} km2")
    
def save_grid(refl: xr.Dataset, output: Path) -> Path:
    rgb_bands = refl[RGB]
    stacked = rgb_bands.to_array("band")
    grid = stacked.plot.imshow(rgb="band", col="time", col_wrap=3, vmin=0, vmax=0.3)
    
    grid_path = output / "grid.png"
    grid.fig.savefig(grid_path)
    plt.close("all")
    return grid_path

def process_month(year: int, month: int) -> list[Path]:
    items = load_collection(year, month)
    
    # Guard for empty collections
    if len(items) == 0:
        print(f"No items for {year}-{month:02d}")
        return []
    
    refl, clear = load_month_reflectance(items)
    
    
    output = renders_dir / str(year) / f"{month:02d}"
    output.mkdir(parents=True, exist_ok=True)
    
    saved = []
    for t in refl.time.values:
        day = np.datetime_as_string(t, unit="D")
        one = refl.sel(time=t)
        water = indices.get_ndwi(one)
        
        saved.extend(save_date_images(one, water, day, output))
        log_date(one, water, clear.sel(time=t), day)
        
    saved.append(save_grid(refl, output))
    
    print(f"saved {len(saved)} files in {output.relative_to(renders_dir.parent)}")
    return saved
    
def main():
    year = int(sys.argv[1])
    band_loader.configure_s3()
    for i in range(12):
        process_month(year, i + 1)
    
if __name__ == "__main__":
    main()
