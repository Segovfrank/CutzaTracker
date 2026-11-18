from ..constants import DATETIME_PROP

def search_request_body(
    date_interval: str,
    intersects: dict, 
    collections: tuple = ("sentinel-2-l2a",), 
    cloud_cover: int = 20, 
    limit = 31
    ) -> dict:
    return  {
        "collections": list(collections),
        "intersects": intersects,
        "datetime": date_interval,
        "sortby": [
          {
              "field": f"properties.{DATETIME_PROP}",
              "direction": "desc"
          }  
        ],
        "filter": {
          "op": "and",
          "args": [
              filter_arg(op="<=", prop="eo:cloud_cover", arg_value=cloud_cover)
          ]  
        },
        "limit": limit
    }

def filter_arg(op: str, prop: str, arg_value: int | float | str) -> dict:
    return {
        "op": op,
        "args": [
            {
                "property": prop
            },
            arg_value
        ]
    }