# CAT 793 F AC Performance Curves - Fitting Summary

## Overview

**Model:** CAT 793 F AC  
**Data Source:**   
**Fitting Method:** rational  
**Extraction Date:** 

## Curve Fitting Results

### Rimpull Curve

**Model Type:** rational  
**Formula:** (a + b*v) / (1 + c*v + d*v^2)  

**Quality Metrics:**
- R² = 0.948593 (94.86% variance explained)
- RMSE = 0.00 kN
- Max Error = 0.00 kN
- Mean Error = 0.00 kN

**Physical Constraints:**
- Maximum Rimpull: 1100 kN
- Speed Range: 0 - 64 km/h

**Conditions:** Sea level, 30°C (86°F), standard tires

### Source Gradeability Data

**Empty Truck (169,802 kg):**

| Grade % | Rimpull (kN) | Rimpull (tf) | Speed (km/h) |
|---------|--------------|--------------|--------------|
| 30      | 420.0        | 42.83        | 13           |
| 25      | 360.0        | 36.71        | 16           |
| 20      | 300.0        | 30.59        | 20           |
| 15      | 230.0        | 23.45        | 24           |
| 10      | 160.0        | 16.32        | 36           |
| 5       | 90.0         | 9.18         | 55           |
| 3       | 50.0         | 5.10         | 60           |

**Loaded Truck (390,089 kg):**

| Grade % | Rimpull (kN) | Rimpull (tf) | Speed (km/h) |
|---------|--------------|--------------|--------------|
| 30      | 1100.0       | 112.17       | 0            |
| 25      | 920.0        | 93.81        | 3            |
| 20      | 760.0        | 77.50        | 5            |
| 15      | 560.0        | 57.10        | 12           |
| 10      | 370.0        | 37.73        | 16           |
| 5       | 195.0        | 19.88        | 30           |
| 3       | 130.0        | 13.26        | 60           |

---
*Generated on 2025-11-28*  
*Version: 1.0.0*
