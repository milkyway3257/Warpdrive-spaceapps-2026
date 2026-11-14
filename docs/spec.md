# Specification v1 — Flood-aware crop rotation planner for rice farmers (Guayas & Los Ríos, Ecuador)

Team WARPDRIVE · NASA Space Apps 2026 · Challenge: "Field Shift: Adapting Farms with NASA Data"
Status: v1 for team review (14 Nov 2026, 13:00). Product name: **TBD by the team**.

---

## 1. Objective and context

Rice farmers in the lowlands of Guayas and Los Ríos usually plant rice after rice all year (wet-season rice, then dry-season rice or ratoon). During El Niño years, wet-season floods drown young rice and farmers lose their investment; in 2026–27 El Niño is forecast to be very strong and about 129,000 ha of rice in Guayas are at risk. Today the decision "plant or not, and what" is made by fear, not data.

**Scene:** María grows 4 ha of rice near Daule. It is November and the news says a strong El Niño is coming. She opens the tool on her phone, chooses her area and her current crop, and in under two minutes sees three rotation options for the next 12 months, a month-by-month calendar showing when each option is exposed to flood season and how much water it needs in the dry season, and a clear note on what she should confirm with a local technician. In March her field floods; she opens the "After a flood" section, enters when the water went down, and sees which options still fit before the dry season.

**Success measure:** a farmer (or a judge) gets a comparison of at least 3 rotation strategies for their location in **under 2 minutes**, without help.

## 2. Users

| User | Who they are | What they can / cannot do |
|---|---|---|
| **Smallholder rice farmer** (primary) | Grows rice on ~1–5 ha in Daule, Salitre, Samborondón or Babahoyo. Knows farming deeply; little experience with apps or maps. | Can choose a place on a list/map and a crop. Will not read technical terms unless explained in one line. |
| **Extension technician / association leader** (secondary) | Works for MAG, a farmers' association or an NGO; advises many farmers. | Uses the comparison and data sources to discuss options with farmers. |
| **Farmer's family / lender** (receives results, does not use the app) | Shares the decision or finances the season. | Sees a screenshot or summary; needs plain language and clear risks. |

## 3. User stories

- **US1** — As a rice farmer, I want to select my location and current crop, so that results apply to my area.
- **US2** — As a rice farmer, I want to compare at least three rotation strategies (including what I do today), so that I can see which one exposes my crop less to flood season.
- **US3** — As a rice farmer, I want a month-by-month calendar for each strategy, so that I know what would be in my field each month and when the field is bare.
- **US4** — As a rice farmer, I want to know how much water each strategy needs in the dry season, so that I can plan irrigation or choose a crop that uses less water.
- **US5** — As a rice farmer whose field just flooded, I want to enter when the water went down, so that I can see which crops still fit before the dry season.
- **US6** — As a technician, I want to see the NASA data source, period and confidence next to each result, so that I can judge how much to trust it.

## 4. Functional requirements (observable behaviour)

- **RF1.** The user can choose one of the supported locations (initially: Daule, Salitre, Samborondón, Babahoyo) from a list or a map.
- **RF2.** The user can choose the current crop pattern (initially: "rice + rice/ratoon").
- **RF3.** The app shows a 12-month climate chart for the chosen location: monthly rainfall and water demand (ET0) from NASA POWER, with the wet and dry seasons labelled.
- **RF4.** The app shows at least **3 rotation strategies**, one of them being the farmer's current pattern.
- **RF5.** For each strategy, the app shows a **calendar** (12 months) with the crop in the field each month, including bare/fallow months.
- **RF6.** For each strategy, the app shows: **flood-season exposure**, **dry-season water need** (mm of irrigation), **soil-health indicators** (legume yes/no, months of bare soil, breaks monoculture yes/no), and **income/market note**.
- **RF7.** For each strategy, the app shows: **why it is suggested, evidence (NASA data + agronomic source), benefits, information gaps, and risks for local review**.
- **RF8.** The user can choose an **El Niño scenario** (normal / wetter-than-normal) and the flood-season exposure updates accordingly. The scenario is clearly labelled as a scenario, not a forecast.
- **RF9.** **After a flood** section: the user enters the month the water receded (and whether the crop was lost); the app shows how many months remain before the dry season and which crops from the crop table still fit, with their water need. *(Detailed behaviour: see Open questions.)*
- **RF10.** Next to every result: data source, period, spatial resolution and a confidence label (e.g., "zone-level, ~50 km").
- **RF11.** A visible note on every result page: "This tool supports, and does not replace, your judgement and local technical advice."
- **RF12.** When the user reopens the app, it works without internet-dependent data downloads (data comes from CSV files in the repository).

## 5. Rules (with worked example)

**Climate per location** (from `data/climate_monthly.csv`, NASA POWER 2001–2025 climatology):
- Rain (mm/month) = PRECTOTCORR (mm/day) × days in month.
- Temperature corrected to field elevation: T_field = T_cell + 0.0065 × (cell elevation − field elevation).
- ET0 (Hargreaves, FAO-56): ET0 = 0.0023 × (T + 17.8) × √(T2M_RANGE) × 0.408 × Ra.

**Crop water need:** ETc = Kc × ET0 (Kc from `data/crops.csv`, FAO-56 Table 12).
**Dry-season water need (irrigation):** sum over dry-season months of max(0, ETc − rain).
**Flood-season exposure:** number of months the crop is young/in field during the wettest months (Jan–Apr), and rainfall in those months; scenario multiplies wet-season rain by a team-chosen factor (labelled as scenario).
**Soil health:** + legume in rotation; − months of bare soil; + breaks rice-after-rice.

**Worked example — Daule, dry season June–September (NASA POWER climatology, field elevation ≈ 1 m):**

| Month | Rain (mm) | ET0 (mm) | Rice Kc | Rice ETc | Soybean Kc | Soybean ETc |
|---|---|---|---|---|---|---|
| Jun | 9.9 | 155.7 | 1.05 | 163.5 | 0.40 | 62.3 |
| Jul | 3.4 | 172.4 | 1.20 | 206.9 | 1.15 | 198.3 |
| Aug | 2.8 | 187.7 | 1.20 | 225.2 | 1.15 | 215.9 |
| Sep | 2.4 | 189.8 | 0.90 | 170.8 | 0.50 | 94.9 |
| **Total** | **18.5** | | | **766.4** | | **571.4** |

- Dry-season irrigation need: **rice ≈ 748 mm**, **soybean ≈ 553 mm** → soybean needs **≈ 195 mm (≈ 26 %) less water**.
- Known limitations (shown to the user): Hargreaves tends to overestimate ET0 in humid climates; the balance ignores water stored in the soil and paddy percolation; NASA POWER is zone-level (~50 km).

**Candidate strategies (to be validated with sources by the science role):**
- **S0 — Current:** wet-season rice → dry-season rice or ratoon (monoculture).
- **S1 — Rice + legume:** wet-season rice → dry-season soybean (rice–soybean rotation proposed for Babahoyo in the literature).
- **S2 — Avoid flood season:** no rice during the riskiest wet months on flood-prone plots (cover/forage or fallow), rice in the dry season with irrigation.
- (Optional S3 if time allows, defined by the science role.)

## 6. Acceptance criteria (yes/no)

- **CA1.** Choosing Daule and "rice + rice/ratoon" shows 3 strategies (S0, S1, S2) in under 2 minutes from opening the app.
- **CA2.** For Daule, the dry-season irrigation need shown for S0 (rice Jun–Sep) is **≈ 748 mm** and for S1 (soybean Jun–Sep) is **≈ 553 mm** (± 5 % if crop calendars are refined).
- **CA3.** Each strategy shows a 12-month calendar, and bare months are visibly marked.
- **CA4.** Each strategy shows why, evidence, benefits, information gaps and risks.
- **CA5.** Every number on screen has a visible source and period.
- **CA6.** Switching the El Niño scenario changes the flood-season exposure of the strategies, and the screen says "scenario".
- **CA7.** In "After a flood", choosing "water receded in March" shows the months left before the dry season and at least one crop option with its water need.
- **CA8.** The app opens and works from the public link in an incognito window on a phone.

## 7. Edge cases

- **What if the user chooses a location outside the supported list?** → The app only offers supported locations in v1.
- **What if a NASA value is missing (-999 / null)?** → The month is shown as "no data", never filled with zero.
- **What if the flood water recedes too late (e.g., in June)?** → The app says there is not enough wet-season time left and shows only dry-season options with their irrigation need.
- **What if the user's crop is not rice?** → v1 supports rice farmers only; the app says so.
- **What if POWER's grid cell elevation differs a lot from the field (e.g., Babahoyo: cell ≈ 837 m)?** → The corrected temperature is used and the correction is shown.

## Open questions (team must decide before implementing)

1. Exact behaviour of **"After a flood"** (RF9): which inputs (month water receded? crop stage? crop lost yes/no?) and which outputs (list of crops that fit? recommended order?).
2. **El Niño scenario factor** for wet-season rain (e.g., +50 %?) — needs a source or must be presented as a user-chosen "what if".
3. Which crops besides rice and soybean enter the crop table for this zone (science role, with sources), considering clay soils that waterlog.
4. Whether to add a flood-prone map layer (NASADEM elevation / GIBS) in v1 or later.
5. Product name and tagline.

---
SI disclosure: this specification was drafted with an AI assistant (Claude) from decisions made by the team (user, location, problem, and focus on rotation and post-flood decisions), and reviewed by the team.
