from pystac import ItemCollection
import odc.stac
import xarray as xr
import matplotlib.pyplot as plt
import json
from pathlib import Path
import rio_configuration
import dask_client


def load_to_image(collection: ItemCollection):
    rio_configuration.configure()
    client = dask_client.get_client()
    
    #TODO: Implement


if __name__ == "__main__":
    try:
        print("Loading image")
        filename = "collection_2024_01.json"
        data_dir = Path(__file__).parent / "data"
        test_dir = data_dir / "metadata" / "valle_de_bravo" / filename
        print(f"Loading directory: {test_dir}")
        collection = load_collection_from_json(test_dir)
        
        # TODO:
    finally:
        dask_client.close_client()