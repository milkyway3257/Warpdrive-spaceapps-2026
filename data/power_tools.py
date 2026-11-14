"""
power_tools.py - Starter helpers for NASA POWER (no login required).

Team WARPDRIVE - NASA Space Apps 2026 - "Field Shift: Adapting Farms with NASA Data"
SI disclosure: this file was drafted with an AI assistant (Claude) and reviewed by the team.

What it does
  1. Downloads 25-year monthly climatology for any lat/lon from NASA POWER (AG community).
  2. Corrects temperature for the elevation mismatch between the POWER grid cell and the
     real field (POWER cells are ~50 km wide; near the Andes the cell can be ~800 m higher
     than a lowland farm -> temperatures several degrees too low).
  3. Estimates reference evapotranspiration ET0 with Hargreaves (FAO-56 eq. 52), which only
     needs temperature + extraterrestrial radiation (both available in POWER).
  4. Computes a monthly crop water balance: rain - crop water need (ETc = Kc x ET0).

Gotchas verified on 2026-11-14:
  - Monthly/climatology T2M_MAX and T2M_MIN are the EXTREME day of the month, not the mean of
    daily values. Use T2M (mean) + T2M_RANGE (mean daily range) instead.
  - The response "geometry.coordinates[2]" is the elevation (m) of the POWER grid cell.
  - Climatology keys are JAN..DEC plus ANN. Fill value is -999.
"""

from __future__ import annotations

import math
import requests

POWER_CLIM_URL = "https://power.larc.nasa.gov/api/temporal/climatology/point"
MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
DAYS_IN_MONTH = [31, 28.25, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
LAPSE_RATE_C_PER_M = 0.0065  # standard environmental lapse rate (6.5 C per km)

DEFAULT_PARAMS = [
    "T2M",          # mean air temperature at 2 m (C)
    "T2M_RANGE",    # mean daily temperature range (C)
    "PRECTOTCORR",  # precipitation, bias corrected (mm/day)
    "TOA_SW_DWN",   # top-of-atmosphere radiation = Ra (MJ/m2/day)
    "ALLSKY_SFC_SW_DWN",  # surface solar radiation (MJ/m2/day)
    "RH2M",         # relative humidity (%)
    "WS2M",         # wind speed at 2 m (m/s)
    "GWETROOT",     # root-zone soil wetness (0-1), MERRA-2 model
]


def fetch_climatology(lat: float, lon: float, params: list[str] | None = None) -> dict:
    """Return {'cell_elevation_m': float, 'data': {PARAM: {JAN..DEC, ANN}}}."""
    params = params or DEFAULT_PARAMS
    r = requests.get(
        POWER_CLIM_URL,
        params={
            "parameters": ",".join(params),
            "community": "AG",
            "latitude": lat,
            "longitude": lon,
            "format": "JSON",
        },
        timeout=60,
    )
    r.raise_for_status()
    j = r.json()
    return {
        "cell_elevation_m": j["geometry"]["coordinates"][2],
        "data": j["properties"]["parameter"],
    }


def correct_temperature(t_cell_c: float, cell_elev_m: float, field_elev_m: float) -> float:
    """Shift POWER temperature from the grid-cell elevation to the real field elevation."""
    return t_cell_c + LAPSE_RATE_C_PER_M * (cell_elev_m - field_elev_m)


def hargreaves_et0(t_mean_c: float, t_range_c: float, ra_mj: float) -> float:
    """FAO-56 eq. 52. Returns ET0 in mm/day. Ra converted with 0.408 (MJ/m2/day -> mm/day)."""
    if t_range_c <= 0:
        return 0.0
    return 0.0023 * (t_mean_c + 17.8) * math.sqrt(t_range_c) * (0.408 * ra_mj)


def monthly_table(clim: dict, field_elev_m: float | None = None) -> list[dict]:
    """One row per month with corrected temperature, rain (mm/month) and ET0 (mm/month)."""
    d = clim["data"]
    cell_elev = clim["cell_elevation_m"]
    rows = []
    for i, m in enumerate(MONTHS):
        t = d["T2M"][m]
        if field_elev_m is not None:
            t = correct_temperature(t, cell_elev, field_elev_m)
        et0_day = hargreaves_et0(t, d["T2M_RANGE"][m], d["TOA_SW_DWN"][m])
        rows.append(
            {
                "month": m,
                "t_mean_c": round(t, 2),
                "rain_mm": round(d["PRECTOTCORR"][m] * DAYS_IN_MONTH[i], 1),
                "et0_mm": round(et0_day * DAYS_IN_MONTH[i], 1),
                "root_soil_wetness": d.get("GWETROOT", {}).get(m),
            }
        )
    return rows


def crop_water_balance(rows: list[dict], kc_by_month: dict[str, float]) -> list[dict]:
    """
    kc_by_month: e.g. {"JAN": 0.3, "FEB": 1.2, ...} only for months the crop is in the field.
    Returns rain - ETc per month (negative = deficit -> irrigation or stress).
    """
    out = []
    for r in rows:
        kc = kc_by_month.get(r["month"])
        if kc is None:
            continue
        etc = kc * r["et0_mm"]
        out.append({**r, "kc": kc, "etc_mm": round(etc, 1), "balance_mm": round(r["rain_mm"] - etc, 1)})
    return out


if __name__ == "__main__":
    # Example: Daule, Guayas (rice area). POWER cell elevation here is ~65 m; the real field is
    # near sea level (~1 m per Copernicus DEM via Open-Meteo). Replace with NASADEM for the final app.
    clim = fetch_climatology(-1.86, -79.98)
    print("POWER cell elevation (m):", clim["cell_elevation_m"])
    table = monthly_table(clim, field_elev_m=1)
    for row in table:
        print(row)
