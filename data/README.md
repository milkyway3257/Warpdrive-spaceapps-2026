# Data

| File | What it is | Source |
|---|---|---|
| `climate_monthly.csv` | Monthly climatology 2001–2025 for the 4 zones (temperature, radiation, precipitation, humidity, soil wetness) | NASA POWER, AG community |
| `ndvi_timeseries.csv` | NDVI greenness on real rice paddies (with `lat`, `lon`), clouds and duplicates removed, 3×3 median | MODIS MOD13Q1 v061, via Microsoft Planetary Computer |
| `crops.csv` | Crops and FAO-56 Kc values (rice, soybean, Sesbania, Azolla). Empty cells for cover crops are an information gap, never zero | FAO-56, ECOCROP, IRRI, FAO |
| `colab_power_sites.py` | Google Colab script that downloads NASA POWER for the sites | — |
| `power_tools.py` | Helper functions for NASA POWER | — |

Monthly precipitation 1981–2025 (NASA POWER `PRECTOTCORR`) used for the El Niño findings and the Monte Carlo is embedded in `../index.html` (`HIST`).
