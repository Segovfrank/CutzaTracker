from ...utils import json_utils
from ..constants import collections_dir, metadata_dir

def load_collection(year: int, month: int) -> dict | None:
    target_dir = collections_dir / "valle_de_bravo" / str(year)
    dict = json_utils.read_json(filename= f"collection_{year}_{month:02d}", dir=target_dir)
    if dict:
        return dict
    else:
        return None
    
def load_latest_date() -> str | None:
    latest_dict = json_utils.read_json(filename="latest", dir=metadata_dir)
    return latest_dict.get("latest")