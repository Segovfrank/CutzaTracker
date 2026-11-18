import numpy as np
import xarray as xr

from ..image_processing import band_loader, indices, reflectance
from ..image_processing.image_processor import SCL, clear_mask
from ..image_processing.item_collection_loader import load_collection

WATER_BANDS = ["B03_10m", "B08_10m"]

# Reads green, NIR and SCL bad for every date and returns 2 arrays on the same grid. 
# NDWI and Boolean mask for each pixel with a clear view
def load_month(year, month) -> tuple[xr.DataArray, xr.DataArray] | None:
    items = load_collection(year, month)
    if len(items) == 0:
        return None
    
    asset = reflectance.shared_asset(items, "B03_10m")
    # Stac Load of Each Item in a Collection and each Band
    raw = band_loader.load_bands(list(items), WATER_BANDS + [SCL])
    refl = reflectance.to_reflectance(raw[WATER_BANDS], asset)
    
    ndwi = indices.get_ndwi(refl)
    clear = clear_mask(raw[SCL])
    return ndwi, clear

if __name__ == "__main__":
    band_loader.configure_s3()
    month_data = load_month(2025, 4)
    if month_data:
        ndwi, clear = month_data
        print("NDWI", ndwi.shape, ndwi.dtype, " clear", clear.shape, clear.dtype)
        for t in ndwi.time.values:
            day = np.datetime_as_string(t, unit="D")
            share = float(clear.sel(time=t).mean())
            print(f"{day}  clear {share:6.1%} of the box")