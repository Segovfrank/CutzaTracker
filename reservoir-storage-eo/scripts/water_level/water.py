import numpy as np
from scipy import ndimage
from skimage.filters import threshold_otsu

PIXEL_AREA_M2 = 10 * 10

def largest_component(mask: np.ndarray) -> np.ndarray:
    # Identify the biggest bodies of water
    # We use the mask and group the largest 'chained 1s (water)'
    labelled, count = ndimage.label(mask)
    if count == 0:
        return mask
    # Ravel unrolls into a single list (instead of a matric)
    # Bincount counts how many 0, 1
    sizes = np.bincount(labelled.ravel())
    # Let's ignore the blob of 0 (land)
    sizes[0] = 0
    # Find which number is biggest
    return labelled == sizes.argmax()


def water_mask(ndwi: np.ndarray, clear: np.ndarray) -> tuple[np.ndarray, float]:
    usable = clear & np.isfinite(ndwi)
    # NDWI ranges from -1 to 1
    # Use Otsu algorithm to get the threshold value from water -> land
    # This way we can classify
    threshold = float(threshold_otsu(np.clip(ndwi[usable], -1, 1)))
    water = usable & (ndwi > threshold)
    return largest_component(water), threshold


def area_km2(mask: np.ndarray) -> float:
    return int(mask.sum()) * PIXEL_AREA_M2 / 1_000_000