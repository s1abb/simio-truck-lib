# LIEBHERR T 264 - Quick Reference for Simulation

## Core Specifications

```
Model: LIEBHERR T 264
Manufacturer: Liebherr
Empty Weight: 176,000 kg
Loaded Weight: 416,000 kg
Payload: 240 tonnes (240,000 kg)
Max Speed: 0 km/h
Tire Size: N/A
Wheelbase: 0 mm
Drivetrain: AC_electric_drive
```

## Performance Summary

### Rimpull Curve

| Speed (km/h) | Rimpull (kN) | Rimpull (tf) |
|--------------|--------------|--------------|
| 0            | 1000.0       | 102.0        |
| 10           | 592.0        | 60.4         |
| 20           | 295.4        | 30.1         |
| 30           | 196.2        | 20.0         |
| 40           | 146.2        | 14.9         |
| 50           | 114.6        | 11.7         |

**Max Rimpull:** 1000 kN  
**Model Type:** rational

### Retarding System

**Continuous Power:** 3500 kW (None hp)  
**Efficiency:** 85%  
**Type:** dynamic_brake

## Data Quality

**R² Score:** 0.9964  
**RMSE:** N/A  
**Fitting Method:** rational  
**Validation Status:** draft

## Usage Example (Python)

```python
import json

# Load performance curves
with open('data/liebherr_t_264/performance_curves.json', 'r') as f:
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
