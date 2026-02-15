# Utilities - Technical Reference

Python scripts for processing equipment performance data. See [main README](../README.md) for overview and workflow.

## Quick Start

```bash
# Install dependencies (or use devcontainer)
pip install numpy scipy matplotlib

# Process equipment from config
python process_equipment.py --model cat_794_ac --config config.json --output-dir ..
```

## Modules

| Module | Purpose | Key Functions |
|--------|---------|---------------|
| `curve_fitting.py` | Fit curves to data | `fit_curve()`, `generate_rimpull_curve()`, `compare_models()` |
| `visualization.py` | Generate plots | `plot_performance_curves()`, `plot_comparison()` |
| `export_utils.py` | Export docs/data | `generate_quick_reference()`, `export_to_csv()` |
| `process_equipment.py` | Main pipeline | `process_equipment()` (CLI) |
| `refactor_legacy_data.py` | Migrate old data | `split_legacy_json()` |

## API Examples

### Fit Curves Programmatically

```python
from curve_fitting import fit_curve, generate_rimpull_curve
import numpy as np

# Your gradeability data
speeds = np.array([61, 37, 25, 18, 15, 13, 32, 15, 10, 7, 6])
forces = np.array([110, 220, 320, 420, 530, 620, 250, 520, 780, 1030, 1250])

# Fit curve
fitted_func, coeffs, quality = fit_curve(speeds, forces, 'rational', max_force=1500)

print(f"R² = {quality['r_squared']:.4f}")
print(f"RMSE = {quality['rmse_kn']:.2f} kN")

# Generate complete curve
curve_data = generate_rimpull_curve(
    speed_range=(0, 70),
    fitted_function=fitted_func,
    max_rimpull_kn=1500
)
```

### Generate Plots

```python
from visualization import plot_performance_curves, plot_comparison
from pathlib import Path
import json

# Single equipment
with open('../data/cat_794_ac/performance_curves.json') as f:
    data = json.load(f)

plot_performance_curves(data, output_file=Path('../outputs/cat_794_ac/curves.png'))

# Compare multiple
plot_comparison(['cat_793f', 'cat_794_ac'], Path('../data'), Path('../outputs/comparison.png'))
```

### Export Documentation

```python
from export_utils import generate_quick_reference, export_to_csv

# Load data files
specs = json.load(open('../data/cat_794_ac/specifications.json'))
curves = json.load(open('../data/cat_794_ac/performance_curves.json'))
meta = json.load(open('../data/cat_794_ac/metadata.json'))

# Generate markdown report
generate_quick_reference('cat_794_ac', specs, curves, meta, 
                        Path('../outputs/cat_794_ac/quick_reference.md'))

# Export CSV tables
export_to_csv(curves, Path('../outputs/cat_794_ac'))
```

## Function Reference

### curve_fitting.py

**`fit_curve(speed_data, force_data, model_type='rational', max_force=None)`**
- Fits curve to gradeability data
- Returns: `(fitted_function, coefficients, quality_metrics)`
- Models: `'rational'`, `'polynomial'`, `'power'`, `'exponential'`

**`generate_rimpull_curve(speed_range, speed_step, fitted_function, max_rimpull_kn)`**
- Generates complete curve data at regular intervals
- Returns: `{'speed_kmh': [...], 'rimpull_kn': [...], 'rimpull_tf': [...]}`

**`generate_retarding_curve(retarding_power_kw, efficiency, speed_range, max_retarding_kn)`**
- Generates power-limited retarding curve
- Returns: `{'speed_kmh': [...], 'retarding_kn': [...], 'retarding_tf': [...]}`

**`compare_models(speed_data, force_data)`**
- Tests all curve models and returns quality metrics
- Returns: `{model_type: {'coefficients': [...], 'metrics': {...}}}`

### visualization.py

**`plot_performance_curves(performance_data, title, output_file, show_gradeability_points)`**
- Plots rimpull and retarding curves side-by-side

**`plot_comparison(models, data_dir, output_file, curve_type='rimpull')`**
- Overlays curves from multiple equipment models

**`plot_gradeability_chart(gradeability_data, title, output_file)`**
- Traditional gradeability chart (grade % vs speed)

**`generate_all_plots(model, data_dir, output_dir)`**
- Generates all standard plots for a model

### export_utils.py

**`generate_quick_reference(model, specifications, performance_curves, metadata, output_file)`**
- Creates quick reference markdown document

**`generate_curve_fitting_summary(model, performance_curves, metadata, output_file)`**
- Creates detailed curve fitting analysis report

**`export_to_csv(performance_curves, output_dir)`**
- Exports rimpull and retarding curves to CSV files

## Templates

Schema files in `templates/`:
- `specifications_schema.json` - Equipment specs format
- `performance_curves_schema.json` - Curve data format  
- `metadata_schema.json` - Quality metrics format

## Notes

- All curve fitting uses scipy's non-linear least squares
- Default: rational function (best for AC electric drives)
- Target R² > 0.99 for excellent fit
- Always apply max_rimpull constraint to prevent unrealistic extrapolation
- See [methodology doc](../docs/curve_fitting_methodology.md) for theory
