
## 1: Get collection response via stac-api
Look at [[Using the Api]] - here we specify the endpoint, a sample request and the type of response we wait.

From the response we get a list of assets that contain Blue, Green and Red points for a spectral band.

## 2: Load item via odc-stac
Documentation: https://odc-stac.readthedocs.io/en/latest/

```
xx = odc.stac.load(
	query.items(),
	bands=["red", "green", "blue"],
	resolution=100,
)

xx.red.plot.imshow(col="time")
```