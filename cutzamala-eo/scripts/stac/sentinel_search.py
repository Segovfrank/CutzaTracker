from datetime import date
import calendar
from intersects import VALLE_DE_BRAVO
from endpoints import COPERNICUS_BASE_API
from response_to_local import save_collection_to_local
from utils import filter_arg
import asyncio
import sys
from httpx import AsyncClient, Response
from pystac import ItemCollection

async def fetch_month(
    client: AsyncClient,
    year: int,
    month: int,
    intersects: dict = VALLE_DE_BRAVO,
    save_to_local: bool = False
    ) -> dict:
    start_date = date(year, month, 1)
    _, last_day = calendar.monthrange(year, month)
    end_date = date(year, month, last_day)
    response = await _do_search(client=client, start_date=start_date, end_date=end_date, intersects=intersects)
    if response.is_error:
        print("Error in search", file=sys.stderr)
        print(f"Status Code: {response.status_code}", file=sys.stderr)
        print(f"Message: {response.text}", file=sys.stderr)
        response.raise_for_status()
    json_data = response.json()
    if save_to_local:
        save_collection_to_local(json_data, year, month)
    return json_data
    

async def _do_search(client: AsyncClient, start_date: date, end_date: date, intersects: dict) -> Response:
    body = _build_body(start_date=start_date, end_date=end_date, intersects=intersects)
    response = await client.post("/search", json=body)
    return response

def _build_body(
    start_date: date, 
    end_date: date, 
    intersects: dict, 
    collections: tuple = ("sentinel-2-l2a",), 
    cloud_cover: int = 20, 
    limit = 31
    ) -> dict:
    start = f"{start_date.isoformat()}T00:00:00Z"
    end = f"{end_date.isoformat()}T23:59:59Z"
    date_interval = f"{start}/{end}"
    return  {
        "collections": list(collections),
        "intersects": intersects,
        "datetime": date_interval,
        "filter": {
          "op": "and",
          "args": [
              filter_arg(op="<=", prop="eo:cloud_cover", arg_value=cloud_cover)
          ]  
        },
        "limit": limit
    }

async def main(): 
    async with AsyncClient(base_url=COPERNICUS_BASE_API, timeout=30.0) as client:
        res = await fetch_month(client=client, year = 2024, month = 2, save_to_local=True)
        collection: ItemCollection = ItemCollection.from_dict(res)
        print("(INFO) Collection Search Response")
        for item in collection:
            print(f"ID: {item.id} - Date: {item.datetime}")
            print(f"Cloud Cover: {item.properties['eo:cloud_cover']}")
        

# if __name__ == "__main__":
#     asyncio.run(main())