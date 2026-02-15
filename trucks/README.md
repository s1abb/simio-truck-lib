# Mining Equipment Performance Data Library

This directory contains performance specifications, curve fitting analysis, and structured data for mining equipment used in Simio simulation models.

## 📁 Directory Structure

```
trucks/
├── specifications/           # Source PDFs and technical specification documents
│   ├── CAT_794_AC_Tech_Specs.pdf
│   ├── CAT_794_AC_Tech_Specs.txt        # Extracted text
│   ├── Komatsu_830E-5_Tech_Specs.pdf
│   ├── Komatsu_830E-5_Tech_Specs.txt    # Extracted text
│   ├── Tonly_DTE145_Tech_Specs.pdf
│   └── Tonly_DTE145_Tech_Specs.txt      # Extracted text
│
├── data/                     # Structured equipment data (JSON)
│   ├── cat_793f/
│   │   ├── specifications.json      # Basic specs (weights, dimensions, etc.)
│   │   ├── performance_curves.json  # Rimpull/retarding curves
│   │   └── metadata.json           # Source info, corrections, quality metrics
│   ├── cat_794_ac/
│   │   ├── specifications.json
│   │   ├── performance_curves.json
│   │   └── metadata.json
│   ├── komatsu_830e_5/
│   │   └── ...
│   └── tonly_dte145/
│       └── ...
│
├── outputs/                  # Generated visualizations and reports
│   ├── cat_793f/
│   │   ├── performance_curves.png
│   │   ├── quick_reference.md
│   │   └── curve_fitting_summary.md
│   ├── cat_794_ac/
│   │   ├── performance_curves.png
│   │   ├── quick_reference.md
│   │   └── curve_fitting_summary.md
│   └── ...
│
├── utilities/                # Python scripts for data extraction and processing
│   ├── pdf_extractor.py          # Extract text from specification PDFs
│   ├── curve_fitting.py          # Core curve fitting functions
│   ├── data_extraction.py        # Extract data from spec sheets
│   ├── visualization.py          # Generate charts and graphs
│   ├── export_utils.py           # JSON/MD export utilities
│   ├── validation.py             # Cross-check and validation functions
│   └── templates/                # Markdown/JSON templates
│       ├── specifications_schema.json
│       ├── performance_curves_schema.json
│       ├── metadata_schema.json
│       ├── quick_reference_template.md
│       └── curve_fitting_summary_template.md
│
├── docs/                     # General documentation and methodology
│   ├── curve_fitting_methodology.md
│   ├── data_extraction_guide.md
│   ├── validation_procedures.md
│   └── equipment_comparison.md
│
└── README.md                # This file
```

## 🎯 Purpose

This library provides:
- **Standardized equipment specifications** for simulation input
- **Performance curves** (rimpull, retarding) derived from OEM data
- **Validation and quality metrics** for curve fitting accuracy
- **Reusable utilities** for adding new equipment models

## 📊 Supported Equipment

| Model          | Manufacturer | Payload (t) | Status     | Notes                     |
| -------------- | ------------ | ----------- | ---------- | ------------------------- |
| CAT 793F AC    | Caterpillar  | 218         | ✅ Complete | Y-axis correction applied |
| CAT 794 AC     | Caterpillar  | 297         | ✅ Complete | Y-axis correction applied |
| Liebherr T 236 | Liebherr     | 100         | ✅ Complete | Trolley assist supported  |
| Liebherr T 264 | Liebherr     | 240         | ✅ Complete | Trolley assist supported  |
| Komatsu 830E-5 | Komatsu      | 231         | 🟡 Pending  | Spec sheet available      |
| TONLY DTE145   | TONLY        | 145         | 🟡 Pending  | Spec sheet available      |

## 🔧 Adding New Equipment

### 1. Add Technical Specifications
Place the PDF/source document in `specifications/`:
```bash
specifications/Manufacturer_Model_Tech_Specs.pdf
```

### 2. Extract PDF Text
Extract text from the PDF for easier searching and reference:
```bash
cd utilities
python pdf_extractor.py --all                           # Extract all PDFs
python pdf_extractor.py --pdf "CAT 794 AC Tech Specs.pdf"  # Extract specific PDF
```
This creates `.txt` files alongside the PDFs in the `specifications/` directory.

### 3. Extract Gradeability Data
Manually extract data points from charts or use OCR tools:
- Empty truck: grade %, rimpull (kN or tf), speed (km/h)
- Loaded truck: grade %, rimpull (kN or tf), speed (km/h)
- Retarding power (kW or hp)
- Basic specifications (weights, dimensions, tire size)

### 4. Run Curve Fitting
```bash
cd utilities
python curve_fitting.py --model manufacturer_model --config config.yaml
```

### 5. Review and Validate
- Check R² values (target: >0.99)
- Verify physical constraints (max rimpull, speed limits)
- Compare with similar equipment
- Review generated visualizations

### 6. Export Structured Data
The script automatically generates:
- `data/{model}/specifications.json`
- `data/{model}/performance_curves.json`
- `data/{model}/metadata.json`
- `outputs/{model}/performance_curves.png`
- `outputs/{model}/quick_reference.md`
- `outputs/{model}/curve_fitting_summary.md`

## 📐 Data Schemas

### specifications.json
```json
{
  "model": "cat_794_ac",
  "manufacturer": "Caterpillar",
  "category": "ultra_class_haul_truck",
  "weights": {
    "empty_kg": 217419,
    "loaded_kg": 521631,
    "payload_kg": 304212
  },
  "dimensions": {
    "wheelbase_mm": 6645,
    "length_mm": 14600,
    "width_mm": 9300,
    "height_mm": 7450
  },
  "tires": {
    "size": "53/80_R63",
    "pressure_kpa": 620
  },
  "drivetrain": {
    "type": "AC_electric_drive",
    "max_speed_kmh": 60,
    "total_reduction_ratio": "35:1"
  }
}
```

### performance_curves.json
```json
{
  "rimpull_curve": {
    "model_type": "rational_function",
    "formula": "(a + b*v) / (1 + c*v + d*v^2)",
    "coefficients": {...},
    "data": {
      "speed_kmh": [0, 1, 2, ...],
      "rimpull_kn": [...],
      "rimpull_tf": [...]
    },
    "constraints": {
      "max_rimpull_kn": 1500,
      "max_speed_kmh": 70
    }
  },
  "retarding_curve": {
    "continuous_power_kw": 4086,
    "efficiency": 0.85,
    "data": {
      "speed_kmh": [1, 2, 3, ...],
      "retarding_kn": [...],
      "retarding_tf": [...]
    }
  },
  "gradeability_data": {
    "empty": {...},
    "loaded": {...}
  }
}
```

### metadata.json
```json
{
  "data_source": "CAT 794 AC Technical Specifications (AEHQ7083-09)",
  "extraction_date": "2025-11-26",
  "extracted_by": "username",
  "fitting_method": "rational_curve_fit",
  "fitting_quality": {
    "r_squared": 0.9976,
    "rmse_kn": 16.30
  },
  "corrections_applied": [
    "Y-axis mislabeling correction (10x multiplier)"
  ],
  "validation_status": "verified",
  "notes": "Compared with CAT 793F for validation"
}
```

## 🧪 Validation Procedures

### Physical Constraints
- Max rimpull scaling should match payload ratios
- Speed limits should not exceed OEM specifications
- Power calculations should be consistent

### Cross-Equipment Validation
- Compare similar payload class trucks
- Verify manufacturer trends (e.g., CAT 793F vs 794 AC)
- Check against industry benchmarks

### Curve Fitting Quality
- **R² > 0.99**: Excellent fit
- **R² 0.95-0.99**: Good fit, review outliers
- **R² < 0.95**: Poor fit, investigate data or model

## 🛠️ Utilities Overview

### pdf_extractor.py
Extracts text from specification PDFs:
- Batch extraction of all PDFs
- Individual PDF extraction
- Creates searchable .txt files
- Page-by-page extraction with markers
- Requires: `pip install PyPDF2`

### curve_fitting.py
Fits mathematical curves to gradeability data:
- Rational functions (best for electric drive)
- Polynomial functions
- Power/exponential functions
- Automatic model selection based on R²

### data_extraction.py
Helper functions for extracting data from spec sheets:
- Manual data entry templates
- Validation checks
- Unit conversions (tf ↔ kN, hp ↔ kW)

### visualization.py
Generates standardized charts:
- Rimpull vs speed curves
- Retarding vs speed curves
- Gradeability comparisons
- Multi-equipment overlays

### export_utils.py
Export data in multiple formats:
- JSON (for simulation import)
- Markdown (documentation)
- PNG (visualizations)
- CSV (data tables)

## 📝 Usage Examples

### Import Performance Curves in Python
```python
import json

# Load CAT 794 AC performance data
with open('data/cat_794_ac/performance_curves.json', 'r') as f:
    curves = json.load(f)

# Get rimpull at specific speed
speed_kmh = 30
idx = curves['rimpull_curve']['data']['speed_kmh'].index(speed_kmh)
rimpull_kn = curves['rimpull_curve']['data']['rimpull_kn'][idx]
print(f"Rimpull at {speed_kmh} km/h: {rimpull_kn:.1f} kN")
```

### Generate Quick Reference
```python
from utilities.export_utils import generate_quick_reference

generate_quick_reference(
    model='cat_794_ac',
    output_dir='outputs/cat_794_ac'
)
```

### Compare Multiple Trucks
```python
from utilities.visualization import plot_comparison

models = ['cat_793f', 'cat_794_ac', 'komatsu_830e_5']
plot_comparison(models, output='outputs/equipment_comparison.png')
```

## 🔄 Migration Notes

### From Previous Structure
The old `trucks/calcs/` directory has been reorganized:
- ✅ JSON files → `data/{model}/performance_curves.json`
- ✅ PNG files → `outputs/{model}/performance_curves.png`
- ✅ Documentation → `outputs/{model}/` (model-specific) or `docs/` (general)
- ✅ Python scripts → `utilities/`

### Naming Conventions
- **Models**: lowercase with underscores (e.g., `cat_794_ac`, `komatsu_830e_5`)
- **Files**: snake_case (e.g., `performance_curves.json`)
- **Directories**: lowercase, descriptive (e.g., `specifications`, `outputs`)

## 📚 References

- [Curve Fitting Methodology](docs/curve_fitting_methodology.md)
- [Simio Parameter Mapping](docs/simio_parameter_mapping.md)
- [Data Extraction Guide](docs/data_extraction_guide.md) (TBD)
- [Validation Procedures](docs/validation_procedures.md) (TBD)

## 🤝 Contributing

When adding new equipment:
1. Follow the directory structure above
2. Use the provided schemas for JSON files
3. Run validation checks before committing
4. Document any corrections or assumptions
5. Generate all output files (JSON, PNG, MD)

## ⚠️ Important Notes

- Always verify Y-axis scaling on gradeability charts (common source of 10x errors)
- Document units clearly (kN vs tf, kW vs hp)
- Apply physical constraints to prevent unrealistic extrapolations
- Cross-validate with similar equipment when possible
- Preserve original source data and document all transformations
