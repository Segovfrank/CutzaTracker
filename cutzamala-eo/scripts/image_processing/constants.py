from pathlib import Path
from ..sentinel.constants import VALLE_DE_BRAVO

data_dir = Path(__file__).parent / "data"
renders_dir = data_dir / "renders"

# Do the box of the intersects values. Looping over the polygon corners.
# What values do we read within the box?
def bbox_of(polygon: dict) -> tuple[float, float, float, float]:
    lons = []
    lats = []
    for lon, lat in polygon["coordinates"][0]:
        lons.append(lon)
        lats.append(lat)
    return (min(lons), min(lats), max(lons), max(lats))

# Used later so reader uses only the pixels instead of all the pixels in a band
BBOX = bbox_of(VALLE_DE_BRAVO)
RGB = ["B04_10m", "B03_10m", "B02_10m"] 
RGB_N = RGB + ["B08_10m"] # almost infrared
FALSE = ["B08_10m", "B04_10m", "B03_10m"] # NIR shown as red

LAKE_CENTER = (-100.1516, 19.1968) # longitue and latitude
LAND = (-100.1828, 19.2272)
