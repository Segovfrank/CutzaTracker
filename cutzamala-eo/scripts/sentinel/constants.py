from pathlib import Path

parent_dir = Path(__file__).parent
data_dir = parent_dir / "data"
metadata_dir = data_dir / "metadata"
collections_dir = data_dir / "collections"

DATETIME_PROP = "datetime"

# Network
COPERNICUS_BASE_API = "https://stac.dataspace.copernicus.eu/v1"
SEARCH_ENDPOINT = COPERNICUS_BASE_API + "/search"

# Copernicus API specifics
TYPE_POLYGON = "Polygon"

VALLE_DE_BRAVO = {
    "type": TYPE_POLYGON,
    "coordinates": [
        [
                [
                    -100.120125,
                    19.166897
                ],
                [
                    -100.122442,
                    19.227528
                ],
                [
                    -100.183125,
                    19.226313
                ],
                [
                    -100.180721,
                    19.166167
                ],
                [
                -100.120125,
                19.166897
            ]
        ]
    ]
}