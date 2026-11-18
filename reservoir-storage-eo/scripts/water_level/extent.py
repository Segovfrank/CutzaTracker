import numpy as np
from scipy import ndimage

from ..image_processing import band_loader
from .constants import data_dir
from .scenes import load_month
from .water import area_km2, water_mask

extent_npy = data_dir / "lake_extent.npy"
MARGIN_PIXELS = 10 # 100 m around the full outline

#Get the lake outline when full

def build_extent(ndwi: np.ndarray, clear: np.ndarray) -> np.ndarray:
    lake, _ = water_mask(ndwi, clear)
    return ndimage.binary_dilation(lake, iterations=MARGIN_PIXELS)

def load_extent() -> np.ndarray:
    return np.load(extent_npy)

# How much of the lake is visible
def clear_fraction(clear:np.ndarray, extent: np.ndarray) -> float:
    inside = clear[extent]
    return float(inside.mean())

if __name__ == "__main__":
    band_loader.configure_s3()
    ndwi, clear = load_month(2025, 10)
    
    fullest = None
    fullest_area = 0.0
    for t in ndwi.time.values:
        lake, _ = water_mask(ndwi.sel(time=t).values, clear.sel(time=t).values)
        area = area_km2(lake)
        print(f"{np.datetime_as_string(t, unit='D')}  {area:.2f}  km2")
        if area > fullest_area:
            fullest = t
            fullest_area = area
            
    extent = build_extent(ndwi.sel(time=fullest).values, clear.sel(time=fullest).values)
    data_dir.mkdir(parents=True, exist_ok=True)
    np.save(extent_npy, extent)
    print(f"extent from {np.datetime_as_string(fullest, unit='D')}: lake {fullest_area:.2f} km2, with margin {area_km2(extent):.2f} km2")
    for t in ndwi.time.values:
        fraction = clear_fraction(clear.sel(time=t).values, extent)
        print(f"{np.datetime_as_string(t, unit='D')}  clear {fraction:6.1%} of the lake")    