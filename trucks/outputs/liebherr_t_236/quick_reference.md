# LIEBHERR T 236 - Quick Reference for Simulation

## Core Specifications

```
Model: LIEBHERR T 236
Manufacturer: Liebherr
Empty Weight: 80,000 kg
Loaded Weight: 180,000 kg
Payload: 100 tonnes (100,000 kg)
Max Speed: 0 km/h
Tire Size: N/A
Wheelbase: 0 mm
Drivetrain: AC_electric_drive
```

## Performance Summary

### Rimpull Curve

| Speed (km/h) | Rimpull (kN) | Rimpull (tf) |
|--------------|--------------|--------------|
| 0            | 500.0        | 51.0         |
| 10           | 233.7        | 23.8         |
| 20           | 116.6        | 11.9         |
| 30           | 77.5         | 7.9          |
| 40           | 57.9         | 5.9          |
| 50           | 46.1         | 4.7          |
| 60           | 38.2         | 3.9          |

**Max Rimpull:** 500 kN  
**Model Type:** rational

### Retarding System

**Continuous Power:** 1045 kW (None hp)  
**Efficiency:** 85%  
**Type:** dynamic_brake

## Data Quality

**R² Score:** 0.9934  
**RMSE:** N/A  
**Fitting Method:** rational  
**Validation Status:** draft

## Usage Example (Python)

```python
import json

# Load performance curves
with open('data/liebherr_t_236/performance_curves.json', 'r') as f:
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
