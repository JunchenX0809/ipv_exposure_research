# Country scope in GEE (one line)

We limit work to a single country by loading the global **FAO GAUL 2015** admin‑2 polygon collection in Earth Engine and filtering with `ee.Filter.eq("ADM0_NAME", "<country>")`, so every `reduceRegions` call runs only on features whose GAUL country label matches that string (swap `"Zambia"` for another country’s exact `ADM0_NAME` as stored in GAUL to reuse the same pattern).
