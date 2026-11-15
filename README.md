# SafeSow — what to sow before and after the flood

**NASA Space Apps Challenge 2026 · Local event: Guayaquil, Ecuador**
**Challenge:** Field Shift: Adapting Farms with NASA Data · **Team:** WarpDrive

### ▶️ Live app: https://milkyway3257.github.io/Warpdrive-spaceapps-2026/
(Spanish: add `?lang=es` · works on any phone, nothing to install)

SafeSow is a free, bilingual web app that tells smallholder rice farmers in **Daule, Salitre, Samborondón (Guayas) and Babahoyo (Los Ríos)** what to sow **before and after a flood** during the 2026–27 El Niño. It turns 45 years of NASA data into a short, concrete action plan — it does not only predict, it **prescribes**.

---

## The problem

- On 6 Nov 2026 Ecuador's official El Niño committee (**ERFEN**) warned that this event could be comparable to 1982–83 and 1997–98, with peak intensity in Nov–Dec 2026 and impacts until Mar 2027.
- The Guayas Prefecture estimates **161,357 ha at flood risk, 129,449 ha of them rice**; Salitre, Daule and Santa Lucía hold 64 % of the area at risk (reported by *Primicias*).
- Smallholder farmers must decide what to sow right now, without data they can use.

## What SafeSow does

**Farmer layer (3 taps):**
1. **Where is your farm?** Pick one of 4 zones, type your hectares or **mark your plots** on a satellite photo (tap corners, drag to adjust) or **walk the edge with the phone's GPS**. The app computes the area, tells you which zone you are in, and uses terrain height to say whether the plot is **low or high**. **"Where does water pool?"** colours the lower (blue) and higher (green) ground around you.
2. **My farm:** saved plots (renamable), total hectares, low/high ground, link to Google Maps. Stored **only on the phone**.
3. **What do you need?** *I'm going to sow* or *My field flooded*, with the El Niño switch set by the ERFEN warning.
4. **What to do:** traffic-light result, flood gauge and probability, 3–4 short actions, **3 El Niño duration scenarios** (ends in December / April / June), a **12-hour rain outlook** with what to do today, **🔊 Listen** (read aloud), sources, and **share by WhatsApp**.
5. **After the flood:** pick the month the water went down → the month to sow again and which crops fit.
6. **📚 Learn:** 6 simple cards with audio and a glossary.

**Technical layer (Full analysis):** globe-to-Ecuador zoom, NASA findings, Monte Carlo bars, map with NASA GIBS layers, rain vs. crop water demand chart, comparison of **3 rotation strategies** (S0 rice + rice/ratoon · S1 rice → soybean · S2 water-tolerant cover → dry-season rice), after-flood planner and MODIS greenness chart.

## NASA data used

| Dataset | What we use it for |
|---|---|
| [**NASA POWER**](https://power.larc.nasa.gov/) (AG community) | Monthly precipitation 1981–2025 (El Niño analysis, Monte Carlo); monthly climatology 2001–2025: temperature, radiation (crop water demand) |
| [**MODIS MOD13Q1 v061 NDVI**](https://lpdaac.usgs.gov/products/mod13q1v061/) (Terra, 250 m, 16-day), via Microsoft Planetary Computer | Greenness time series on real rice paddies (clouds and duplicates removed, 3×3 median) |
| [**NASA GIBS**](https://nasa-gibs.github.io/gibs-api-docs/) map tiles | MODIS 3-day flood, MODIS true colour, MODIS NDVI, **GPM IMERG** precipitation rate, SEDAC flood-hazard frequency 1985–2003 |

**Other sources:** NOAA ONI (which years were strong El Niño) · Copernicus DEM 90 m via [Open-Meteo](https://open-meteo.com/) (terrain height) · NOAA GFS / ECMWF forecasts via Open-Meteo (12-hour outlook) · Esri World Imagery (high-resolution photo; the app shows its capture date) · FAO-56, INIAP, IRRI, FAO and Bailey-Serres et al. (2010) for agronomy.

## How it works

- **Crop water demand (FAO-56):** ET0 with the Hargreaves equation from NASA POWER temperature and radiation; crop demand = Kc × ET0 (FAO-56 Table 12); irrigation = Σ max(0, demand − rain). Daule, Jun–Sep: rice ≈ 748 mm vs. soybean ≈ 553 mm → **26 % less water, ≈ 2 million litres per hectare**.
- **Monte Carlo (1,000 runs, seeded):** resample real Jan–Apr rain totals 1981–2025 with small log-normal noise and count how often the season exceeds 1.5 × the median. Pools: all years / strong El Niño years (1983, 1988, 1992, 1998, 2010, 2016, 2024 — NOAA ONI) / extraordinary (1983, 1998). Daule: **27 % / 40 % / 99 %**.
- **Low or high plot:** plot centre height vs. the median of 8 points on a 1.5 km ring (±1 m). The "water pools" map compares a 10 × 10 grid against its median (±1.5 m).
- **Area:** geodesic polygon area (checked: a 100 × 100 m square = 1.0 ha).
- **Architecture:** a single static page (`index.html`, HTML + JavaScript) on GitHub Pages — no server and no database. Libraries: Leaflet, Chart.js, PapaParse. All calculations run on the user's phone.

## Key findings (NASA POWER, Daule cell)

| | El Niño year | Normal (median) |
|---|---|---|
| Rain Nov–Dec | **918 mm** (1997) | 39 mm |
| Rain Jan–Apr | **2,432 mm** (1998), 3.7 × normal | 651 mm |
| Rain in May | **406 mm** (1998) · 387 mm (1983) | 27 mm |

→ El Niño rain starts early, is much heavier and lasts longer: **do not sow the dry-season crop before June.** Only 3 of the 7 strong El Niños flooded this area, which is why SafeSow gives scenarios, not a single forecast.

## Honest limits

- 4 rice zones only; other regions (e.g. the Sierra) need their own crops and climate data — the method is the same.
- NASA POWER cells are ~50 km: Daule, Salitre and Samborondón share one cell.
- Only 2 extraordinary El Niños in 45 years: probabilities are a guide, not a certainty (the app says so).
- Terrain height is a 90 m model; the app asks farmers to confirm in the field.
- The Esri photo is not live (Babahoyo: 2016); the app shows the date.
- Offline: GPS and hectares work without signal; maps and terrain height need internet.
- `data/crops.csv` lists a 180-day rice cycle (FAO generic); the app uses a 120-day local cycle (`LOCAL_RICE_DAYS`).
- Not yet tested with farmers in the field — next step.

## Repository structure

| Path | Contents |
|---|---|
| `index.html` | **The SafeSow app** (single file, served by GitHub Pages) |
| `data/` | CSV data the app reads (`climate_monthly.csv`, `crops.csv`, `ndvi_timeseries.csv`) and the download scripts (`colab_power_sites.py`, `power_tools.py`) |
| `docs/` | Constitution, specification, data notes, rotation rules (with sources), glossary |
| `app/` | Earlier Streamlit prototype (backup: https://warpdrive-spaceapps.streamlit.app) |
| `media/` | Images and video for the pitch |

**Run locally:** `python3 -m http.server 8000` in this folder, then open http://localhost:8000. No build step.

## Privacy

Plots are saved only in the browser on the farmer's phone (`localStorage`). Nothing is sent to a server.

## Use of AI

AI assistants (Claude, Gemini) were used to help with research, coding, writing and translation. The team defined the problem, chose the data and the science, and checked every number. All code and data are open in this repository.

## Team WarpDrive

- **Alejandro Avelino** — captain; product, app design and development, pitch
- **Diego Lino** — NASA data: NASA POWER and MODIS NDVI processing
- **Isaac Aguilar** — agronomy: crops, Kc values, rotation strategies and sources

**Thanks to** mentor Alexis (insights, prescriptions, Monte Carlo, simpler interface) and to a rice agronomist, the father of Valeria Moreno, who reviewed the app and asked for El Niño duration scenarios and the "where does water pool" map.

## License

MIT
