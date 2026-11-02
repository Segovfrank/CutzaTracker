
import json
from pystac import ItemCollection
from pathlib import Path
from datetime import datetime

current_dir = Path(__file__).parent
target_dir = current_dir / "data" / "metadata" / "valle_de_bravo"

def save_collection_to_local(collection: ItemCollection, year: int, month: int):
    save_json_to_local(data=collection.to_dict(), filename=f"collection_{year}_{month:02d}")

def save_json_to_local(data: dict, filename: str, dir: Path = target_dir) -> bool:
    """ Save a json to a local file under /data/metadata + a dir
    
    Args:
        data: the json data to save
        filename: the name of the file to save
        dir: optional directory name to save the file to. Detaulf is 'valle_de_bravo'
        
    Returns:
        A True if save was successful or False if not. Logs the error.
    
    """
    try:
        final_dir = dir
        
        final_dir.mkdir(parents=True, exist_ok=True)
        file_path = final_dir / f"{filename}.json"
        
        with open(file=file_path, mode="w", encoding="utf-8") as file:
            print(f"Saving item at: {file_path}")
            json.dump(data, file)
    except Exception as e:
        print(f"Error while saving json to local: {e}")
        return False
    return True