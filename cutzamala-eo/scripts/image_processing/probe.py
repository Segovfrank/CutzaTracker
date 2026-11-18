import xarray as xr
from pyproj import Transformer

from .band_loader import configure_s3, load_bands
from .constants import LAKE_CENTER, LAND, RGB_N
from .item_collection_loader import load_collection
from .reflectance import shared_asset, to_reflectance

# Context:
# Sentinel-2 is a camera with 13 fiolters. Each band is one slice of reflected sunlight. Visible light is 400-700 nm (nano meter).
# B02 - blue 490 nm
# B03 green - 560 nm
# B04 red - 665 nm
# NIR = Near Infrared - light past the red

# Relevant for us - water absorbs NIR. Almost nothing comes back.
# Land differs significally from water NIR. Do note that in this case, this lake is not "text book" and reflectance changes.
# A pure water lake absorbs almost all red and NIR.

def sample(reflectance: xr.Dataset, lon: float, lat: float, crs: str = "EPSG:32614") -> dict[str, float]:
    # Transform from lon/lat degrees
    # EPSG - its a registry for coordinate system
    # 4326 is for latitude/longitude. In this case the system for STAC
    # 32614 is for UTM zone 14N. Earth Model flattened onto a grid. The lake is in zone 14
    to_utm = Transformer.from_crs("EPSG:4326", crs, always_xy=True)
    x, y = to_utm.transform(lon, lat)
    # Picking the nearest pixel. We use this method to snap to closest, otherwise we would need an exact match (and if not found it raises an Error)
    pixel = reflectance.sel(x=x, y=y, method="nearest")
    values = {}
    for band in reflectance.data_vars:
        values[band] = round(float(pixel[band]), 3)
    return values


if __name__ == "__main__":
    configure_s3()
    items = load_collection(2024, 1)
    data_set = load_bands([items[0]], RGB_N)
    reflectance = to_reflectance(data_set, shared_asset(items, "B04_10m")).isel(time=0)
    print("lake: ", sample(reflectance, *LAKE_CENTER))
    print("land: ", sample(reflectance, *LAND))