# Physics: Speed and Force Dynamics

**Applies to:** ALL trucks, ALL modes  
**Purpose:** Calculate truck acceleration and speed based on available power, grade, and resistance forces  
**Related:** [01-fleet-and-modes.md](01-fleet-and-modes.md), [03-power-flow.md](03-power-flow.md), [07-trolley-power-sharing.md](07-trolley-power-sharing.md)

---

## Overview

This section describes the **universal speed dynamics** that apply to all trucks regardless of operating mode. The calculations determine:
- Target speed considering path and truck limits
- Tractive force (rimpull or retarding) with power degradation
- **Traction limits** based on tire-ground friction
- Resistance forces (grade and rolling resistance)
- Net acceleration and speed update

**Key Feature:** For SustainSpeed modes, an additional **power-limited scaling factor** applies to ensure tractive force respects both mechanical limits (curves) and electrical power limits when combining sources.

---

## Input Parameters

```
Current State:
├─ CurrentSpeedKmh          // Current truck speed (km/h)
├─ CurrentGrade             // Current path grade (%)
├─ CurrentWeightKg          // Empty or loaded weight (kg)
├─ DesiredSpeedKmh          // Target speed from operator/path
└─ Loaded                   // Boolean: truck is loaded

Truck Specifications (from tbl_TruckTypes):
├─ MaxSpeedKmh_Loaded       // Maximum loaded speed
├─ MaxSpeedKmh_Empty        // Maximum empty speed
├─ BaseRimpullForceN        // Rated rimpull force (N)
├─ BaseRetardForceN         // Rated retarding force (N)
├─ RollingResistance        // Rolling resistance coefficient (typically 0.02)
├─ GrossVehicleWeight       // Loaded weight (kg)
└─ EmptyVehicleWeight       // Empty weight (kg)

Degradation State:
├─ BatteryHealthPct         // Current battery health (100 = new, 80 = end of life)
├─ PowerDegradationActive   // Boolean flag to enable/disable degradation
└─ EndOfLifeBatteryHealthPct // Minimum health threshold (typically 80%)

Path Conditions:
├─ OnElectricPath           // Boolean: is truck on trolley-enabled path?
├─ ElectricPathSpeedLimit   // Speed limit on electric path (km/h)
└─ RoadFrictionCoefficient  // Surface friction μ (typically 0.7 dry, 0.4 wet, 0.3 muddy)

Operating Mode:
├─ TruckMode                // "BatterySwap", "DieselElectric", "BatteryElectric"
└─ ElectricAssistMode       // "PreserveEnergy", "SustainSpeed", "PreserveBattery", etc.

Power Availability (for SustainSpeed modes):
├─ TotalAvailablePowerKw    // Combined power from all sources (from power flow)
├─ AvailableMotorPowerKw    // Motor thermal limit (from power flow)
└─ TrolleyPowerCapacityKw   // Dynamic trolley power (from power sharing)

Simulation Control:
└─ TimeStepSeconds          // Simulation timestep (seconds, typically 1-10)
```

---

## Speed Update Calculations (11-Step Process)

### STEP 1: Determine Power Degradation Factor

```pseudocode
IF (TruckMode == "BatterySwap" OR TruckMode == "BatteryElectric"):
    // Battery trucks experience power degradation as battery ages
    IF (PowerDegradationActive == TRUE):
        PowerDegradationFactor = MAX(
            BatteryHealthPct / 100, 
            EndOfLifeBatteryHealthPct / 100
        )
    ELSE:
        PowerDegradationFactor = 1.0
    END IF
ELSE:
    // DieselElectric trucks - no power degradation
    PowerDegradationFactor = 1.0
END IF
```

**Note:** At 80% battery health, PowerDegradationFactor = 0.8, meaning available power = 80% of rated power.

---

### STEP 2: Determine Maximum Allowable Speed

```pseudocode
IF (Loaded == TRUE):
    MaxSpeedKmh = MaxSpeedKmh_Loaded
ELSE:
    MaxSpeedKmh = MaxSpeedKmh_Empty
END IF
```

**Note:** Loaded trucks have lower maximum speed than empty trucks.

---

### STEP 3: Determine Target Speed Considering Path Limits

```pseudocode
IF (OnElectricPath == TRUE):
    TargetSpeedKmh = MIN(ElectricPathSpeedLimit, DesiredSpeedKmh, MaxSpeedKmh)
ELSE:
    TargetSpeedKmh = MIN(DesiredSpeedKmh, MaxSpeedKmh)
END IF
```

**Note:** Electric paths may have speed limits for safety or power capacity constraints.

---

### STEP 4: Calculate Tractive Force

#### Step 4a: Get Baseline Force from Curves

```pseudocode
IF (CurrentSpeedKmh < TargetSpeedKmh):
    // Accelerating - apply rimpull force
    BaselineForceN = BaseRimpullForceN × PowerDegradationFactor
ELSE:
    // Braking/maintaining - apply retarding force
    BaselineForceN = -BaseRetardForceN × PowerDegradationFactor
END IF
```

**Note:** Rimpull and retard curves represent motor/drivetrain capability, not traction limits.

#### Step 4b: Apply Power-Limited Scaling (SustainSpeed Modes Only)

```pseudocode
IF (ElectricAssistMode == "SustainSpeed" AND CurrentSpeedKmh < TargetSpeedKmh):
    // SustainSpeed mode: combine power sources and apply power limit
    
    // Determine total available power from all sources
    IF (TruckMode == "DieselElectric"):
        IF (OnElectricPath == TRUE):
            // Diesel + trolley combined
            TotalAvailablePowerKw = DieselGeneratorMaxPowerKw + TrolleyPowerCapacityKw
        ELSE:
            // Diesel only
            TotalAvailablePowerKw = DieselGeneratorMaxPowerKw
        END IF
    
    ELSE IF (TruckMode == "BatteryElectric"):
        // Apply degradation to battery power
        MaxBatteryPowerKw = MaxBatteryPowerKw × PowerDegradationFactor
        
        IF (OnElectricPath == TRUE):
            // Battery + trolley combined
            TotalAvailablePowerKw = MaxBatteryPowerKw + TrolleyPowerCapacityKw
        ELSE:
            // Battery only
            TotalAvailablePowerKw = MaxBatteryPowerKw
        END IF
    
    ELSE:
        // BatterySwap mode doesn't use SustainSpeed
        TotalAvailablePowerKw = MaxBatteryPowerKw × PowerDegradationFactor
    END IF
    
    // Consider motor thermal limits (from Section 3.2 of power flow)
    TotalAvailablePowerKw = MIN(TotalAvailablePowerKw, AvailableMotorPowerKw)
    
    // Calculate power-limited force using P = F × V
    SpeedMs = CurrentSpeedKmh / 3.6
    
    IF (SpeedMs > 0):
        // At non-zero speed: apply power limit
        PowerLimitedForceN = (TotalAvailablePowerKw × 1000) / SpeedMs
        
        // Use minimum of curve limit and power limit
        TractiveForceN = MIN(BaselineForceN, PowerLimitedForceN)
    ELSE:
        // At standstill: use curve-based force (power limit = infinity)
        TractiveForceN = BaselineForceN
    END IF

ELSE:
    // PreserveEnergy/PreserveBattery modes or braking: use baseline force
    // Force/speed unchanged - only energy source accounting differs
    TractiveForceN = BaselineForceN
END IF
```

**Critical:** For SustainSpeed modes, `TrolleyPowerCapacityKw` must be **dynamically calculated** from power sharing (see [07-trolley-power-sharing.md](07-trolley-power-sharing.md)), not a static property.

---

### STEP 5: Calculate Traction Limit

```pseudocode
// ============================================================================
// Calculate normal force considering grade
// Note: CurrentWeightKg is already set based on Loaded state (see Step 2)
// ============================================================================

GradeAngleRad = ATAN(CurrentGrade / 100)
NormalForceN = CurrentWeightKg × 9.81 × COS(GradeAngleRad)

// ============================================================================
// Calculate traction limit
// ============================================================================

TractionLimitN = RoadFrictionCoefficient × NormalForceN

// Convert to kN for comparison with curve forces
TractionLimitKN = TractionLimitN / 1000
```

**Physics Explanation:**

**Maximum force equation:**
```
F_max = μ × N = μ × m × g × cos(θ)

Where:
  μ = coefficient of friction (tire-to-road)
  N = normal force (perpendicular to surface)
  m = truck mass (kg)
  g = 9.81 m/s²
  θ = grade angle
```

**Typical friction coefficients:**
- **Dry compacted gravel:** μ = 0.7 - 0.8
- **Wet gravel:** μ = 0.4 - 0.6
- **Muddy conditions:** μ = 0.3 - 0.4
- **Icy conditions:** μ = 0.1 - 0.2

**Grade effects on normal force:**
```
Flat (0°):     Normal force = m × g × 1.000
10% grade:     Normal force = m × g × 0.995  (-0.5%)
20% grade:     Normal force = m × g × 0.980  (-2.0%)
30% grade:     Normal force = m × g × 0.957  (-4.3%)
```

**Simplification:** For typical mining grades (<20%), can approximate `cos(θ) ≈ 1.0` with <2% error.

---

### STEP 6: Apply Traction Limit to Tractive Force

```pseudocode
// ============================================================================
// Apply traction limit to ensure force doesn't exceed tire-ground friction
// ============================================================================

IF (TractiveForceN > 0):
    // Rimpull (accelerating/climbing): limit by traction
    TractiveForceN = MIN(TractiveForceN, TractionLimitN)
ELSE:
    // Retarding (braking/descending): limit by traction (negative force)
    TractiveForceN = MAX(TractiveForceN, -TractionLimitN)
END IF
```

**When Traction Limiting Matters:**

**For Rimpull (Accelerating):**
- ✅ **Empty trucks** on poor road conditions (μ < 0.5)
- ✅ **All trucks** on wet/muddy roads (μ = 0.3-0.4)
- ✅ **Low speeds** where motor capability exceeds traction
- ❌ **Loaded trucks on dry roads** - curves already conservative (~40% of traction)

**For Retarding (Braking):**
- ✅ **All trucks at low speeds** (0-10 km/h) - motor capability 2-5× traction
- ✅ **Empty trucks** at higher speeds
- ✅ **All conditions** - retarding curves show motor capability, not friction limits

**Example: CAT 794 AC Retarding at 1 km/h**
```
Motor capability:      8,000 kN (from retarding curve)
Traction (loaded, μ=0.7):  3,578 kN
Traction (empty, μ=0.7):   1,527 kN
Actual force limited to traction values → prevents wheel lock-up
```

---

### STEP 7: Calculate Resistance Forces

```pseudocode
GradeResistanceForceN = CurrentWeightKg × 9.81 × (CurrentGrade / 100)
RollingResistanceForceN = CurrentWeightKg × 9.81 × RollingResistance
```

**Notes:**
- Grade resistance opposes motion on upslopes (positive grade)
- Grade resistance assists motion on downslopes (negative grade)
- Rolling resistance always opposes motion

---

### STEP 8: Calculate Net Force and Acceleration

```pseudocode
NetTractiveForceN = TractiveForceN - GradeResistanceForceN - RollingResistanceForceN
AccelerationMs2 = NetTractiveForceN / CurrentWeightKg
```

**Note:** Net force can be positive (accelerating), negative (decelerating), or zero (steady state).

---

### STEP 9: Update Speed (Integrate Acceleration)

```pseudocode
NewSpeedMs = (CurrentSpeedKmh / 3.6) + (AccelerationMs2 × TimeStepSeconds)
NewSpeedKmh = NewSpeedMs × 3.6
```

**Note:** Simple Euler integration over timestep.

---

### STEP 10: Apply Limits

```pseudocode
NewSpeedKmh = MAX(0, MIN(MaxSpeedKmh, NewSpeedKmh))
```

**Note:** Speed cannot be negative or exceed maximum.

---

### STEP 11: Update Movement Rate

```pseudocode
MovementRate = NewSpeedKmh  // km/h
```

**Note:** This updates the truck's movement rate in the simulation.

---

## Traction Limit Examples

### Example 1: CAT 794 AC Loaded on Dry Road

**Specifications:**
- Gross weight: 521,631 kg
- Friction coefficient: μ = 0.7 (dry compacted gravel)
- Grade: 10% (climbing)

**Calculations:**
```
Normal force = 521,631 × 9.81 × cos(atan(0.1)) = 5,110,734 N
Traction limit = 0.7 × 5,110,734 = 3,577,514 N = 3,578 kN

Rimpull curve at 0 km/h: 1,400 kN
Rimpull curve at 16 km/h: 502 kN
Rimpull curve at 30 km/h: 265 kN

Result: Curve forces well below traction limit → curves dominate ✓
```

### Example 2: CAT 794 AC Empty on Wet Road

**Specifications:**
- Empty weight: 222,525 kg
- Friction coefficient: μ = 0.4 (wet gravel)
- Grade: 0% (flat)

**Calculations:**
```
Normal force = 222,525 × 9.81 × 1.0 = 2,182,970 N
Traction limit = 0.4 × 2,182,970 = 873,188 N = 873 kN

Rimpull curve at 0 km/h: 1,400 kN → Limited to 873 kN ⚠️
Rimpull curve at 10 km/h: 799 kN → OK (below limit) ✓
Rimpull curve at 16 km/h: 502 kN → OK (below limit) ✓

Result: Traction limiting active at low speeds on wet roads
```

### Example 3: Liebherr T236 Retarding at Low Speed

**Specifications:**
- Loaded weight: 180,000 kg
- Friction coefficient: μ = 0.7
- Speed: 1 km/h
- Grade: -10% (descending)

**Calculations:**
```
Normal force = 180,000 × 9.81 × cos(atan(-0.1)) = 1,764,180 N
Traction limit = 0.7 × 1,764,180 = 1,234,926 N = 1,235 kN

Retarding curve at 1 km/h: 2,500 kN
Actual retarding force: 1,235 kN (traction-limited)

Result: Traction limit prevents wheel lock-up ✓
Motor has excess capability for safety margin
```

### Example 4: Traction Limit vs Speed

**CAT 794 AC Loaded (521,631 kg, μ = 0.7)**

| Speed (km/h) | Retarding Curve (kN) | Traction Limit (kN) | Actual Force (kN) | Limited By |
| ------------ | -------------------- | ------------------- | ----------------- | ---------- |
| 1            | 8,000                | 3,578               | **3,578**         | Traction   |
| 5            | 2,501                | 3,578               | **2,501**         | Curve      |
| 10           | 1,250                | 3,578               | **1,250**         | Curve      |
| 20           | 625                  | 3,578               | **625**           | Curve      |
| 40           | 313                  | 3,578               | **313**           | Curve      |

**Pattern:** Traction limiting only matters at very low speeds (<5 km/h) for retarding.

---

## Configuration Parameters

### Recommended Friction Coefficients

```
// Default values for different road conditions
FrictionCoefficient_Dry = 0.7        // Dry compacted gravel (conservative)
FrictionCoefficient_Wet = 0.4        // Wet gravel
FrictionCoefficient_Muddy = 0.3      // Muddy/slippery conditions
FrictionCoefficient_Icy = 0.15       // Ice/snow (extreme conditions)

// Can vary by:
// - Weather conditions (dry/wet/snow)
// - Road maintenance quality
// - Tire condition/type
// - Surface material (gravel vs paved)
```

### Typical Mining Road Conditions

| Season/Condition  | Typical μ | Notes                    |
| ----------------- | --------- | ------------------------ |
| Dry summer        | 0.7 - 0.8 | Best traction            |
| Light rain        | 0.5 - 0.6 | Slightly reduced         |
| Heavy rain        | 0.4 - 0.5 | Moderately reduced       |
| Muddy             | 0.3 - 0.4 | Significantly reduced    |
| Graded/maintained | +0.1      | Better than unmaintained |
| Worn tires        | -0.1      | Worse than new tires     |

---

## Power-Limited Scaling Factor (SustainSpeed Modes)

**Applies to:** DieselElectric + SustainSpeed, BatteryElectric + SustainSpeed  
**Purpose:** Calculate maximum tractive force considering both mechanical limits (curves) and electrical power limits when combining power sources

### Design Rationale

**Why Power-Limited Scaling:**

1. **Existing curves capture mechanical limits** - Tire adhesion, drivetrain capacity already validated
2. **SustainSpeed changes available power** - Not fundamental vehicle mechanics
3. **Physically accurate** - Uses Power = Force × Velocity relationship
4. **Reuses validated data** - No new curve derivation required
5. **Natural regime transition** - Seamlessly handles curve-limited vs power-limited conditions

**Alternatives Considered (and Rejected):**

- ❌ **New Curves:** Extensive data collection/validation for each truck+trolley combination
- ❌ **Direct Curve Scaling:** Assumes linear power-force relationship (not physically accurate at all speeds)
- ✅ **Power-Limited Scaling:** Combines curve reuse with physics accuracy

### Mathematical Foundation

```
Power-Force-Velocity Relationship:
    Power (kW) = Force (kN) × Velocity (m/s)
    Force (kN) = Power (kW) / Velocity (m/s)

Implementation:
    CurveLimitForceN = BaseRimpullForceN × PowerDegradationFactor
    PowerLimitForceN = (TotalAvailablePowerKw × 1000) / SpeedMs
    TractionLimitForceN = μ × m × g × cos(θ)
    ActualForceN = min(CurveLimitForceN, PowerLimitForceN, TractionLimitForceN)
```

### Speed Regime Examples

#### Low Speed (5 km/h on steep grade)

```
Curve rimpull:  800 kN        (tire adhesion limit)
Power limit:    (8000 kW × 1000) / 1.39 m/s = 5,755 kN
Traction limit: 3,578 kN       (μ = 0.7, loaded)
Result:         Curve-limited (800 kN)
Limiting factor: Mechanical limits dominate
```

#### Medium Speed (20 km/h on 8% grade)

```
Curve rimpull:  400 kN
Power limit:    (8000 kW × 1000) / 5.56 m/s = 1,439 kN
Traction limit: 3,578 kN
Result:         Curve-limited (400 kN)
Limiting factor: Still within mechanical capability
```

#### High Speed (35 km/h approaching max)

```
Curve rimpull:  150 kN        (curves taper at high speed)
Power limit:    (8000 kW × 1000) / 9.72 m/s = 823 kN
Traction limit: 3,578 kN
Result:         Curve-limited (150 kN)
Limiting factor: Curves dominate
```

**Key Observation:** In most practical scenarios, mechanical limits (curves) dominate. Traction limits matter primarily at low speeds or poor conditions. Power limit becomes relevant when sustaining high speeds on grades.

### SustainSpeed Performance Benefit

**Key Insight:** Higher power enables **sustaining** higher speeds on grades where baseline truck would slow down.

**Example: Loaded climb on 10% grade**

| Speed (km/h) | Resistance Force | Baseline Power (2500 kW)      | With Trolley (7500 kW) | Benefit   |
| ------------ | ---------------- | ----------------------------- | ---------------------- | --------- |
| 15           | 350 kN           | Can sustain                   | Can sustain            | No change |
| 20           | 350 kN           | Slowing down (208 kW deficit) | Can sustain            | +5 km/h   |
| 25           | 350 kN           | Cannot reach                  | Can sustain            | +10 km/h  |
| 30           | 350 kN           | Cannot reach                  | Can sustain            | +15 km/h  |

**Net Effect:**
- Faster average speed without violating mechanical constraints
- System naturally transitions between curve-limited (low speed), power-limited (high speed), and traction-limited (poor conditions) regimes
- Maintains physics accuracy by respecting all three constraint types

### Critical Integration with Power Sharing

**⚠️ WARNING:** Must use **dynamically calculated** trolley power from power sharing, not static properties.

```pseudocode
// ✅ CORRECT - Dynamic trolley power from power sharing
ActiveTrucksOnSection = CurrentPath.NumberTravelers
SharedPowerKw = TrolleySectionTotalPowerKw / ActiveTrucksOnSection
TrolleyPowerKw = min(SharedPowerKw, TrolleyMaxPowerPerTruckKw) × Efficiency

TotalAvailablePowerKw = BasePowerKw + TrolleyPowerKw  // Use dynamic value

// ❌ WRONG - Static property overestimates available power
TotalAvailablePowerKw = BasePowerKw + TrolleyMaxPowerKw  // Ignores sharing
```

**Physics Validation Example (10 MW section, 5 MW truck limit):**

| Active Trucks | Shared Power         | TrolleyPowerKw (93% eff) | Total Power (4MW base) | Section Load           |
| ------------- | -------------------- | ------------------------ | ---------------------- | ---------------------- |
| 1 truck       | 5 MW (truck-limited) | 4.65 MW                  | 8.65 MW                | ✅ 4.65 MW (valid)      |
| 3 trucks      | 3.3 MW               | 3.07 MW                  | 7.07 MW                | ✅ 9.2 MW total (valid) |
| 6 trucks      | 1.7 MW               | 1.58 MW                  | 5.58 MW                | ✅ 9.5 MW total (valid) |
| **Wrong**     | -                    | **5 MW (static)**        | **9 MW**               | ❌ Would need 54 MW!    |

**See:** [07-trolley-power-sharing.md](07-trolley-power-sharing.md) for complete power sharing implementation.

---

## Key Considerations

### Three-Tier Force Limiting System

**All forces must respect:**
1. **Curve limits** - Motor/drivetrain mechanical capability (from manufacturer data)
2. **Power limits** - Electrical power availability (P = F × v)
3. **Traction limits** - Tire-ground friction (μ × m × g × cos(θ))

**Actual force = MIN(curve_limit, power_limit, traction_limit)**

### Power Degradation

- **Only applies** to battery-powered trucks (BatterySwap, BatteryElectric)
- **Reduces available power** as battery ages
- **Example:** At 80% health, available power = 80% of rated power
- **DieselElectric trucks:** No power degradation (diesel generator constant)

### Speed Targets

- **Electric paths** may have speed limits (safety or power capacity constraints)
- **Operator desired speed** may be lower than maximum
- **Loaded trucks** have lower maximum speed than empty trucks

### Force Balance

- **Rimpull** accelerates the truck forward
- **Grade resistance** opposes motion on slopes (assists on downslopes)
- **Rolling resistance** always opposes motion
- **Net force** determines acceleration

### Mode-Specific Behavior

- **PreserveEnergy/PreserveBattery modes:** Speed/force unchanged, only energy source accounting differs
- **SustainSpeed modes:** Power-limited scaling enables higher sustained speeds on grades
- **BatterySwap/StandAlone modes:** Standard force calculations, no trolley interaction

### Traction Limit vs Load State

**Empty trucks are more susceptible to traction limiting:**
- Lower mass → lower normal force → lower traction limit
- Same motor capability as loaded
- Can exceed traction on wet/muddy roads
- Especially critical for retarding forces at low speeds

**Loaded trucks are more protected:**
- Higher mass → higher traction limit
- Curves already conservative (~40% of available traction on dry roads)
- Traction limiting only matters in extreme conditions (μ < 0.3)

---

## Related Documents

- [01-fleet-and-modes.md](01-fleet-and-modes.md) - Operating modes and configurations
- [03-power-flow.md](03-power-flow.md) - Power source management and motor thermal limits
- [07-trolley-power-sharing.md](07-trolley-power-sharing.md) - Dynamic trolley power allocation
- [08-degradation-models.md](08-degradation-models.md) - Battery health calculation