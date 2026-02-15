# Battery Degradation Models

**Version:** 1.0  
**Last Updated:** November 2025  
**Status:** Design Specification

---

## Overview

Battery degradation tracking reduces available capacity and power over time, reflecting real-world battery aging. Two models are implemented based on operating characteristics:

1. **Simple Throughput-Based** - Linear degradation for BatterySwap mode (TONLY DTE145)
2. **Advanced Cycle-Life** - Physics-based degradation for BatteryElectric mode (Liebherr T 264 BE)

**Source Documents:**
- Complete_Physics_Implementation_Matrix.md (Section 5, battery degradation models)
- MultiTruckConcept.md (degradation calculations, operating scenarios)

---

## Model Selection by Truck Type

| Truck Type            | Operating Mode                    | Degradation Model       | Reason                                                                           |
| --------------------- | --------------------------------- | ----------------------- | -------------------------------------------------------------------------------- |
| **TONLY DTE145**      | BatterySwap                       | **Simple Throughput**   | Controlled cycling, consistent DoD (20%), station charging, predictable behavior |
| **Liebherr T 264 BE** | BatteryElectric + PreserveBattery | **Advanced Cycle-Life** | Variable DoD (2-5%), dynamic trolley charging, minimal stress                    |
| **Liebherr T 264 BE** | BatteryElectric + SustainSpeed   | **Advanced Cycle-Life** | Variable DoD (10-15%), high discharge rates (0.75C), moderate stress             |
| **Liebherr T 264 BE** | BatteryElectric + StandAlone      | **Advanced Cycle-Life** | Deep DoD (80%), high stress, NOT RECOMMENDED                                     |

---

## 1. Simple Throughput-Based Degradation

### Principle

Battery health degrades linearly with total energy cycled (charge + discharge). Suitable for operations with consistent cycling patterns and controlled charging.

**Applies to:** BatterySwap mode (TONLY DTE145)

### Input Parameters

```
Battery Specifications:
├─ RatedBatteryStorageEnergyKwh       // Nominal capacity (e.g., 801 kWh)
├─ RatedLifetimeThroughputKwh         // Total energy over lifetime (e.g., 160,200 kWh)
└─ EndOfLifeBatteryHealthPct          // Replacement threshold (typically 80%)

Current State:
├─ CurrentCumulativeThroughputKwh     // Energy cycled so far (kWh)
├─ BatteryHealthPct                   // Current health (100-80%)
└─ EnergyDeltaKwh                     // Energy this timestep (from SOC calculations)
```

### Calculation Process

**Step 1: Calculate absolute throughput**
```pseudocode
# Both charge and discharge count toward degradation
AbsoluteEnergyThroughputKwh = ABS(EnergyDeltaKwh)
```

**Step 2: Accumulate total throughput**
```pseudocode
NewCumulativeThroughputKwh = CurrentCumulativeThroughputKwh + AbsoluteEnergyThroughputKwh
```

**Step 3: Calculate battery health (linear model)**
```pseudocode
HealthLossPercent = (NewCumulativeThroughputKwh / RatedLifetimeThroughputKwh) × (100 - EndOfLifeBatteryHealthPct)
NewBatteryHealthPct = 100 - HealthLossPercent
```

**Step 4: Apply minimum threshold**
```pseudocode
NewBatteryHealthPct = MAX(EndOfLifeBatteryHealthPct, NewBatteryHealthPct)
```

**Step 5: Update state variables**
```pseudocode
CurrentCumulativeThroughputKwh = NewCumulativeThroughputKwh
BatteryHealthPct = NewBatteryHealthPct
```

### Example: TONLY DTE145 BatterySwap

**Configuration:**
- Battery capacity: 801 kWh
- Energy per cycle: ~167 kWh net (after regen)
- Rated lifetime throughput: 160,200 kWh
- Expected cycles: ~1,000 cycles
- End of life: 80% health

**Degradation timeline:**

| Cycles | Cumulative Throughput | Health Loss | Battery Health | Status                 |
| ------ | --------------------- | ----------- | -------------- | ---------------------- |
| 0      | 0 kWh                 | 0%          | 100%           | New battery            |
| 250    | 41,750 kWh            | 5.2%        | 94.8%          | Good                   |
| 500    | 83,500 kWh            | 10.4%       | 89.6%          | Good                   |
| 750    | 125,250 kWh           | 15.6%       | 84.4%          | Acceptable             |
| 1,000  | 167,000 kWh           | 20.8%       | **79.2%**      | **Replacement needed** |

**Economic impact:**
- Operating life: ~1,000 cycles
- Replacement cost: $500k-$800k (battery pack)
- Annual cycles: ~500 cycles (2 shifts/day)
- Battery lifespan: ~2 years
- Annual battery cost: $250k-$400k/year

### Implementation Notes

**Advantages:**
- ✅ Simple calculation (5 steps)
- ✅ Low computational cost
- ✅ Predictable degradation timeline
- ✅ Suitable for controlled charging scenarios

**Limitations:**
- ❌ Doesn't account for DoD variations
- ❌ Doesn't account for C-rate effects
- ❌ Overestimates degradation for shallow cycling
- ❌ Underestimates degradation for deep cycling

**Use case:** BatterySwap operations where all batteries experience similar cycling patterns (controlled station charging, consistent 100%→80% discharge).

---

## 2. Advanced Cycle-Life Degradation

### Principle

Battery degradation depends on **how** the battery is used, not just how much energy is cycled. Physics-based model accounts for:

1. **Depth of Discharge (DoD)** - Shallow cycles cause less damage
2. **Discharge Rate (C-rate)** - High discharge rates accelerate aging
3. **Charge Rate (C-rate)** - High charge rates accelerate aging  
4. **Temperature** - Higher temperatures accelerate aging

**Applies to:** BatteryElectric mode (Liebherr T 264 BE) with trolley assist

### Mathematical Foundation

**Cycle-life formula:**
```
N_c = N_c_ref × θ_DoD × θ_i_dis × θ_i_ch × θ_T

Where:
  N_c = Expected cycle life under actual conditions
  N_c_ref = Reference cycle life (9,175 cycles for LFP at reference conditions)
  θ_DoD = Depth of discharge factor
  θ_i_dis = Discharge rate factor
  θ_i_ch = Charge rate factor
  θ_T = Temperature factor
```

**Degradation factor calculation:**
```
θ_DoD = (DoD / DoD_ref)^(-ξ)
θ_i_dis = (i_dis / i_dis_ref)^(-γ₁)
θ_i_ch = (i_ch / i_ch_ref)^(-γ₂)
θ_T = exp(-ψ × (1/T_ref - 1/T_op))^α

Where:
  DoD_ref = 0.5 (50% reference)
  i_dis_ref = 0.5C (discharge rate reference)
  i_ch_ref = 0.5C (charge rate reference)
  T_ref = 298K (25°C)
  ξ = 0.8 (DoD exponent)
  γ₁ = 0.8 (discharge rate exponent)
  γ₂ = 2.34 (charge rate exponent)
  ψ = 3700 (temperature coefficient)
  α = 0.9708 (temperature base)
```

**Interpretation:** Higher θ values mean **longer battery life** (less degradation per cycle).

### Input Parameters

**Battery specifications:**
```
RatedBatteryStorageEnergyKwh         // Nominal capacity (e.g., 3200 kWh)
ReferenceLifeCycles                  // Cycles at reference conditions (9,175)
EndOfLifeBatteryHealthPct            // Replacement threshold (80%)
```

**Model parameters (LFP chemistry):**
```
ReferenceDOD = 0.5                   // 50% DoD reference
ReferenceDischargeCRate = 0.5        // 0.5C discharge
ReferenceChargeCRate = 0.5           // 0.5C charge
ReferenceTemperatureK = 298          // 25°C
Xi = 0.8                             // DoD exponent
Psi = 3700                           // Temperature coefficient
Gamma1 = 0.8                         // Discharge rate exponent
Gamma2 = 2.34                        // Charge rate exponent
Alpha = 0.9708                       // Temperature base
```

**Operating parameters:**
```
OperatingTemperatureK = 318          // 45°C typical operating temp
```

### Per-Cycle Tracking Variables

**Cycle boundaries:**
```
CycleInProgress                      // Boolean - truck is in active haul cycle
CurrentCycleStartSOC                 // SOC when cycle started (%)
```

**SOC extremes:**
```
CurrentCycleMinSOC                   // Minimum SOC reached this cycle (%)
CurrentCycleMaxSOC                   // Maximum SOC reached this cycle (%)
```

**Energy flow accumulation:**
```
CurrentCycleDischargeEnergySum       // Total discharge energy this cycle (kWh)
CurrentCycleDischargeTimeSum         // Total discharge time this cycle (hours)
CurrentCycleChargeEnergySum          // Total charge energy this cycle (kWh)
CurrentCycleChargeTimeSum            // Total charge time this cycle (hours)
```

**Accumulated degradation:**
```
EquivalentCyclesAccumulated          // Weighted cycle count
BatteryHealthPct                     // Current health (100-80%)
```

### Calculation Process

#### Step 1: Cycle Detection and Initialization

```pseudocode
# Detect cycle start (truck leaves dump, starts new haul)
if TruckState == "StartingNewCycle":
    CurrentCycleStartSOC = CurrentBatterySOCPct
    CurrentCycleMinSOC = CurrentBatterySOCPct
    CurrentCycleMaxSOC = CurrentBatterySOCPct
    CurrentCycleDischargeEnergySum = 0
    CurrentCycleDischargeTimeSum = 0
    CurrentCycleChargeEnergySum = 0
    CurrentCycleChargeTimeSum = 0
    CycleInProgress = True
```

#### Step 2: Accumulate Cycle Data (Every Timestep)

```pseudocode
if CycleInProgress:
    # Track SOC extremes
    CurrentCycleMinSOC = min(CurrentCycleMinSOC, NewBatterySOCPct)
    CurrentCycleMaxSOC = max(CurrentCycleMaxSOC, NewBatterySOCPct)
    
    # Accumulate discharge energy and time
    if NetBatteryPowerKw > 0:  # Discharging
        CurrentCycleDischargeEnergySum += abs(EnergyDeltaKwh)
        CurrentCycleDischargeTimeSum += TimeStepSeconds / 3600
    
    # Accumulate charge energy and time
    elif NetBatteryPowerKw < 0:  # Charging
        CurrentCycleChargeEnergySum += abs(EnergyDeltaKwh)
        CurrentCycleChargeTimeSum += TimeStepSeconds / 3600
```

#### Step 3: Cycle Completion - Calculate DoD

```pseudocode
# Detect cycle end (truck completes dump)
if TruckState == "CompletingCycle" and CycleInProgress:
    # Calculate depth of discharge (fraction 0-1)
    CycleDoD = (CurrentCycleMaxSOC - CurrentCycleMinSOC) / 100
```

#### Step 4: Calculate Average C-Rates

```pseudocode
# Average discharge C-rate
if CurrentCycleDischargeTimeSum > 0:
    AvgDischargeCRate = (CurrentCycleDischargeEnergySum / 
                         (RatedBatteryStorageEnergyKwh × CurrentCycleDischargeTimeSum))
else:
    AvgDischargeCRate = 0

# Average charge C-rate
if CurrentCycleChargeTimeSum > 0:
    AvgChargeCRate = (CurrentCycleChargeEnergySum / 
                      (RatedBatteryStorageEnergyKwh × CurrentCycleChargeTimeSum))
else:
    AvgChargeCRate = 0
```

#### Step 5: Calculate Degradation Factors (θ values)

```pseudocode
# Depth of discharge factor (higher θ = less degradation)
ThetaDoD = (CycleDoD / ReferenceDOD) ^ (-Xi)

# Discharge rate factor
if AvgDischargeCRate > 0:
    ThetaDischarge = (AvgDischargeCRate / ReferenceDischargeCRate) ^ (-Gamma1)
else:
    ThetaDischarge = 1.0

# Charge rate factor
if AvgChargeCRate > 0:
    ThetaCharge = (AvgChargeCRate / ReferenceChargeCRate) ^ (-Gamma2)
else:
    ThetaCharge = 1.0

# Temperature factor
ThetaTemperature = exp(-Psi × ((1 / ReferenceTemperatureK) - 
                                (1 / OperatingTemperatureK))) ^ Alpha
```

#### Step 6: Calculate Equivalent Cycle Fraction

```pseudocode
# Combined cycle impact factor
CycleImpactFactor = ThetaDoD × ThetaDischarge × ThetaCharge × ThetaTemperature

# Convert to equivalent cycle fraction (inverse relationship)
EquivalentCycleFraction = 1 / CycleImpactFactor
```

**Interpretation:**
- `CycleImpactFactor > 1` → This cycle is **easier** on battery than reference (e.g., 820 for shallow cycling)
- `EquivalentCycleFraction < 1` → This cycle counts as **less than 1 reference cycle** (e.g., 0.0012 cycles)
- `CycleImpactFactor < 1` → This cycle is **harder** on battery than reference (e.g., 0.1 for deep cycling)
- `EquivalentCycleFraction > 1` → This cycle counts as **more than 1 reference cycle** (e.g., 10 cycles)

#### Step 7: Accumulate Equivalent Cycles

```pseudocode
EquivalentCyclesAccumulated += EquivalentCycleFraction
```

#### Step 8: Calculate Battery Health

```pseudocode
# Fraction of reference life consumed
CycleFractionUsed = EquivalentCyclesAccumulated / ReferenceLifeCycles

# Health loss (linear with cycle fraction)
HealthLossPercent = CycleFractionUsed × (100 - EndOfLifeBatteryHealthPct)

# New battery health
NewBatteryHealthPct = 100 - HealthLossPercent

# Apply minimum threshold
NewBatteryHealthPct = max(EndOfLifeBatteryHealthPct, NewBatteryHealthPct)

# Update state
BatteryHealthPct = NewBatteryHealthPct
```

#### Step 9: Reset Cycle Tracking

```pseudocode
CycleInProgress = False
# Variables reset at next cycle start
```

### Example Scenarios

#### Scenario A: PreserveBattery Mode (Shallow Cycling)

**Operating profile:**
- SOC range: 95% → 90% (DoD = 5% = 0.05)
- Discharge energy: 64 kWh over 0.8 hours → 0.40C average
- Charge energy: 50 kWh over 0.6 hours → 0.43C average
- Temperature: 45°C (318K)

**Degradation calculation:**
```
# Step 1: DoD factor
θ_DoD = (0.05 / 0.5)^(-0.8) = 0.1^(-0.8) = 6.31

# Step 2: Discharge rate factor
θ_i_dis = (0.40 / 0.5)^(-0.8) = 0.8^(-0.8) = 1.17

# Step 3: Charge rate factor
θ_i_ch = (0.43 / 0.5)^(-2.34) = 0.86^(-2.34) = 1.38

# Step 4: Temperature factor
θ_T = exp(-3700 × (1/298 - 1/318))^0.9708 = 0.44

# Step 5: Combined cycle impact
CycleImpactFactor = 6.31 × 1.17 × 1.38 × 0.44 = 4.48

# Step 6: Equivalent cycle fraction
EquivalentCycleFraction = 1 / 4.48 = 0.223 equivalent cycles
```

**Result:** This cycle counts as **0.223 reference cycles** (less than 1/4 of standard cycle).

**Battery life estimate:**
```
Expected cycles = 9,175 / 0.223 = 41,143 cycles
Cycles per year = 500 (2 shifts/day)
Battery lifespan = 82 years (outlives truck!)
```

**Conclusion:** PreserveBattery mode with shallow cycling provides **exceptional battery life**.

#### Scenario B: SustainSpeed Mode (Moderate Cycling)

**Operating profile:**
- SOC range: 100% → 85% (DoD = 15% = 0.15)
- Discharge energy: 288 kWh over 0.8 hours → 0.75C average (high power)
- Charge energy: 150 kWh over 0.6 hours → 0.47C average
- Temperature: 45°C (318K)

**Degradation calculation:**
```
# Step 1: DoD factor
θ_DoD = (0.15 / 0.5)^(-0.8) = 0.3^(-0.8) = 2.41

# Step 2: Discharge rate factor
θ_i_dis = (0.75 / 0.5)^(-0.8) = 1.5^(-0.8) = 0.74

# Step 3: Charge rate factor
θ_i_ch = (0.47 / 0.5)^(-2.34) = 0.94^(-2.34) = 1.14

# Step 4: Temperature factor
θ_T = 0.44 (same as Scenario A)

# Step 5: Combined cycle impact
CycleImpactFactor = 2.41 × 0.74 × 1.14 × 0.44 = 0.895

# Step 6: Equivalent cycle fraction
EquivalentCycleFraction = 1 / 0.895 = 1.12 equivalent cycles
```

**Result:** This cycle counts as **1.12 reference cycles** (slightly harder than standard).

**Battery life estimate:**
```
Expected cycles = 9,175 / 1.12 = 8,192 cycles
Cycles per year = 500
Battery lifespan = 16.4 years (still excellent)
```

**Conclusion:** SustainSpeed mode with moderate cycling still provides **very good battery life**.

#### Scenario C: StandAlone Mode (Deep Cycling - NOT RECOMMENDED)

**Operating profile:**
- SOC range: 100% → 20% (DoD = 80% = 0.80)
- Discharge energy: 1,920 kWh over 4.0 hours → 0.60C average
- Charge energy: 1,800 kWh over 6.0 hours → 0.47C average
- Temperature: 45°C (318K)

**Degradation calculation:**
```
# Step 1: DoD factor
θ_DoD = (0.80 / 0.5)^(-0.8) = 1.6^(-0.8) = 0.68

# Step 2: Discharge rate factor
θ_i_dis = (0.60 / 0.5)^(-0.8) = 1.2^(-0.8) = 0.86

# Step 3: Charge rate factor
θ_i_ch = (0.47 / 0.5)^(-2.34) = 0.94^(-2.34) = 1.14

# Step 4: Temperature factor
θ_T = 0.44

# Step 5: Combined cycle impact
CycleImpactFactor = 0.68 × 0.86 × 1.14 × 0.44 = 0.293

# Step 6: Equivalent cycle fraction
EquivalentCycleFraction = 1 / 0.293 = 3.41 equivalent cycles
```

**Result:** This cycle counts as **3.41 reference cycles** (very harsh).

**Battery life estimate:**
```
Expected cycles = 9,175 / 3.41 = 2,690 cycles
Cycles per year = 500
Battery lifespan = 5.4 years
Replacement cost: $800k-$1.2M
Annual battery cost: $148k-$222k/year
```

**Conclusion:** StandAlone mode with deep cycling causes **severe degradation**. NOT RECOMMENDED for standard operations.

### Operating Mode Comparison

| Operating Mode      | DoD | Discharge C-rate | θ_DoD | θ_i_dis | Cycle Impact | Expected Life       | Battery Cost/Year       |
| ------------------- | --- | ---------------- | ----- | ------- | ------------ | ------------------- | ----------------------- |
| **PreserveBattery** | 5%  | 0.40C            | 6.31  | 1.17    | 4.48         | 41,000+ cycles      | **$0** (outlives truck) |
| **SustainSpeed**   | 15% | 0.75C            | 2.41  | 0.74    | 0.90         | 8,000-10,000 cycles | $80k-$150k              |
| **StandAlone**      | 80% | 0.60C            | 0.68  | 0.86    | 0.29         | 2,500-3,000 cycles  | $267k-$480k             |

**Key insights:**
1. **PreserveBattery is optimal** - Shallow cycling (5% DoD) results in battery outliving truck lifespan
2. **SustainSpeed is acceptable** - Moderate stress (15% DoD, high C-rate) provides 8,000+ cycles (16+ years)
3. **StandAlone is NOT RECOMMENDED** - Deep cycling (80% DoD) causes severe degradation (5-6 years)

---

## 3. Operating Implications

### Power Degradation Factor

Battery health directly affects available power through the `PowerDegradationFactor`:

```pseudocode
if prop_PowerDegradationActive:
    PowerDegradationFactor = BatteryHealthPct / 100  # 0.80 to 1.00
else:
    PowerDegradationFactor = 1.0  # Degradation disabled
```

**Impact on truck performance:**

| Battery Health | Power Factor | Max Battery Power | Speed Impact (loaded, 8% grade) |
| -------------- | ------------ | ----------------- | ------------------------------- |
| 100% (new)     | 1.00         | 3200 kW           | 24.2 km/h (baseline)            |
| 90%            | 0.90         | 2880 kW           | 22.5 km/h (-7%)                 |
| 80% (EOL)      | 0.80         | 2560 kW           | 20.8 km/h (-14%)                |

**Trolley assist compensation:**
- On trolley section: Trolley power compensates for battery degradation
- Off trolley section: Performance degrades with battery health
- **Recommendation:** Replace battery at 80% health to maintain acceptable performance

### Mode-Specific Degradation Strategies

**BatterySwap (TONLY DTE145):**
- Model: Simple throughput-based
- Strategy: Replace batteries at 1,000 cycles (~2 years)
- Cost: $250k-$400k/year for battery inventory
- Management: Centralized battery pool at swap station

**BatteryElectric + PreserveBattery (T 264 BE):**
- Model: Advanced cycle-life
- Strategy: Maximize trolley coverage, minimize battery use
- Expected life: 200,000+ cycles (truck lifetime)
- Cost: $0/year (battery outlives truck)
- **RECOMMENDED** - Optimal for long-term sustainability

**BatteryElectric + SustainSpeed (T 264 BE):**
- Model: Advanced cycle-life
- Strategy: Accept battery replacement for productivity
- Expected life: 30,000-50,000 cycles (3-5 years)
- Cost: $160k-$400k/year
- Use case: High ore value periods, production bottlenecks

**BatteryElectric + StandAlone (T 264 BE):**
- Model: Advanced cycle-life
- Strategy: Avoid if possible
- Expected life: 10,000-15,000 cycles (1-2 years)
- Cost: $400k-$1.2M/year
- **NOT RECOMMENDED** - Emergency/backup only

### Economic Decision Framework

**Question: When is SustainSpeed mode worth the battery cost?**

**Break-even analysis:**
```
Additional battery cost: $160k-$400k/year
Production increase: 7.4% more cycles (T 264 BE)
Break-even ore value: $160k / (154 additional cycles) = $1,039/cycle

If ore value > $1,039/cycle → SustainSpeed mode is profitable
If ore value < $1,039/cycle → PreserveBattery mode is better
```

**Typical ore values:**
- Copper: $3,000-$5,000/cycle (SustainSpeed profitable)
- Iron ore: $500-$800/cycle (PreserveBattery better)
- Gold: $10,000+/cycle (SustainSpeed highly profitable)

---

## 4. State Variables Summary

### Simple Throughput Model (BatterySwap)

**obj_BatteryElectricTruck state variables:**
```
var_CumulativeThroughputKwh          // Real - Total energy cycled (kWh)
var_BatteryHealthPct                 // Real - Current health (100-80%)
```

**Properties (tbl_TruckTypes):**
```
RatedLifetimeThroughputKwh           // Real - Lifetime energy capacity (e.g., 160,200 kWh)
EndOfLifeBatteryHealthPct            // Real - Replacement threshold (typically 80%)
BatteryDegradationModel              // String - "ThroughputBased"
```

### Advanced Cycle-Life Model (BatteryElectric)

**obj_Battery state variables:**
```
# Cycle tracking (reset each cycle)
var_CycleInProgress                    // Boolean - Active haul cycle flag
var_CurrentCycleStartSOCPct            // Real - SOC at cycle start (%)
var_CurrentCycleMinSOCPct              // Real - Minimum SOC this cycle (%)
var_CurrentCycleMaxSOCPct              // Real - Maximum SOC this cycle (%)
var_CurrentCycleDischargeEnergyKwh     // Real - Total discharge energy (kWh)
var_CurrentCycleDischargeTimeHrs       // Real - Total discharge time (hours)
var_CurrentCycleChargeEnergyKwh        // Real - Total charge energy (kWh)
var_CurrentCycleChargeTimeHrs          // Real - Total charge time (hours)

# Accumulated degradation
var_EquivalentCyclesAccumulated        // Real - Weighted cycle count
var_BatteryHealthPct                   // Real - Current health (100-80%)
```

**Properties (tbl_TruckTypes):**
```
RatedBatteryStorageEnergyKwh         // Real - Nominal capacity (e.g., 3200 kWh)
ReferenceLifeCycles                  // Real - Reference cycles (9,175)
EndOfLifeBatteryHealthPct            // Real - Replacement threshold (80%)
BatteryDegradationModel              // String - "CycleLifeBased"

# Model parameters (LFP chemistry)
DegradationReferenceDOD              // Real - 0.5 (50%)
DegradationReferenceDischargeCRate   // Real - 0.5 (0.5C)
DegradationReferenceChargeCRate      // Real - 0.5 (0.5C)
DegradationReferenceTemperatureK     // Real - 298 (25°C)
DegradationXi                        // Real - 0.8
DegradationPsi                       // Real - 3700
DegradationGamma1                    // Real - 0.8
DegradationGamma2                    // Real - 2.34
DegradationAlpha                     // Real - 0.9708
OperatingTemperatureK                // Real - 318 (45°C typical)
```

---

## 5. Implementation Notes

### Model Selection Configuration

**tbl_TruckTypes.BatteryDegradationModel values:**
- `"None"` - No degradation tracking (testing/debugging)
- `"ThroughputBased"` - Simple linear model (BatterySwap mode)
- `"CycleLifeBased"` - Advanced physics model (BatteryElectric mode)

### Computational Complexity

| Model          | Calculations per Timestep | Calculations per Cycle | Total Variables |
| -------------- | ------------------------- | ---------------------- | --------------- |
| **Throughput** | 5 operations              | 0                      | 2 state vars    |
| **Cycle-Life** | 4-6 operations            | 20-25 operations       | 10 state vars   |

**Recommendation:** Use throughput model for large fleets (100+ trucks) if computational performance is critical. Use cycle-life model for accuracy and realistic battery management.

### Cycle Detection Implementation

**Trigger points:**
```pseudocode
# Cycle start - truck picks up load
if TruckState == "LoadComplete":
    trigger_cycle_start()

# Cycle end - truck completes dump
if TruckState == "DumpComplete":
    trigger_cycle_end()
    calculate_degradation()  # Only for cycle-life model
```

### Temperature Modeling

Current implementation uses **constant operating temperature** (45°C). Future enhancements could include:
- Dynamic temperature based on ambient conditions
- Temperature variation with load/speed
- Cooling system modeling
- Seasonal temperature variations

**Impact of temperature:**
```
25°C (reference): θ_T = 1.00 (baseline)
35°C: θ_T = 0.65 (-35% cycle life)
45°C: θ_T = 0.44 (-56% cycle life)
55°C: θ_T = 0.30 (-70% cycle life)
```

**Mitigation:** Battery thermal management systems keep operating temperature near 45°C.

---

## Cross-References

**Related concept documents:**
- `01-fleet-and-modes.md` - Truck modes and operating configurations
- `03-power-flow.md` - Power degradation factor application
- `04-battery-management.md` - SOC calculations and energy flow tracking
- `05-fuel-systems.md` - Comparative economics (battery vs diesel)

**Source documents:**
- Complete_Physics_Implementation_Matrix.md Section 5 - Battery degradation models (throughput and cycle-life)
- MultiTruckConcept.md - Degradation calculations and operating scenario impacts

**Implementation reference:**
- `/workspace/simproj/Models.obj_Battery.md` - Battery object specification (when implemented)






