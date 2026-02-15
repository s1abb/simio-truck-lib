# CAT 794 AC Performance Curves - Fitting Summary

## Overview

**Model:** CAT 794 AC  
**Data Source:**   
**Fitting Method:** rational  
**Extraction Date:** 

## Curve Fitting Results

### Rimpull Curve

**Model Type:** rational  
**Formula:** (a + b*v) / (1 + c*v + d*v^2)  

**Quality Metrics:**
- R² = 0.952458 (95.25% variance explained)
- RMSE = 0.00 kN
- Max Error = 0.00 kN
- Mean Error = 0.00 kN

**Physical Constraints:**
- Maximum Rimpull: 1400 kN
- Speed Range: 0 - 60 km/h

**Conditions:** Sea level, 30°C (86°F), 53/80 R63 tires

### Source Gradeability Data

**Empty Truck (222,525 kg):**

| Grade % | Rimpull (kN) | Rimpull (tf) | Speed (km/h) |
|---------|--------------|--------------|--------------|
| 30      | 620.0        | 63.22        | 13           |
| 25      | 520.0        | 53.03        | 15           |
| 20      | 420.0        | 42.83        | 18           |
| 15      | 320.0        | 32.63        | 26           |
| 10      | 220.0        | 22.43        | 37           |
| 6       | 130.0        | 13.26        | 60           |

**Loaded Truck (521,631 kg):**

| Grade % | Rimpull (kN) | Rimpull (tf) | Speed (km/h) |
|---------|--------------|--------------|--------------|
| 30      | 1400.0       | 142.76       | 0            |
| 25      | 1260.0       | 128.48       | 6            |
| 20      | 1000.0       | 101.97       | 8            |
| 15      | 720.0        | 73.42        | 11           |
| 10      | 520.0        | 53.03        | 16           |
| 5       | 250.0        | 25.49        | 33           |
| 3       | 130.0        | 13.26        | 60           |

---
*Generated on 2025-11-28*  
*Version: 1.0.0*
