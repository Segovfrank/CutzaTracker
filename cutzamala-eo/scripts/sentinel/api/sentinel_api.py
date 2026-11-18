from datetime import datetime, timedelta
from httpx import AsyncClient, Response
import sys
from ..utils import request_utils
from ...utils import date_utils
from ..constants import VALLE_DE_BRAVO

lookback_days = 3

async def fetch_since(client: AsyncClient, start: datetime, end: datetime | None = None, intersects: dict = VALLE_DE_BRAVO) -> list[dict]:
    start_date = date_utils.to_stac_date(start - timedelta(days = lookback_days))
    end_date = date_utils.to_stac_date(end) if end else ".."
    request_body = request_utils.search_request_body(date_interval=f"{start_date}/{end_date}", intersects=intersects)
    return await _search_all_pages(client, request_body)

async def _search_all_pages(client: AsyncClient, body: dict) -> list[dict]:
    # Initial page
    page = await _search(client, "/search", body)
    features = page["features"]
    next_link = _find_next_link(page)
    
    # While we have pages to navigate, let's do search and populate all our features
    while next_link is not None:
        page = await _search(client, next_link["href"], next_link.get("body", body))
        features += page["features"]
        next_link = _find_next_link(page)
    
    return features
    
async def _search(client: AsyncClient, url: str, body: dict) -> dict:
    response = await client.post(url, json=body)
    report_error(response)
    return response.json()

def _find_next_link(page: dict) -> dict | None:
    for link in page.get("links", []):
        if link.get("rel") == "next":
            return link
    return None

def report_error(response: Response):
    if response.is_error:
        print("Error in search", file=sys.stderr)
        print(f"Status Code: {response.status_code}", file=sys.stderr)
        print(f"Message: {response.text}", file=sys.stderr)
        response.raise_for_status()