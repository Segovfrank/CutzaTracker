# Overview

This project is a showcase of how the water levels in the Cutzamala reservoir has changed over time.

## Objective

There are two main objectives: 
1. Estimate reservoir storage from satellite imagery. The idea is to build a model that estimates the "Valle de Bravo" stored volume (hm^3) from Sentinel-2 water surface area. The model accuracy will be callibrated and validated against CONAGUA's official SINA records (2019 -> April 2025)
2. Fill the public data gap. After April 23, 2025 there's no data available.
3. Use this practical project in order to learn about Copernicus, OpenEO ultimately applying this knowledge to build a ML Model.

## Technologies Used

- Sentinel-2 L2A imagery to get a historical data timeline of how the reservoir levels changed.
- OpenEO library
- Sentinel HUB Statistical API

## Context on the Cutzamala System

The Cutzamala System comprom7 dams. These are found in Michocan and Estado de Mexico.
From those 7 dams, "Miguel Aleman (Valle de Bravo)" is the biggest one, containing, at NAMO, 394.39 hm^3.
Since reports and other official statements refer to the Cutzamala capacity as 782.521 hm^3 (the sum of the three NAMOs from the Big 3 Reservois: El Bosque, Valle de Bravo and Villa Victoria), we will only refer to these 3.

## Glossary

| Term | Meaning                                                                    | Note                                                                                                                                                  |
| ---- | -------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| NAMO | Nivel de Aguas Máximas Ordinarias (maximum ordinary water level)           | The highest level the dam is _normally operated_ at. Everything up to here is usable storage for water supply. It's the 100% in every CONAGUA report. |
| NAME | Nivel de Aguas Máximas Extraordinarias (maximum extraordinary water level) | The highest level the dam is _designed_ to reach under any circumstance. The water level between this and NAMO is known as over-storage.              |
References: https://app.conagua.gob.mx/spr/glosario.html

## Source of truth

Getting the data from Conagua official API: https://sinav30.conagua.gob.mx:8080/PresasPG/presas/reporte/{YYYY-MM-DD}

Measurement unit for dams: hm^3

| Dam            | SINA ID (`clavesih`) | NAMO capacity (100%) | NAME capacity (absolute max) | Elevation at NAMO |
| -------------- | -------------------- | -------------------- | ---------------------------- | ----------------- |
| Valle de Bravo | `VBRMX`              | **394.39 hm³**       | 449.42 hm³                   | 1830.0 m          |
| El Bosque      | `DBOMC`              | **202.4 hm³**        | 220.1 hm³                    | 1741.4 m          |
| Villa Victoria | `VVCMX`              | **185.723 hm³**      | 249.943 hm³                  | 2605.5 m          |
