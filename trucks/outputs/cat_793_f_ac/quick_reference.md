# CAT 793 F AC - Quick Reference for Simulation

## Core Specifications

```
Model: CAT 793 F AC
Manufacturer: Caterpillar
Empty Weight: 169,802 kg
Loaded Weight: 390,089 kg
Payload: 218 tonnes (220,287 kg)
Max Speed: 64 km/h
Tire Size: standard
Wheelbase: 5905 mm
Drivetrain: AC_electric_drive
```

## Performance Summary

### Rimpull Curve

| Speed (km/h) | Rimpull (kN) | Rimpull (tf) |
|--------------|--------------|--------------|
| 0            | 1100.0       | 112.2        |
| 10           | 507.6        | 51.8         |
| 20           | 306.3        | 31.2         |
| 30           | 219.3        | 22.4         |
| 40           | 170.8        | 17.4         |
| 50           | 139.9        | 14.3         |
| 60           | 118.4        | 12.1         |

**Max Rimpull:** 1100 kN  
**Model Type:** rational

### Retarding System

**Continuous Power:** 3550 kW (None hp)  
**Efficiency:** 85%  
**Type:** dynamic_brake

## Data Quality

**R² Score:** 0.9486  
**RMSE:** N/A  
**Fitting Method:** rational  
**Validation Status:** draft

## Usage Example (Python)

```python
import json

# Load performance curves
with open('data/cat_793_f_ac/performance_curves.json', 'r') as f:
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
