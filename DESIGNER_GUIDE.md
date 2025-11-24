# Designer Guide for create_forecast_ad_hoc

## What this repo does
- Builds traffic-zone (TAZ) forecasts by combining baseline spatial layers with project "index" inputs and exporting updated shapefiles/CSVs for approval and modeling.
- Runs mainly through `main.ipynb`, which orchestrates geospatial joins, demand/supply adjustments, and final exports.
- Uses Papermill to optionally re-run a base forecast notebook (`create_forecast_basic/run_basic.ipynb`) when a new TAZ layer is provided.

## High-level flow
1) Read run config from `inputs_outputs.xlsx` (client folder, version/date, target year, flags for potentials/new TAZ, kollim factor).
2) Load base TAZ shapefile from the client `For_approval/Reference_tabels/shp` folder and convert polygons to points for joins.
3) Spatial-join TAZ with background layers: urban class, school district, PUMA, Jerusalem city/metro, subdistrict, municipality.
4) If a new TAZ layer is present, re-run the base forecast via Papermill (`create_forecast_basic/run_basic.ipynb`); otherwise use packaged 2020 baseline data.
5) Load the project "index" (shapefile + Excel), split its attributes across overlapping TAZs, and merge supplies (housing, dorms, employment floor area, classrooms).
6) Merge with 2020 baseline fields, then compute students/dorms/uni, yeshiva/kollim uplift, employment by sector, and population/household adjustments.
7) Assign DISTRICT/PUMA, aggregate where needed, and export updated TAZ shapefiles plus PUMA-level CSVs to the client `For_approval` folder.

## Flow diagram (text)
```
inputs_outputs.xlsx
   ↓ config
Base TAZ layer → point centroids → spatial joins with background layers
   ↓
New TAZ layer?
   ├─ yes → Papermill run: create_forecast_basic/run_basic.ipynb → 2020 baseline
   └─ no  → packaged 2020 baseline
   ↓
Index SHP + Excel → split to TAZ → merge supplies
   ↓
Demand/education/employment calculations + yeshiva uplift
   ↓
DISTRICT/PUMA classification + optional aggregation
   ↓
Exports: For_approval/… shapefiles & PUMA CSVs
```

## Key directories & artifacts
- Root notebooks: `main.ipynb` (orchestrator), `add_results_to_geo.ipynb` (post-processing), empty `README.md` placeholder.
- Core code: `global_functions.py` (loaders, spatial splits, muni name mapping), `create_forecast_basic/run_basic.py` & `current/run_current.py` (Papermill helpers).
- Data prep notebooks: `create_forecast_basic/current/*.ipynb` (CBS cleanup, students, employment); `create_forecast_basic/arab_and_palestinian/*` (scenario-specific prep).
- Inputs: `inputs_outputs.xlsx` (run settings), `background_files/` (urban/PUMA/municipal borders, projections, promoter ratios, etc.), client `For_approval/Reference_tabels/*` (TAZ layers, index files).
- Outputs: client `For_approval/` shapefiles (`*_taz_for_approval.shp`, optional `*_new_taz_for_project.shp`) and PUMA CSVs (`*_puma<year>_V4…csv`).

## How to talk about it with designers
- This pipeline enriches and rebalances a geospatial TAZ layer; the designer touchpoints are the exported shapefiles/CSVs in `For_approval/` and the configuration spreadsheet.
- Visuals to expect: TAZ boundaries colored by sector/PUMA/DISTRICT; tables with housing, population, students, and employment by TAZ/PUMA.
- Changing inputs (new TAZs, different potentials, kollim factor, target year) alters those outputs; the notebooks handle the plumbing.

## Typical run (conceptual)
- Update `inputs_outputs.xlsx` with client paths, forecast version/date, target year (2030/2040/2050), flags for potentials/new TAZ, kollim factor.
- Place/update base TAZ and index layers in the client `For_approval/Reference_tabels/shp` folder.
- Execute `main.ipynb` (or Papermill-run) to regenerate outputs into the client `For_approval/` directory.
