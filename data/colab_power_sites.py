# === WARPDRIVE - NASA Space Apps 2026 ===
# Google Colab cell: downloads NASA POWER climatology for several sites and saves climate_monthly.csv
# SI disclosure: drafted with an AI assistant (Claude), reviewed by the team.
import math, datetime, requests, pandas as pd

SITES = [  # site_id, name, lat, lon  (the team can change this list)
    ("daule",     "Daule, Guayas",         -1.86, -79.98),
    ("babahoyo",  "Babahoyo, Los Rios",    -1.80, -79.53),
    ("quevedo",   "Quevedo, Los Rios",     -1.03, -79.46),
    ("chone",     "Chone, Manabi",         -0.69, -80.09),
    ("santa_ana", "Santa Ana, Manabi",     -1.20, -80.37),
]
PARAMS = "T2M,T2M_RANGE,PRECTOTCORR,TOA_SW_DWN,RH2M,GWETROOT"
MONTHS = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]
DAYS = [31, 28.25, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

def power_climatology(lat, lon):
    url = "https://power.larc.nasa.gov/api/temporal/climatology/point"
    r = requests.get(url, params={"parameters": PARAMS, "community": "AG",
                                  "latitude": lat, "longitude": lon, "format": "JSON"}, timeout=60)
    r.raise_for_status()
    j = r.json()
    return j["geometry"]["coordinates"][2], j["properties"]["parameter"]

def field_elevation(lat, lon):
    # Temporary source: Open-Meteo (Copernicus DEM 90 m). Replace with NASA NASADEM later if time allows.
    r = requests.get("https://api.open-meteo.com/v1/elevation",
                     params={"latitude": lat, "longitude": lon}, timeout=30)
    r.raise_for_status()
    return float(r.json()["elevation"][0])

def hargreaves(t, rng, ra):
    return 0.0023 * (t + 17.8) * math.sqrt(max(rng, 0)) * 0.408 * ra  # mm/day

def build_rows(site_id, name, lat, lon, cell_elev, field_elev, p, today):
    rows = []
    for i, m in enumerate(MONTHS):
        t_cell = p["T2M"][m]
        t = t_cell + 0.0065 * (cell_elev - field_elev)  # lapse-rate correction
        rows.append({
            "site_id": site_id, "site_name": name, "lat": lat, "lon": lon,
            "field_elev_m": round(field_elev, 1), "cell_elev_m": round(cell_elev, 1),
            "month": i + 1,
            "t_mean_c": round(t, 2), "t_mean_raw_c": round(t_cell, 2),
            "t_range_c": p["T2M_RANGE"][m],
            "rain_mm": round(p["PRECTOTCORR"][m] * DAYS[i], 1),
            "et0_mm": round(hargreaves(t, p["T2M_RANGE"][m], p["TOA_SW_DWN"][m]) * DAYS[i], 1),
            "rh_pct": p["RH2M"][m],
            "root_soil_wetness": p["GWETROOT"][m],
            "source": "NASA POWER climatology 2001-2025 (AG community); ET0 Hargreaves FAO-56",
            "retrieved": today,
        })
    return rows

if __name__ == "__main__":
    today = datetime.date.today().isoformat()
    all_rows = []
    for sid, name, lat, lon in SITES:
        cell_elev, p = power_climatology(lat, lon)
        fe = field_elevation(lat, lon)
        all_rows += build_rows(sid, name, lat, lon, cell_elev, fe, p, today)
        print(f"OK {name}: cell {cell_elev:.0f} m, field {fe:.0f} m")
    df = pd.DataFrame(all_rows)
    df.to_csv("climate_monthly.csv", index=False)
    print(df.head(12))
    try:
        from google.colab import files
        files.download("climate_monthly.csv")
    except ImportError:
        print("Saved climate_monthly.csv")
