import numpy as np
import xarray as xr

from .constants import FALSE, RGB

def to_rgb(reflectance: xr.Dataset, bands: list[str] = RGB, vmax: float = 0.3) -> np.ndarray:
    # Stack the bands so we form an rgb (B04, B03, B02)
    channels = []
    for b in bands:
        channels.append(reflectance[b].values)
    rgb = np.dstack(channels)
    # We need to stretch the reflectance values because they come in small values and we need them in 0-1 scale
    # We use a vmax (reflectance show at full brightness, in order to normalize the days (brighter vs dim days))
    return np.clip(np.nan_to_num(rgb / vmax), 0, 1)

def false_color(reflectance: xr.Dataset) -> np.ndarray:
    return to_rgb(reflectance, bands=FALSE, vmax=0.4)