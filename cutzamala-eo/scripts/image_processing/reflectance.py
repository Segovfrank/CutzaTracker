import numpy as np
from pystac import Asset, Item, ItemCollection
import xarray as xr

from .band_loader import configure_s3, load_bands
from .constants import RGB
from .item_collection_loader import load_collection

RASTER_VALUES = ("raster:scale", "raster:offset", "nodata")

def to_reflectance(data_set: xr.Dataset, asset: Asset):
    # Reflectance is the fraction of sunlight a surface sends back
    # Formula is DN x raster:scale + raster:offset
    # 0 means absorbs everything and 1 means reflects it all
    scale = asset.extra_fields["raster:scale"]
    offset = asset.extra_fields["raster:offset"]
    nodata = asset.extra_fields["nodata"]
    # We need this because nodata 0 scaled becomes -0.1 and looks like water
    return data_set.where(data_set != nodata) * scale + offset

def decode_values(asset: Asset) -> list:
    values = []
    for field in RASTER_VALUES:
        values.append(asset.extra_fields[field])
    return values

def shared_asset(items: ItemCollection, key: str) -> Asset:
    # Let's guard using the first item as expected. If anything differs we throw an error
    first = items[0].assets[key]
    expected = decode_values(first)
    for item in items:
        found = decode_values(item.assets[key])
        if found != expected:
            raise ValueError(f"{item.id} decoes {key} with {found}, expected: {expected}")
    return first

if __name__ == "__main__":
    configure_s3()
    items = load_collection(2024, 1)
    data_set = load_bands([items[0]], RGB)
    red = data_set["B04_10m"].isel(time=0)
    print(f"Red: {red.dtype}, min: {int(red.min())}, max: {int(red.max())}")
    asset = shared_asset(items, "B04_10m")
    reflectance = to_reflectance(data_set, asset).isel(time=0)
    for band in RGB:
        p2, p50, p98 = np.nanpercentile(reflectance[band].values, [2,50,98])
        print(f"{band} p2={p2:.3f}, median {p50:.3f}, p98={p98:.3f}")