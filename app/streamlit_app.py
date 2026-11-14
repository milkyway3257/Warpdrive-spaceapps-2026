"""
WARPDRIVE - Flood-aware crop rotation planner for rice farmers (Guayas & Los Rios, Ecuador)
NASA Space Apps Challenge 2026 - "Field Shift: Adapting Farms with NASA Data"

SI disclosure: this file was drafted with an AI assistant (Claude) from the team's spec
(docs/spec.md) and reviewed by the team.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

DATA = Path(__file__).resolve().parent.parent / "data"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
WET = [1, 2, 3, 4]          # flood-risk months used for exposure (Jan-Apr)
DRY_START = 6               # dry season starts in June

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
# Fallback so the app works before data/climate_monthly.csv is uploaded.
# Values: NASA POWER climatology 2001-2025, Daule (-1.86, -79.98), temperature corrected
# from cell elevation 64.6 m to field elevation 1 m; ET0 Hargreaves (FAO-56).
FALLBACK = pd.DataFrame({
    "site_id": "daule", "site_name": "Daule, Guayas (sample)",
    "month": list(range(1, 13)),
    "rain_mm": [123.4, 214.7, 212.3, 126.0, 37.8, 9.9, 3.4, 2.8, 2.4, 6.2, 8.1, 23.6],
    "et0_mm": [165.2, 134.9, 141.8, 144.4, 154.1, 155.7, 172.4, 187.7, 189.8, 189.9, 177.3, 176.3],
    "root_soil_wetness": [0.64, 0.73, 0.79, 0.76, 0.69, 0.63, 0.60, 0.59, 0.59, 0.59, 0.59, 0.60],
    "cell_elev_m": 64.6, "field_elev_m": 1.0,
    "source": "NASA POWER climatology 2001-2025 (AG community); ET0 Hargreaves FAO-56",
})


@st.cache_data
def load_climate() -> tuple[pd.DataFrame, bool]:
    f = DATA / "climate_monthly.csv"
    if f.exists():
        df = pd.read_csv(f)
        df = df.replace(-999, pd.NA)
        return df, True
    return FALLBACK.copy(), False


@st.cache_data
def load_ndvi() -> pd.DataFrame | None:
    f = DATA / "ndvi_timeseries.csv"
    if f.exists():
        df = pd.read_csv(f, parse_dates=["date"])
        return df
    return None


# ---------------------------------------------------------------------------
# Crops and strategies (Kc from FAO-56 Table 12; calendars are simplified, see spec)
# ---------------------------------------------------------------------------
CROPS = {
    "rice": {"label": "Rice", "kc": [1.05, 1.20, 1.20, 0.90], "legume": False, "cash": True,
             "kc_short": [1.05, 1.20, 1.20, 0.90]},   # ~120 days
    "soybean": {"label": "Soybean", "kc": [0.40, 1.15, 1.15, 0.50], "legume": True, "cash": True,
                "kc_short": [0.40, 1.15, 0.50]},       # ~85-100 days (short cycle after a flood)
    "cover": {"label": "Cover / fallow", "kc": None, "legume": False, "cash": False},
}


def calendar(*blocks: tuple[str, int, int]) -> dict[int, tuple[str, float | None]]:
    """blocks: (crop, start_month, n_months) -> {month: (crop, kc)}"""
    cal = {}
    for crop, start, n in blocks:
        kcs = CROPS[crop]["kc"]
        for i in range(n):
            m = (start - 1 + i) % 12 + 1
            cal[m] = (crop, kcs[i] if kcs else None)
    return cal


STRATEGIES = {
    "S0": {
        "name": "S0 - Current: rice + rice/ratoon",
        "cal": calendar(("rice", 1, 4), ("rice", 6, 4)),
        "why": "This is what most rice farmers in the zone do today (baseline for comparison).",
        "evidence": "Local practice; wet-season rice is the most flood-affected crop in Guayas.",
        "benefits": "Known crop, known market, existing equipment and buyers.",
        "gaps": "Field-level flood frequency is unknown (NASA POWER is zone-level, ~50 km).",
        "risks": "Young rice in Jan-Apr is exposed to floods; rice after rice keeps pests and depletes soil.",
        "breaks_mono": "No",
    },
    "S1": {
        "name": "S1 - Rice (wet season) + soybean (dry season)",
        "cal": calendar(("rice", 1, 4), ("soybean", 6, 4)),
        "why": "Replaces dry-season rice with a legume that needs less water and adds nitrogen.",
        "evidence": "Rice-soybean rotation proposed for Babahoyo (Caicedo et al., Killkana Tecnica, UCACUE); "
                    "dry-season water need computed from NASA POWER.",
        "benefits": "Less irrigation water in the dry season; soybean fixes nitrogen; breaks rice-after-rice.",
        "gaps": "Soybean performance on heavy clay rice soils; local soybean prices and buyers.",
        "risks": "Waterlogging hurts soybean; needs drainage and different equipment. Review with a local technician.",
        "breaks_mono": "Yes",
    },
    "S2": {
        "name": "S2 - Avoid flood season: cover/fallow (wet) + rice (dry, irrigated)",
        "cal": calendar(("cover", 1, 4), ("rice", 6, 4)),
        "why": "On flood-prone plots, no cash crop is in the field during the riskiest months.",
        "evidence": "During El Nino years some farmers already skip wet-season rice for fear of floods; "
                    "flood-season rain from NASA POWER.",
        "benefits": "No investment lost to wet-season floods; soil covered instead of bare.",
        "gaps": "Which cover crop tolerates waterlogging locally; irrigation water availability in the dry season.",
        "risks": "One harvest per year instead of two (less income); depends on irrigation. Review locally.",
        "breaks_mono": "Partly",
    },
}


def evaluate(strategy: dict, clim: pd.DataFrame, wet_factor: float) -> dict:
    rain = dict(zip(clim["month"], clim["rain_mm"]))
    et0 = dict(zip(clim["month"], clim["et0_mm"]))
    irrigation, exposure_mm, exposure_months, bare, legume = 0.0, 0.0, 0, 0, False
    for m in range(1, 13):
        crop, kc = strategy["cal"].get(m, (None, None))
        if crop is None:
            bare += 1
            continue
        info = CROPS[crop]
        legume = legume or info["legume"]
        if kc is not None and m >= DRY_START - 1:          # May-Dec: water need beyond rain
            irrigation += max(0.0, kc * float(et0[m]) - float(rain[m]))
        if info["cash"] and m in WET:
            exposure_months += 1
            exposure_mm += float(rain[m]) * wet_factor
    return {
        "Dry-season irrigation need (mm)": round(irrigation),
        "Cash crop in field Jan-Apr (months)": exposure_months,
        "Rain while exposed (mm)": round(exposure_mm),
        "Legume in rotation": "Yes" if legume else "No",
        "Bare months": bare,
        "Breaks rice-after-rice": strategy["breaks_mono"],
    }


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Flood-aware rotation planner", page_icon="🌾", layout="wide")
st.title("🌾 Flood-aware crop rotation planner")
st.caption("For rice farmers in Guayas & Los Rios, Ecuador · NASA Space Apps 2026 · Team WARPDRIVE")
st.info("This tool supports, and does not replace, your judgement and local technical advice.")

clim_all, real_data = load_climate()
if not real_data:
    st.warning("Showing sample data for Daule while the full dataset is being prepared.")

with st.sidebar:
    st.header("Your farm")
    sites = clim_all.drop_duplicates("site_id")[["site_id", "site_name"]]
    site_name = st.selectbox("Location", sites["site_name"].tolist())
    st.selectbox("Current crop pattern", ["Rice + rice/ratoon"])
    st.header("Scenario")
    scenario = st.radio("Wet-season rain", ["Normal (climatology)", "Wetter than normal (what if)"])
    wet_factor = 1.0
    if scenario.startswith("Wetter"):
        wet_factor = st.slider("Wet-season rain multiplier (scenario, not a forecast)", 1.1, 2.0, 1.5, 0.1)

clim = clim_all[clim_all["site_name"] == site_name].sort_values("month")
src = clim["source"].iloc[0] if "source" in clim else "NASA POWER"
conf = "Zone-level (~50 km grid), long-term average"

# 1. Climate
st.subheader(f"1 · Climate of {site_name}")
fig = go.Figure()
fig.add_bar(x=MONTHS, y=clim["rain_mm"], name="Rain (mm/month)", marker_color="#4C78A8")
fig.add_scatter(x=MONTHS, y=clim["et0_mm"], name="Water demand ET0 (mm/month)", mode="lines+markers",
                line=dict(color="#E45756"))
fig.add_vrect(x0=-0.5, x1=3.5, fillcolor="#4C78A8", opacity=0.08, line_width=0,
              annotation_text="Wet season / flood risk", annotation_position="top left")
fig.add_vrect(x0=4.5, x1=10.5, fillcolor="#F58518", opacity=0.08, line_width=0,
              annotation_text="Dry season", annotation_position="top left")
fig.update_layout(height=360, margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h"))
st.plotly_chart(fig, width="stretch")
if "cell_elev_m" in clim and "field_elev_m" in clim:
    st.caption(f"Source: {src}. {conf}. Temperature corrected from grid-cell elevation "
               f"{float(clim['cell_elev_m'].iloc[0]):.0f} m to field elevation {float(clim['field_elev_m'].iloc[0]):.0f} m.")

# 2. Strategies
st.subheader("2 · Compare rotation strategies")
rows, cal_rows = [], []
for key, s in STRATEGIES.items():
    rows.append({"Strategy": s["name"], **evaluate(s, clim, wet_factor)})
    cal_rows.append([CROPS[s["cal"][m][0]]["label"] if m in s["cal"] else "Bare" for m in range(1, 13)])
table = pd.DataFrame(rows).set_index("Strategy")
st.dataframe(table, width="stretch")
if wet_factor != 1.0:
    st.caption(f"Scenario: wet-season rain × {wet_factor:.1f} (what-if, not a forecast).")
st.caption(f"Irrigation need = sum of max(0, Kc × ET0 − rain) May–Dec. Kc: FAO-56 Table 12. Climate: {src}. "
           "Limitations: Hargreaves may overestimate ET0 in humid climates; soil water storage and paddy "
           "percolation are not included.")

st.markdown("**12-month calendar**")
cal_df = pd.DataFrame(cal_rows, columns=MONTHS, index=[s["name"] for s in STRATEGIES.values()])
colors = {"Rice": "background-color:#9ecae1", "Soybean": "background-color:#a1d99b",
          "Cover / fallow": "background-color:#e5d8bd", "Bare": "background-color:#f2f2f2;color:#999"}
st.dataframe(cal_df.style.map(lambda v: colors.get(v, "")), width="stretch")

for s in STRATEGIES.values():
    with st.expander(s["name"]):
        st.markdown(f"**Why suggested:** {s['why']}\n\n**Evidence:** {s['evidence']}\n\n"
                    f"**Benefits:** {s['benefits']}\n\n**Information gaps:** {s['gaps']}\n\n"
                    f"**Risks to review locally:** {s['risks']}")

# 3. After a flood
st.subheader("3 · After a flood")
receded = st.selectbox("Month the water went down", MONTHS[:6], index=2)
m0 = MONTHS.index(receded) + 1
left = max(0, DRY_START - (m0 + 1))
st.write(f"Months of wet season left before the dry season (June): **{left}**")
rain = dict(zip(clim["month"], clim["rain_mm"]))
et0 = dict(zip(clim["month"], clim["et0_mm"]))
opts = []
for key in ["rice", "soybean"]:
    kcs = CROPS[key]["kc_short"]
    need = 0.0
    for i, kc in enumerate(kcs):
        m = (m0 + i) % 12 + 1
        need += max(0.0, kc * float(et0[m]) - float(rain[m]))
    opts.append({"Crop": CROPS[key]["label"], "Cycle (months)": len(kcs),
                 "Fits in remaining wet season": "Yes" if len(kcs) <= left else "No",
                 "Extra water needed if planted next month (mm)": round(need)})
st.dataframe(pd.DataFrame(opts).set_index("Crop"), width="stretch")
st.caption("Simplified: assumes planting the month after the water goes down. Check soil condition, seed and "
           "irrigation availability with a local technician.")

# 4. NDVI (optional, Proposed D)
st.subheader("4 · Field greenness from space (NDVI)")
ndvi = load_ndvi()
if ndvi is None:
    st.info("NASA MODIS NDVI time series coming soon.")
else:
    sid = clim["site_id"].iloc[0]
    sub = ndvi[ndvi["site_id"] == sid]
    if sub.empty:
        st.info("No NDVI data for this location yet.")
    else:
        f2 = go.Figure(go.Scatter(x=sub["date"], y=sub["ndvi"], mode="lines+markers", line=dict(color="#54A24B")))
        f2.update_layout(height=300, yaxis_title="NDVI", margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(f2, width="stretch")
        st.caption("NDVI: healthy crop ≈ 0.6–0.9; bare soil ≈ 0.1–0.3; water/flooded ≈ 0 or below. "
                   "Source: NASA MODIS MOD13Q1 (250 m, 16-day). One 250 m pixel ≈ zone, not a single plot.")

st.divider()
st.caption("Data: NASA POWER (climate), NASA MODIS (NDVI). Crop coefficients: FAO-56. "
           "Code and documentation: github.com/milkyway3257/Warpdrive-spaceapps-2026")
