# NASA Earth Observation & Agroclimatic Data Dictionary — Team WARPDRIVE

This document describes the datasets generated and used in *Field Shift: Adapting Farms with NASA Data* (NASA International Space Apps Challenge 2026 — Guayaquil, Ecuador). All datasets cover four representative rice-growing cantons in the Guayas River Basin (daule, salitre, samborondon, and babahoyo).

---

## 1. data/climate_monthly.csv

Monthly agroclimatic normals (2001–2025 climatology) used to evaluate thermal suitability, water balance, rainfall seasonality, and reference evapotranspiration ($ET_0$) across crop rotation scenarios.

* *Primary Source:* NASA POWER Project (AG Agroclimatology community, Temporal Climatology API v2, 2001–2025).
* *Elevation Source:* Open-Meteo Elevation API (Copernicus DEM GLO-90, 90 m spatial resolution) for field-level lapse-rate temperature adjustment.
* *Spatial Resolution:* ~0.5° × 0.625° (~50 km grid cell) for NASA POWER; 90 m for field elevation.
* *Temporal Resolution:* 12 monthly climatological averages (month 1 to 12) per site (48 rows total).

### Column Definitions

| Column | Unit | Description | Source / Calculation |
| :--- | :--- | :--- | :--- |
| site_id | text | Unique lowercase identifier for the rice-growing zone (daule, salitre, samborondon, babahoyo). | Team WARPDRIVE |
| site_name | text | Human-readable canton and province name in Ecuador. | Team WARPDRIVE |
| lat | decimal degrees | Latitude (WGS84) of the site reference point. | WGS84 |
| lon | decimal degrees | Longitude (WGS84) of the site reference point. | WGS84 |
| field_elev_m | meters (m) | Local terrain elevation at the agricultural site. | Copernicus DEM (90 m) |
| cell_elev_m | meters (m) | Mean elevation of the ~50 km NASA POWER grid cell (geometry.coordinates[2]). | NASA POWER |
| month | integer (1–12) | Calendar month (1 = January, 12 = December). | NASA POWER |
| t_mean_c | °C | Lapse-rate corrected monthly mean air temperature at 2 m: $T_{\text{mean}} = T_{\text{raw}} + 0.0065 \times (\text{cell\_elev\_m} - \text{field\_elev\_m})$. | Derived from NASA POWER T2M |
| t_mean_raw_c | °C | Uncorrected monthly mean air temperature at 2 m for the ~50 km grid cell. | NASA POWER T2M |
| t_range_c | °C | Mean daily temperature range ($T_{\max} - T_{\min}$ averaged across days in the month). | NASA POWER T2M_RANGE |
| rain_mm | mm/month | Total monthly bias-corrected precipitation (PRECTOTCORR daily rate × days in month). | NASA POWER PRECTOTCORR |
| et0_mm | mm/month | Monthly FAO-56 Hargreaves reference evapotranspiration calculated from t_mean_c, t_range_c, and extraterrestrial solar radiation (TOA_SW_DWN). | FAO-56 Hargreaves / NASA POWER |
| rh_pct | % | Monthly mean relative humidity at 2 m height. | NASA POWER RH2M |
| root_soil_wetness | dimensionless (0–1) | Root-zone soil wetness fraction (0 = completely dry, 1 = fully saturated). | NASA POWER GWETROOT |
| source | text | Dataset provenance and methodology label. | NASA POWER / FAO-56 |
| retrieved | ISO date (YYYY-MM-DD) | Date the data was retrieved and processed. | Pipeline timestamp |

### Known Limitations (climate_monthly.csv)
1. *Coarse Grid Resolution (~50 km):* NASA POWER cells average climate over ~50 km, which can include Andean foothills on eastern cells (e.g., Babahoyo cell_elev_m = 837 m vs. lowland rice fields at ~12 m), causing a ~5 °C cold bias if uncorrected. We applied a standard environmental lapse-rate correction ($0.0065\ ^\circ\text{C/m}$) to restore realistic lowland temperatures.
2. *Climatological Normals vs. Extreme Events:* Monthly climatology represents multi-year averages (2001–2025) and smooths out individual El Niño flooding anomalies or extreme drought weeks.
3. *Reference $ET_0$ Approximation:* FAO-56 Hargreaves estimates reference grass evapotranspiration using temperature range and extraterrestrial radiation rather than full Penman-Monteith wind/net radiation terms.

---

## 2. data/ndvi_timeseries.csv

Multi-year satellite vegetation index time series (2023–2026) sampled directly over verified lowland rice paddies to track double-cropping cycles, fallow periods, and seasonal flooding.

* *Primary Source:* NASA Terra MODIS Vegetation Indices (MOD13Q1 Version 6.1), accessed via Microsoft Planetary Computer STAC API (modis-13Q1-061).
* *Spatial Resolution:* 250 m native pixel; aggregated as the *spatial median of a 3×3 pixel window* (~750 m × 750 m) centered on verified rice fields.
* *Temporal Resolution:* 16-day composite intervals from 2023-01-01 to 2026-11-14 (one deduplicated record per site_id and composite start date).

### Column Definitions

| Column | Unit | Description | Source / Calculation |
| :--- | :--- | :--- | :--- |
| site_id | text | Unique lowercase identifier matching climate_monthly.csv (daule, salitre, samborondon, babahoyo). | Team WARPDRIVE |
| date | ISO date (YYYY-MM-DD) | Start date of the 16-day MODIS composite period. | NASA MODIS MOD13Q1 |
| ndvi | dimensionless (-1 to 1) | Cloud-filtered 3×3 window median Normalized Difference Vegetation Index (raw * 0.0001). Values $>0.5$ indicate dense healthy crop canopy; $0.1–0.3$ indicate bare/harvested soil; $\le 0$ indicate standing floodwater. Left blank (null) when all 9 pixels are cloud-contaminated. | NASA MODIS 250m_16_days_NDVI |
| lat | decimal degrees | Latitude (WGS84) of the verified rice-paddy sampling center. | Google Earth / WGS84 |
| lon | decimal degrees | Longitude (WGS84) of the verified rice-paddy sampling center. | Google Earth / WGS84 |
| source | text | Satellite product, spatial aggregation, quality filter, and access platform. | NASA LP DAAC / Planetary Computer |

### Known Limitations (ndvi_timeseries.csv)
1. *Persistent Tropical Cloud Cover:* During the Guayas rainy season (January–April), dense cloud cover frequently degrades optical satellite observations. Pixels with 250m_16_days_pixel_reliability > 1 (snow/ice or cloudy) are strictly excluded; dates where all 9 pixels in the 3×3 window are cloudy remain empty (null) rather than interpolated or zero-filled.
2. *250 m Spatial Footprint vs. Smallholder Plots:* A 3×3 MODIS window covers ~56 hectares (~750 m × 750 m), capturing neighborhood-scale rice paddy dynamics rather than individual smallholder parcels (<5 ha), which would require 10 m Sentinel-2 imagery.
3. *Floodwater Suppression:* Standing water in flooded rice paddies (babahoyo rainy season) produces negative NDVI values (< 0), reflecting surface water inundation rather than permanent soil degradation.

---

## 3. Auxiliary NASA Map Layers (Visual Reference)
In addition to the tabular CSV datasets above, the web application can stream real-time/historical Earth observation tiles from *NASA GIBS (Global Imagery Browse Services)* (GoogleMapsCompatible_Level9):
* MODIS_Terra_L3_NDVI_16Day (16-day vegetation vigor)
* SMAP_L4_Analyzed_Root_Zone_Soil_Moisture (Root-zone soil moisture)
* IMERG_Precipitation_Rate (GPM precipitation rate)

---

AI Disclosure: Data extraction scripts and documentation formatting were drafted with assistance from AI tools (Claude and Gemini) and verified by Team WARPDRIVE.
