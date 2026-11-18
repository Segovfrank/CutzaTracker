from collections.abc import Sequence

import matplotlib.pyplot as plt
import odc.stac
import numpy as np
from pystac import Item
import xarray as xr

from . import rio_configuration
from .constants import BBOX, renders_dir
from .item_collection_loader import load_collection

def configure_s3() -> None:
    # Set keys
    rio_configuration.configure()
    
def load_bands(items: Sequence[Item], bands: list[str]) -> xr.Dataset:
    # Read the pixels
    return odc.stac.load(
        items=items,
        bands=bands,
        bbox=BBOX, # Read only the the lake polygon, not the whole tile
        crs="EPSG:32614", # Tile's own UTM 14N grid
        resolution=10,
        groupby="solar_day" # Scenes from the same day merge into one time stamp (avoid dark sections?)
    )
    
if __name__ == "__main__":
    configure_s3()
    first = load_collection(2024, 1)[0]
    rgb_tci = ["TCI_10m.1", "TCI_10m.2", "TCI_10m.3"]
    dataset = load_bands([first], rgb_tci)
    print(dataset)
    
    one_date = dataset.isel(time=0)
    channels = []
    for band in rgb_tci:
        channels.append(one_date[band].values)
    rgb = np.dstack(channels)
    print("rgb", rgb.shape, rgb.dtype)
    
    renders_dir.mkdir(parents=True, exist_ok=True)
    plt.imsave(renders_dir / f"tci_{first.datetime.date()}.png", rgb)