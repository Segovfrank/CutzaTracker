from pystac import ItemCollection, Item
from shapely.geometry import box, shape
from .constants import BBOX
from httpx import AsyncClient
import asyncio

from ..sentinel.constants import COPERNICUS_BASE_API
from ..sentinel.constants import collections_dir
from ..sentinel.sentinel_fetcher import fetch_month

collection_path = collections_dir / "valle_de_bravo"

LAKE_BOX = box(*BBOX)

def load_collection(year: int, month: int) -> ItemCollection:
    loaded = asyncio.run(_fetch_month(year, month))
    return keep_full_coverage(loaded)

async def _fetch_month(year: int, month: int) -> ItemCollection:
    async with AsyncClient(base_url=COPERNICUS_BASE_API, timeout=30.0) as client:
        return await fetch_month(client, year, month)
    
def covers_lake(item: Item) -> bool:
    footprint = shape(item.geometry)
    return footprint.contains(LAKE_BOX)

def keep_full_coverage(items: ItemCollection) -> ItemCollection:
    kept = []
    for item in items:
        if covers_lake(item):
            kept.append(item)
        else:
            print(f"Identified image that does not contain lake shape at {item.id} - {item.datetime}")
    return ItemCollection(kept)

if __name__ == "__main__":
    collection = load_collection(2024, 1)
    print(len(collection), "items")
    first = collection[0]
    red = first.assets["B04_10m"]
    print("B04_10m", red.href[:45], "...")
    fields = red.extra_fields
    print("scale", fields["raster:scale"], "offset", fields["raster:offset"])