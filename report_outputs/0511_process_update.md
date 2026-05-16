# Process update — 2026-05-11

## Context

Google Earth Engine (GEE) is used here only as a **cloud execution + catalog** layer: we do **not** download full-country rasters locally. The first delivered table is **Hansen Global Forest Change** forest loss summarized to **admin‑2 polygons** (FAO GAUL 2015) for **Zambia**, **calendar year 2013**.

---

## Completed

| Item | Detail |
|------|--------|
| **Pipeline** | `gee_zambia/hansen_zonal.py` → `data/raw/exposure_gee/zambia/hansen_loss_y2013_admin2_zambia.csv` |
| **Source image** | `UMD/hansen/global_forest_change_2025_v1_13` (`lossyear` 13 = 2013) |
| **Boundaries** | GAUL 2015 level 2, `ADM0_NAME == Zambia` |
| **Notebook** | `exposure_notebooks/zambia_gee_v2.ipynb` — auth, small raster checks, CSV load |
| **CSV fix** | `loss_area_ha` now populated (GEE `Reducer.sum()` exposes **`sum`** m²; script maps to ha) |

**Table read — `hansen_loss_y2013_admin2_zambia.csv` (post‑rerun)**

- **72 rows** — one row per GAUL **district (ADM2)** in Zambia in this boundary product.
- **National total (Hansen 2013 forest loss):** **~157,847 ha** (`loss_area_ha` summed over rows). Interpret as **mapped stand‑replacement forest loss attributed to 2013** at ~30 m; not fire, not sub‑annual timing within 2013.
- **Spatial concentration:** largest single‑district values are on the order of **6,000–8,800 ha** (e.g. Mkushi, Mpika, Solwezi, Serenje, Mumbwa in this extract). Use for **relative** cross‑district comparison unless/until joined to survey geographies with an explicit spatial link rule.
- **Provenance columns:** `_hansen_image`, `_loss_calendar_year`, `_lossyear_band_value` record which catalog asset and year filter produced each row.

---

## PI direction (queued)

- **MODIS burned area** and **FIRMS** (or FIRMS‑class products) **inside GEE** — feasible as a **separate** exposure track from Hansen **forest loss**; needs agreed **date range**, **geometry unit** (EA vs district vs raster), and product IDs (e.g. MCD64, VIIRS/SNPP collections) before implementation.

---

## Next steps

1. **Document join logic** (if any): how GAUL ADM2 relates to survey **EA / cluster / district** fields for Zambia 2014 — do not assume identity without a spec.
2. **GEE burned area / FIRMS prototype:** one country, one time window, one zonal statistic — mirror Hansen script pattern (small script + thin notebook section).
3. Re‑run Hansen zonal for other **calendar years** only if the analysis window requires it (`--year`); filenames follow `hansen_loss_y{year}_admin2_zambia.csv`.

---

## References (internal)

- `gee_zambia/README.md` — CLI, auth, `EARTHENGINE_PROJECT` / `--project`
- `skills/memory.md` + `skills/CONVENTIONS.md` — agent handoff and concise communication preference
