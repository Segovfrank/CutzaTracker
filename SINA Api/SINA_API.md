To call the SINA API:

https://sinav30.conagua.gob.mx:8080/PresasPG/presas/reporte/{YYYY-MM-DD}

See: [Sample Json From February 2, 2025](json_sample_2025_02_20.json)

```
  {
    "idmonitoreodiario": 2273207,
    "fechamonitoreo": "2025-02-19",
    "clavesih": "VBRMX",
    "nombreoficial": "Valle de Bravo, Méx.",
    "nombrecomun": "Valle de Bravo, Méx.",
    "estado": "México",
    "nommunicipio": "Valle de Bravo",
    "regioncna": "Balsas",
    "latitud": 19.2075,
    "longitud": -100.18,
    "uso": "AP",
    "corriente": "R. Valle de Bravo",
    "tipovertedor": "Libre",
    "inicioop": "1947",
    "elevcorona": "1835.37",
    "bordolibre": 2.5,
    "nameelev": 1833.0,
    "namealmac": 449.42,
    "namoelev": 1830.0,
    "namoalmac": 394.39,
    "alturacortina": "56",
    "elevacionactual": 1822.37,
    "almacenaactual": 265.116,
    "llenano": 0.6722178554222977
  }
```

### Daily Params

| Field               | Type in JSON          | Meaning                                       | Unit                              |
| ------------------- | --------------------- | --------------------------------------------- | --------------------------------- |
| `idmonitoreodiario` | int                   | Unique ID of this daily record                | none                              |
| `fechamonitoreo`    | string (`YYYY-MM-DD`) | Measurement date                              | none                              |
| `elevacionactual`   | float                 | Current water surface elevation               | m above sea level                 |
| `almacenaactual`    | float                 | Current stored volume. **Your ground truth.** | hm³                               |
| `llenano`           | float                 | Fill fraction, `almacenaactual / namoalmac`   | ratio (0.64 = 64%, can be over 1) |

### Dam Metadata

This is static

| Field                           | Type in JSON         | Meaning                                    | Unit                        |
| ------------------------------- | -------------------- | ------------------------------------------ | --------------------------- |
| `clavesih`                      | string               | Dam ID, e.g. `VBRMX`. **Your join key.**   | none                        |
| `nombreoficial` / `nombrecomun` | string / nullable    | Official and common names                  | none                        |
| `estado`, `nommunicipio`        | string               | State, municipality                        | none                        |
| `regioncna`                     | string               | CONAGUA hydrological-administrative region | none                        |
| `latitud`, `longitud`           | float                | Dam location                               | degrees (WGS84, presumably) |
| `uso`                           | string               | Use codes, combinable (`AP/GH/RI`)         | see below                   |
| `corriente`                     | string               | River or stream it impounds                | none                        |
| `tipovertedor`                  | string               | Spillway type: `Libre`, `Contr`, `Mixto`   | none                        |
| `inicioop`                      | **string**, nullable | Year operations began                      | year                        |
| `elevcorona`                    | **string**, nullable | Crest (top of dam) elevation               | m                           |
| `alturacortina`                 | **string**, nullable | Dam wall height                            | m                           |
| `bordolibre`                    | float                | Freeboard (NAME to crest)                  | m                           |
| `namoelev` / `namoalmac`        | float                | NAMO elevation / NAMO capacity (100%)      | m / hm³                     |
| `nameelev` / `namealmac`        | float                | NAME elevation / NAME capacity             | m / hm³                     |
