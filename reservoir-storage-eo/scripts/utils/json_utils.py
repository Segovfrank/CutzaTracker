import json
from pathlib import Path


def save_json_to_local(data: dict, filename: str, dir: Path) -> bool:
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
        if not final_dir.exists():
            final_dir.mkdir(parents=True, exist_ok=True)
        file_path = final_dir / f"{filename}.json"
        
        with open(file=file_path, mode="w", encoding="utf-8") as file:
            print(f"Saving item at: {file_path}")
            json.dump(data, file)
    except Exception as e:
        print(f"Error while saving json to local: {e}")
        return False
    return True

def read_json(filename: str, dir: Path) -> dict:
    try:
        file_path = dir / f"{filename}.json"
        with open(file=file_path, mode='r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error reading json: {e}")
        return {}