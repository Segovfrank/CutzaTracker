import xarray as xr

# We are going to get the NDWI (Normalized Difference Water Index) = (B03 - B08) / (B03 + B08), from -1 to 1
# That mean above 0 is more green that infrared: probably water
def get_ndwi(reflectance: xr.Dataset) -> xr.DataArray:
    green = reflectance["B03_10m"]
    nir = reflectance["B08_10m"]
    return (green - nir) / (green + nir)

