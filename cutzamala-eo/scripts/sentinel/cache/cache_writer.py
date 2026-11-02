from ...utils import json_utils
from ...utils import date_utils
from ..cache import cache_loader
from ..constants import DATETIME_PROP, metadata_dir, collections_dir
from collections import defaultdict

def save_features(features: list[dict]):
    # Although we usually search by months, technically we could have multiple months
    # Split features by month so create the files accordingly
    features_by_month = defaultdict(list)
    for feature in features:
        feature_date = _get_feature_datetime(feature)
        features_by_month[f"{feature_date.year}-{feature_date.month:02d}"].append(feature)
        
    for key, month_features in features_by_month.items():
        year, month = map(int, key.split("-"))
        save_collection_to_local(month_features, year, month)
        
def _get_feature_datetime(feature: dict):
    return date_utils.parse(feature["properties"][DATETIME_PROP])

def save_collection_to_local(new_features: list[dict], year: int, month: int):
    target_dir = collections_dir / "valle_de_bravo" / str(year)
    existing_collection = cache_loader.load_collection(year, month) or {}
    collection_json = {
        "type": "FeatureCollection",
        "features": merge_features(new_features, existing_collection.get("features", []))
    }
    is_successful = json_utils.save_json_to_local(data=collection_json, filename=f"collection_{year}_{month:02d}", dir=target_dir)
    if is_successful:
        save_latest_date(collection_json)
        
def merge_features(new: list[dict], old: list[dict]) -> list[dict]:
    # Dedup by feature id
    features_by_id = {}
    
    for feature in old:
        feature_id = feature["id"]
        features_by_id[feature_id] = feature
    
    for feature in new:
        feature_id = feature["id"]
        features_by_id[feature_id] = feature
        
    merged = list(features_by_id.values())
    # Sort by descending datetime
    merged.sort(key=_get_feature_datetime, reverse=True)
    return merged

def save_latest_date(collection_json: dict):
    # Collection is made of 'features' array.
    # A feature contains "properties" and inside we got "end_datetime"
    # Good for us, Features are ordered by date time (descending). So we can take item 0 properties and then end_datetime
    features = collection_json.get("features", [])
    if len(features) == 0:
        return
    
    last_date = features[0]["properties"][DATETIME_PROP]
    
    existing_date = cache_loader.load_latest_date()
    if existing_date:
        last_date = date_utils.get_latest_date(existing_date, last_date)
        
    latest_json = { "latest": last_date }
    is_successful = json_utils.save_json_to_local(data=latest_json, filename="latest", dir=metadata_dir)
    
    if not is_successful:
        print("Error writing latest date")
