# Single-File Runner Outline

Goal: collapse the repo into one Python script (`run_all.py`) that executes the core notebooks headlessly with Papermill and minimal external wiring.

## Requirements
- Python 3.10+; install `pip install -r requirements.txt` (needs papermill, pandas, geopandas/fiona stack, nbformat, openpyxl).
- Access to client data folders referenced in `inputs_outputs.xlsx` (For_approval/Reference_tabels/shp, background_files, etc.).

## Script behavior (conceptual)
- Read `inputs_outputs.xlsx` for defaults; allow CLI overrides (client folder, forecast version/date, target year, flags `index_with_poten`, `new_taz_made`, `kollim_factor`).
- Optionally trigger the base-layer refresh by running `create_forecast_basic/run_basic.ipynb` with Papermill when a new TAZ layer is supplied.
- Run `main.ipynb` with Papermill so all joins/calculations/exports happen without opening notebooks.
- Emit output notebooks (`*_output.ipynb`) alongside the originals for traceability.

## Example `run_all.py`
```python
import argparse
from pathlib import Path
import pandas as pd
import papermill as pm

ROOT = Path(__file__).parent

# Small helper to execute any notebook headlessly

def run_notebook(notebook_path, params=None):
    nb_path = ROOT / notebook_path
    out_path = nb_path.with_name(nb_path.stem + "_output.ipynb")
    pm.execute_notebook(str(nb_path), str(out_path), parameters=params or {})
    return out_path

def load_config(cfg_path):
    cfg = pd.read_excel(cfg_path)
    vals = cfg["location"]
    return {
        "client_data_folder": vals[0],
        "forecast_version": vals[1],
        "v_date": vals[2],
        "index_with_poten": int(vals[3]),
        "new_taz_made": int(vals[4]),
        "kollim_factor": float(vals[5]),
        "year": int(vals[6]),
    }

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--client-data-folder")
    p.add_argument("--forecast-version")
    p.add_argument("--v-date")
    p.add_argument("--year", type=int, choices=[2030, 2040, 2050])
    p.add_argument("--index-with-poten", type=int, choices=[0, 1])
    p.add_argument("--new-taz-made", type=int, choices=[0, 1])
    p.add_argument("--kollim-factor", type=float)
    p.add_argument("--run-base", action="store_true", help="Rebuild base layer via create_forecast_basic/run_basic.ipynb")
    p.add_argument("--new-layer-path", help="Shapefile/GDB to pass into run_basic when --run-base is set")
    return p.parse_args()

def main():
    args = parse_args()
    cfg = load_config(ROOT / "inputs_outputs.xlsx")

    # Override config when CLI args are provided
    for key, arg_name in [
        ("client_data_folder", "client_data_folder"),
        ("forecast_version", "forecast_version"),
        ("v_date", "v_date"),
        ("year", "year"),
        ("index_with_poten", "index_with_poten"),
        ("new_taz_made", "new_taz_made"),
        ("kollim_factor", "kollim_factor"),
    ]:
        val = getattr(args, arg_name, None)
        if val is not None:
            cfg[key] = val

    if args.run_base:
        if not args.new_layer_path:
            raise SystemExit("--new-layer-path required when --run-base is used")
        run_notebook(
            "create_forecast_basic/run_basic.ipynb",
            params={
                "output_folder_path": f"{cfg['client_data_folder']}\\For_approval\\Reference_tabels",
                "new_layer_path": args.new_layer_path,
            },
        )

    # Main pipeline run (relies on inputs_outputs.xlsx + any overrides baked in there)
    run_notebook("main.ipynb")

if __name__ == "__main__":
    main()
```

Notes:
- `main.ipynb` reads `inputs_outputs.xlsx` from the repo root; if you need the overrides reflected there, update the sheet before calling `run_notebook` (or adjust the notebook to accept Papermill parameters for full CLI control).
- Papermill outputs a copy with `_output.ipynb`; keep it for logs or set `progress_bar=False, log_output=True` in `execute_notebook` for quieter runs.
- The script assumes the same folder layout the notebooks expect (background_files in root, client data folders reachable via paths in the config sheet).

## Minimal run sequence
```
python -m venv .venv
.venv\\Scripts\\pip install -r requirements.txt
.venv\\Scripts\\python run_all.py --run-base --new-layer-path "<path_to_new_TAZ_layer>" --year 2040 --index-with-poten 1 --kollim-factor 0.5
```
- Drop `--run-base`/`--new-layer-path` if you want to use the packaged 2020 baseline instead of regenerating it.
