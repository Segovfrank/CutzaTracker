
#### Search
Base:https://stac.dataspace.copernicus.eu/v1/
Endpoint: search
Http Type: POST

Required request body:

```
{
    "collections": [
        "sentinel-2-l2a"
    ],
    "filter": {
         "op": "and",
         "args": [
            {
                "op": "<=",
                "args": [
                    {
                        "property": "eo:cloud_cover"
                    },
                    20
                ]
            },
            {
                "op": ">=",
                "args": [
                    {
                        "property": "datetime"
                    },
                    {
                        "timestamp": "2024-01-01T04:39:23Z"
                    }
                ]
            },
            {
                "op": "<",
                "args": [
                    {
                        "property": "datetime"
                    },
                    {
                        "timestamp": "2024-12-30T04:39:23Z"
                    }
                ]
            }
         ]
    },
    "intersects": {
        "type": "Polygon",
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
    },
    "limit": 20
}
```

Fetch 20 (max) items from the year of 2024

------

### Search (Single)
For a single entry Request Sample this is the following

```
{
    "collections": [
        "sentinel-2-l2a"
    ],
    "filter": {
         "op": "and",
         "args": [
            {
                "op": "<=",
                "args": [
                    {
                        "property": "eo:cloud_cover"
                    },
                    20
                ]
            },
            {
                "op": ">=",
                "args": [
                    {
                        "property": "datetime"
                    },
                    {
                        "timestamp": "2024-01-01T04:39:23Z"
                    }
                ]
            },
            {
                "op": "<",
                "args": [
                    {
                        "property": "datetime"
                    },
                    {
                        "timestamp": "2024-12-30T04:39:23Z"
                    }
                ]
            }
         ]
    },
    "intersects": {
        "type": "Polygon",
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
    },
    "limit": 1
}
```