# CAT 794 AC - Quick Reference for Simulation

## Core Specifications

```
Model: CAT 794 AC
Manufacturer: Caterpillar
Empty Weight: 222,525 kg
Loaded Weight: 521,631 kg
Payload: 297 tonnes (299,106 kg)
Max Speed: 60 km/h
Tire Size: 53/80_R63
Wheelbase: 6645 mm
Drivetrain: AC_electric_drive
```

## Performance Summary

### Rimpull Curve

| Speed (km/h) | Rimpull (kN) | Rimpull (tf) |
|--------------|--------------|--------------|
| 0            | 1400.0       | 142.8        |
| 10           | 798.7        | 81.4         |
| 20           | 400.7        | 40.9         |
| 30           | 265.3        | 27.1         |
| 40           | 198.0        | 20.2         |
| 50           | 157.8        | 16.1         |
| 60           | 131.2        | 13.4         |

**Max Rimpull:** 1400 kN  
**Model Type:** rational

### Retarding System

**Continuous Power:** 4086 kW (None hp)  
**Efficiency:** 85%  
**Type:** dynamic_brake

## Data Quality

**R² Score:** 0.9525  
**RMSE:** N/A  
**Fitting Method:** rational  
**Validation Status:** draft

## Usage Example (Python)

```python
import json

# Load performance curves
with open('data/cat_794_ac/performance_curves.json', 'r') as f:
    curves = json.load(f)

# Get rimpull at 30 km/h
speed_idx = curves['rimpull_curve']['data']['speed_kmh'].index(30.0)
rimpull_kn = curves['rimpull_curve']['data']['rimpull_kn'][speed_idx]
print(f"Rimpull at 30 km/h: {rimpull_kn:.1f} kN")
```

## References

**Data Source:**   
**Extraction Date:**   
**Version:** 1.0.0

---
*Generated on 2025-11-28*
