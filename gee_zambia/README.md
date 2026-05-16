# Google Earth Engine (Zambia demos)

**Beginner walkthrough:** open [`exposure_notebooks/zambia_gee_v2.ipynb`](../exposure_notebooks/zambia_gee_v2.ipynb) for auth checks and tiny “hello raster” samples before running the scripts below.

## One-time access

1. Register for Earth Engine: [Earth Engine signup](https://code.earthengine.google.com/register) (Google account; research / nonprofit use is standard).
2. Install deps: `pip install -r requirements.txt` (includes `earthengine-api`, which provides **`import ee`** and the **`earthengine`** CLI). Install into the **same Python** you use for notebooks (e.g. from repo root: `source .venv/bin/activate` then `pip install -r requirements.txt`). If you see **`ModuleNotFoundError: No module named 'ee'`**, your shell is using a different interpreter (often conda **`(base)`**) than the venv where packages were installed—activate that venv or run **`.venv/bin/python -m gee_zambia.hansen_zonal`**.
3. Authenticate the Python API on this machine (with that same environment active):

   ```bash
   earthengine authenticate
   ```

   Follow the browser flow. See also: [Python install & auth](https://developers.google.com/earth-engine/guides/python_install).

4. Set **`EARTHENGINE_PROJECT`** to your GCP **project id** (the string id, not the numeric project number), e.g. `export EARTHENGINE_PROJECT=my-project-id`, or put that line in the repository root **`.env`** file — `hansen_zonal` loads `.env` automatically when `python-dotenv` is installed.

5. Optional: if your organization uses a **service account**, set `GOOGLE_APPLICATION_CREDENTIALS` to the JSON path and call `ee.Initialize(project='your-cloud-project-id')` (see Google’s EE service account docs).

## Run Hansen admin-2 loss summary (writes CSV)

From the **repository root** (so `.env` is found), with the same Python env as `earthengine-api`:

```bash
python -m gee_zambia.hansen_zonal --year 2013
```

If `EARTHENGINE_PROJECT` is not in the environment or `.env`, pass the Cloud **project id** explicitly:

```bash
python -m gee_zambia.hansen_zonal --year 2013 --project ipv-exposure-research
```

**Shell tip:** do not put `# comments` on the same line as `earthengine ...` — the CLI will treat them as arguments and error.

Output default: `data/raw/exposure_gee/zambia/hansen_loss_y2013_admin2_zambia.csv`

If you see `Please authorize access to your Earth Engine account`, complete **Authenticate** above and rerun.

Optional: `python -m gee_zambia.hansen_zonal --year 2013 --output /path/to/out.csv`

If `reduceRegions` times out, try again (EE load) or use `--simplified` (coarser GAUL geometries).
