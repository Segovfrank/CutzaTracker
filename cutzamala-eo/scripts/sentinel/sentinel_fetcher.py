import asyncio
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from httpx import AsyncClient
from pystac import ItemCollection
from ..utils import date_utils
from .api import sentinel_api
from .cache import cache_loader, cache_writer
from .constants import COPERNICUS_BASE_API

async def fetch_month(client: AsyncClient, year: int, month: int) -> ItemCollection:
    cached = cache_loader.load_collection(year, month)
    if cached is None:
        features = await fetch(client, start=datetime(year, month, 1, tzinfo=timezone.utc))
        cache_writer.save_features(features)
        cached = cache_loader.load_collection(year, month) or { "type": "FeatureCollection", "features": []}
    else:
        print(f"loaded collection_{year}_{month} from cache")
    return ItemCollection.from_dict(cached)

# Fetch 1 month by default
async def fetch(client: AsyncClient, start: datetime, end: datetime | None = None) -> list[dict]:
    if end is None:
        end = start + relativedelta(months=1)
        
    return await sentinel_api.fetch_since(client, start=start, end=end)

def _start_from_cache() -> datetime:
    latest = cache_loader.load_latest_date()
    if latest:
        return date_utils.parse(latest)
    return datetime(2024, 1, 1, tzinfo=timezone.utc)

async def main():
    async with AsyncClient(base_url=COPERNICUS_BASE_API, timeout=30.0) as client:
        features = await fetch(client=client, start=_start_from_cache())
        cache_writer.save_features(features)
        print(f"Fetched {len(features)} features")
    
if __name__ == "__main__":
    asyncio.run(main())