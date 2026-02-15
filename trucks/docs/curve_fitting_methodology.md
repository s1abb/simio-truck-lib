# Curve Fitting Methodology

This document describes the mathematical methodology for fitting performance curves to equipment gradeability data.

## Overview

Mining equipment manufacturers provide gradeability charts showing the relationship between grade %, rimpull force, and speed for both empty and loaded conditions. We fit mathematical curves to these discrete data points to generate continuous performance curves for simulation use.

## Mathematical Models

### 1. Rational Function (Recommended)

**Formula:**
```
F(v) = (a + b·v) / (1 + c·v + d·v²)
```

**Best for:** AC electric drive trucks (smooth torque curves)

**Characteristics:**
- 4 parameters (a, b, c, d)
- Smooth, continuous curve
- Good extrapolation behavior
- Physically realistic at low speeds
- Excellent fit for electric drive characteristics

**Fitting Method:** Non-linear least squares (scipy.optimize.curve_fit)

**Example:** CAT 794 AC
```
F = (12,169 - 201·v) / (1 + 1.468·v - 0.0246·v²)
R² = 0.9976 (99.76% fit)
RMSE = 16.30 kN
```

### 2. Polynomial

**Formula:**
```
F(v) = a + b·v + c·v² + d·v³ + ...
```

**Best for:** When high accuracy is needed over limited range

**Characteristics:**
- Flexible (n parameters)
- Can oscillate between data points
- Poor extrapolation
- May produce unrealistic values outside data range

**Caution:** Higher order polynomials (n > 3) often overfit

### 3. Power Function

**Formula:**
```
F(v) = a / (v + b)^c
```

**Best for:** Mechanical drive trucks

**Characteristics:**
- 3 parameters
- Physically meaningful (power-limited)
- Good for constant power curves
- Limited flexibility for complex curves

### 4. Exponential Decay

**Formula:**
```
F(v) = a·e^(-b·v) + c
```

**Best for:** Alternative smooth curve

**Characteristics:**
- 3 parameters
- Smooth decay
- Asymptotic to c at high speed
- May not fit as well as rational for electric drives

## Fitting Procedure

### Step 1: Data Extraction

Extract gradeability data from manufacturer spec sheets:

**Empty Truck:**
- Grade % (e.g., 5, 10, 15, 20, 25, 30)
- Corresponding rimpull (kN or tf)
- Corresponding speed (km/h)

**Loaded Truck:**
- Grade % (e.g., 5, 10, 15, 20, 25)
- Corresponding rimpull (kN or tf)
- Corresponding speed (km/h)

**Critical:** Verify Y-axis units! Common error: mislabeled as 0-150 instead of 0-1500.

### Step 2: Data Preparation

1. **Convert to consistent units** (kN recommended)
   - 1 tonne-force (tf) = 9.80665 kN
   
2. **Combine empty and loaded data**
   - Use all data points for fitting
   - Creates 11-15 total points (typical)
   
3. **Check for outliers**
   - Plot data points
   - Verify physical consistency

### Step 3: Model Selection

Test multiple models and compare:

```python
from curve_fitting import compare_models

results = compare_models(speed_data, force_data)

# Select model with highest R²
best_model = max(results.items(), key=lambda x: x[1]['metrics']['r_squared'])
```

**Selection Criteria:**
- R² > 0.99: Excellent
- R² > 0.95: Good
- R² < 0.95: Investigate issues

### Step 4: Apply Physical Constraints

**Maximum Rimpull:**
- Cap at realistic value based on:
  - Comparison with similar equipment
  - Payload scaling ratios
  - Manufacturer specifications
  
**Example:**
```python
# CAT 793F: ~1,100 kN (220t payload)
# CAT 794 AC: ~1,500 kN (297t payload)
# Scaling ratio: 297/220 = 1.35x
# Expected max: 1,100 × 1.35 = 1,485 kN ✓
```

**Speed Limits:**
- Min: 0 km/h
- Max: OEM max speed + margin (typically 60-70 km/h)

### Step 5: Quality Assessment

**Metrics:**
- **R²** (coefficient of determination): Proportion of variance explained
- **RMSE** (root mean square error): Average prediction error
- **Max Error:** Largest absolute error
- **Mean Error:** Average absolute error

**Target Values:**
- R² > 0.99 for excellent fit
- RMSE < 2% of max force
- Max error < 5% of local force

### Step 6: Validation

**Physical Validation:**
1. Check max rimpull vs similar equipment
2. Verify payload scaling (should be ~1.3-1.4x for similar % increase)
3. Ensure smooth curve (no oscillations)
4. Validate speed limits

**Cross-Equipment Validation:**
```
Example: CAT 793F vs 794 AC
- Payload ratio: 297/220 = 1.35x
- Max rimpull ratio: 1,500/1,100 = 1.36x
- Match: ✓ (within 1%)
```

**Power Validation:**
```
Power = Force × Velocity
At 15 km/h, 523 kN:
P = 523 kN × (15/3.6) m/s = 2,180 kW
Reasonable for 297t truck climbing 10% grade ✓
```

## Retarding Curve

Retarding curves are power-limited and simpler to model.

**Formula:**
```
F(v) = P_eff / v
```

Where:
- P_eff = continuous power × efficiency
- v = velocity (m/s)

**With low-speed limit:**
```
F(v) = min(P_eff / v, F_max)
```

**Example:**
```python
retarding_power_kw = 4086  # From spec sheet
efficiency = 0.85          # Typical for electric retarding
max_retarding_kn = 2000    # Low-speed limit

speeds_ms = speeds_kmh / 3.6
retarding_kn = min(
    (retarding_power_kw * efficiency) / speeds_ms,
    max_retarding_kn
)
```

## Complete Curve Generation

After fitting, generate complete curves at 1 km/h intervals:

```python
speeds = np.arange(0, 71, 1)  # 0-70 km/h, 1 km/h steps
rimpull_kn = fitted_function(speeds)
rimpull_kn = np.minimum(rimpull_kn, max_rimpull_kn)  # Apply constraint
rimpull_tf = rimpull_kn / 9.80665  # Convert to tf
```

**Output:**
- 71 data points (0-70 km/h)
- Both kN and tf units
- Ready for simulation import

## Common Issues and Solutions

### Issue: Poor Fit (R² < 0.95)

**Possible Causes:**
1. Y-axis scaling error (10x common!)
2. Incorrect units (kN vs tf)
3. Data transcription errors
4. Wrong model for drive type

**Solutions:**
1. Verify Y-axis carefully
2. Check unit consistency
3. Re-extract data points
4. Try different curve models

### Issue: Unrealistic Max Rimpull

**Indicators:**
- Max rimpull 5-10x higher than similar equipment
- Doesn't scale with payload

**Solutions:**
1. Check for Y-axis mislabeling (divide by 10)
2. Verify tf vs kN conversion
3. Apply physical constraint based on similar equipment

### Issue: Oscillating Curve

**Causes:**
- High-order polynomial
- Too few data points

**Solutions:**
1. Use rational function instead
2. Reduce polynomial order
3. Add more data points from spec sheet

### Issue: Poor Extrapolation

**Causes:**
- Polynomial or exponential model
- Extrapolating far beyond data range

**Solutions:**
1. Use rational or power function
2. Limit speed range to data coverage
3. Add high-speed data points if available

## Best Practices

1. **Always plot the fitted curve with data points** - Visual inspection catches issues
2. **Document all assumptions and corrections** - Especially unit conversions and scaling
3. **Cross-validate with similar equipment** - Verify physical reasonableness
4. **Preserve original data** - Keep source data separate from fitted curves
5. **Version control** - Track changes and corrections
6. **Quality metrics** - Always report R², RMSE, and validation method

## References

- scipy.optimize.curve_fit documentation
- Mining equipment performance theory
- OEM technical specifications
- Comparative equipment databases

## See Also

- [Data Extraction Guide](data_extraction_guide.md)
- [Validation Procedures](validation_procedures.md)
- [Utilities README](../utilities/README.md)
