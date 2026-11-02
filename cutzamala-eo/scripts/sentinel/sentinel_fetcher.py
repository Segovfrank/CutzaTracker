import asyncio
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from httpx import AsyncClient
from ..utils import date_utils
from .api import sentinel_api
from .cache import cache_loader, cache_writer
from .constants import COPERNICUS_BASE_API

# Fetch 1 month by default
async def fetch(client: AsyncClient, start: datetime, end: datetime | None = None) -> int:
    if end is None:
        end = start + relativedelta(months=1)
        
    features = await sentinel_api.fetch_since(client, start=start, end=end)
    cache_writer.save_features(features)
    return len(features)

def _start_from_cache() -> datetime:
    latest = cache_loader.load_latest_date()
    if latest:
        return date_utils.parse(latest)
    return datetime(2024, 1, 1, tzinfo=timezone.utc)

async def main():
    async with AsyncClient(base_url=COPERNICUS_BASE_API, timeout=30.0) as client:
        amount = await fetch(client=client, start=_start_from_cache())
        print(f"Fetched {amount} features")
    
if __name__ == "__main__":
    asyncio.run(main())