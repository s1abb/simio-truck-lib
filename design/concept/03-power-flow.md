# Power Flow Management

**Purpose:** Calculate electrical power distribution between battery, diesel, trolley, and motor based on operating mode  
**Related:** [01-fleet-and-modes.md](01-fleet-and-modes.md), [02-physics-speed-force.md](02-physics-speed-force.md)

---

## Overview

Power flow management determines:
- How much power each source (battery/diesel/trolley) provides
- Motor thermal state and peak power availability
- Actual motor electrical power (may be limited by thermal state)

**Key Note:** For SustainSpeed modes, `TotalAvailablePowerKw` computed here feeds into the power-limited force calculation in [02-physics-speed-force.md](02-physics-speed-force.md).

---

## Input Parameters

```
Truck Specifications:
├─ MaxMotorPowerKw_Continuous      // Indefinite rating (kW)
├─ MaxMotorPowerKw_Peak            // Short-term overload rating (kW)
├─ MaxMotorPeakDurationSec         // Peak duration limit (typically 60 seconds)
├─ MaxBatteryPowerKw               // Battery discharge limit from tbl_TruckTypes (kW) [0 for diesel trucks]
├─ MaxBatteryChargePowerKw         // Battery charge limit from tbl_TruckTypes (kW) [0 for diesel trucks]
├─ DieselGeneratorMaxPowerKw       // Generator electrical output (kW) [0 for battery trucks]
├─ DieselGeneratorEfficiencyPct    // Generator efficiency (typically 40%)
├─ MotorEfficiencyPct              // Motor efficiency (typically 92%)
├─ RegenEfficiencyPct              // Regenerative efficiency (typically 75%)
└─ AuxiliaryPowerDemandKw          // Auxiliary systems power (typically 18-20 kW)

Path Specifications:
├─ TrolleyPowerCapacityKw          // Available trolley power on this path section (kW)
└─ OnElectricPath                  // Boolean: is truck on trolley path?

Motor Thermal State:
├─ MotorThermalStatePercent        // 0-100%, where 100 = thermal limit
├─ MotorPeakModeActive             // Boolean: is peak mode currently active?
└─ MotorPeakModeStartTime          // Timestamp when peak mode started

Operating State:
├─ TruckMode                       // "BatterySwap", "DieselElectric", "BatteryElectric"
├─ ElectricAssistMode              // "PreserveEnergy", "SustainSpeed", etc.
├─ CurrentSpeedKmh                 // Current speed
├─ TractiveForceN                  // From speed dynamics calculations
└─ PowerDegradationFactor          // From speed dynamics (battery health impact)
```

---

## Motor Thermal Management

**Purpose:** Track motor temperature and enforce peak power duration limits

### Step 1: Calculate Current Motor Power Demand

```pseudocode
SpeedMs = CurrentSpeedKmh / 3.6
MotorMechanicalPowerKw = (TractiveForceN × SpeedMs) / 1000

MotorElectricalDemandKw = IF (MotorMechanicalPowerKw > 0):
    // Motoring: account for efficiency losses + auxiliaries
    (MotorMechanicalPowerKw / (MotorEfficiencyPct / 100)) + AuxiliaryPowerDemandKw
ELSE IF (MotorMechanicalPowerKw < 0):
    // Regenerating: account for efficiency gains
    MotorMechanicalPowerKw × (RegenEfficiencyPct / 100)
ELSE:
    // Idle: just auxiliaries
    AuxiliaryPowerDemandKw
END IF

CurrentPowerRatio = ABS(MotorElectricalDemandKw) / MaxMotorPowerKw_Continuous
```

### Step 2: Calculate Thermal Accumulation/Dissipation

### Step 2: Calculate Thermal Accumulation/Dissipation
```pseudocode
IF (MotorPeakModeActive == TRUE):
    // Peak mode: motor heating up
    ThermalAccumulationRatePerSec = 100 / MaxMotorPeakDurationSec  // e.g., 1.67%/sec for 60s
    MotorThermalStatePercent = MotorThermalStatePercent + (ThermalAccumulationRatePerSec × TimeStepSeconds)
ELSE:
    // Normal operation: cooling or thermal equilibrium
    IF (CurrentPowerRatio > 1.0):
        // Should not occur, but if power exceeds continuous: heating
        CoolingRatePerSec = -0.3     // Heating (negative cooling = warming)
    ELSE IF (CurrentPowerRatio >= 0.95):
        // Near continuous: thermal equilibrium (heat generation ≈ dissipation)
        CoolingRatePerSec = 0.03     // Very slow recovery (~11 min to reach 80% from 100%)
    ELSE IF (CurrentPowerRatio >= 0.8):
        // High load: slow cooling
        CoolingRatePerSec = 0.15     // Slow cooling (~2.2 min to reach 80% from 100%)
    ELSE IF (CurrentPowerRatio >= 0.5):
        // Medium load: moderate cooling
        CoolingRatePerSec = 0.4      // Moderate cooling (~50 sec to reach 80% from 100%)
    ELSE IF (CurrentPowerRatio >= 0):
        // Light load: fast cooling
        CoolingRatePerSec = 0.8      // Fast cooling (~25 sec to reach 80% from 100%)
    ELSE:
        // Regenerating: very fast cooling (motor acting as generator + active cooling)
        CoolingRatePerSec = 1.2      // Very fast cooling (~17 sec to reach 80% from 100%)
    END IF
    
    MotorThermalStatePercent = MotorThermalStatePercent - (CoolingRatePerSec × TimeStepSeconds)
END IF

// Enforce limits [0-100%]
MotorThermalStatePercent = MAX(0, MIN(100, MotorThermalStatePercent))
```

### Step 3: Determine Motor Power Limit Based on Thermal State

```pseudocode
CanUsePeakMode = (MotorThermalStatePercent < 80)      // Need <80% thermal state to enter peak
MustStopPeakMode = (MotorThermalStatePercent >= 100)  // Must stop at 100%

IF (MotorElectricalDemandKw > MaxMotorPowerKw_Continuous):
    // Demand exceeds continuous rating - need peak mode
    IF (CanUsePeakMode == TRUE AND MustStopPeakMode == FALSE):
        // Activate or maintain peak mode
        IF (MotorPeakModeActive == FALSE):
            MotorPeakModeStartTime = CurrentTime
            MotorPeakModeActive = TRUE
        END IF
        MotorPowerLimitKw = MaxMotorPowerKw_Peak × PowerDegradationFactor
    ELSE:
        // Cannot use peak - too hot or timeout
        MotorPeakModeActive = FALSE
        MotorPowerLimitKw = MaxMotorPowerKw_Continuous × PowerDegradationFactor
    END IF
ELSE:
    // Within continuous rating - motor can cool
    MotorPeakModeActive = FALSE
    MotorPowerLimitKw = MaxMotorPowerKw_Continuous × PowerDegradationFactor
END IF
```

**Thermal State Interpretation:**
- **0-50%:** Motor cool, peak mode available with full duration
- **50-80%:** Motor warm, peak mode available with reduced duration
- **80-100%:** Motor hot, peak mode not available
- **100%:** Thermal limit - forced reduction to continuous rating

---

## Power Source Availability

**Purpose:** Determine available power from each source before mode-specific combining

```pseudocode
// ============================================================================
// Determine trolley power availability
// ============================================================================

IF (OnElectricPath == TRUE):
    TrolleyAvailablePowerKw = TrolleyPowerCapacityKw
ELSE:
    TrolleyAvailablePowerKw = 0
END IF

// ============================================================================
// Determine primary power source based on truck mode
// ============================================================================

IF (TruckMode == "BatterySwap" OR TruckMode == "BatteryElectric"):
    PrimarySourcePowerKw = MaxBatteryPowerKw × PowerDegradationFactor
ELSE IF (TruckMode == "DieselElectric"):
    PrimarySourcePowerKw = DieselGeneratorMaxPowerKw
ELSE:
    PrimarySourcePowerKw = 0
END IF
```

**Note:** `PowerDegradationFactor` only affects battery trucks (see [02-physics-speed-force.md](02-physics-speed-force.md#step-1-determine-power-degradation-factor)).

---

## Mode-Specific Power Combining

**Architecture Overview:**
- **BatterySwap:** Battery-only (trolley paths treated as normal paths)
- **DieselElectric + PreserveEnergy:** Trolley replaces diesel (fuel savings)
- **DieselElectric + SustainSpeed:** Diesel + trolley combine (productivity boost)
- **BatteryElectric + StandAlone:** Battery-only (no trolley interaction)
- **BatteryElectric + PreserveBattery:** Trolley priority (minimize battery stress)
- **BatteryElectric + SustainSpeed:** Battery + trolley combine (max performance)

### MODE: BatterySwap

**Trucks:** TONLY DTE145

```pseudocode
// Battery only, trolley paths ignored
AvailableElectricalPowerKw = PrimarySourcePowerKw
BatteryPowerKw = MIN(MotorElectricalDemandKw, AvailableElectricalPowerKw)
DieselPowerKw = 0
TrolleyPowerDrawKw = 0
```

### MODE: DieselElectric + PreserveEnergy

**Trucks:** Liebherr T236, CAT 793F AC, Liebherr T264 diesel, CAT 794 AC

**Objective:** Trolley REPLACES diesel (fuel savings priority)  
**Performance:** Speed maintained at 1.0x, fuel consumption reduced 95-98%

```pseudocode
IF (TrolleyAvailablePowerKw >= MotorElectricalDemandKw):
    // On trolley with sufficient power - diesel idles
    TrolleyPowerDrawKw = MotorElectricalDemandKw
    DieselPowerKw = AuxiliaryPowerDemandKw × 0.1  // Diesel idles (10% fuel consumption)
    AvailableElectricalPowerKw = TrolleyAvailablePowerKw
ELSE IF (TrolleyAvailablePowerKw > 0):
    // On trolley but insufficient power - diesel supplements
    TrolleyPowerDrawKw = TrolleyAvailablePowerKw
    DieselPowerKw = MIN(MotorElectricalDemandKw - TrolleyPowerDrawKw, PrimarySourcePowerKw)
    AvailableElectricalPowerKw = TrolleyPowerDrawKw + DieselPowerKw
ELSE:
    // Off trolley - diesel provides all power
    TrolleyPowerDrawKw = 0
    DieselPowerKw = MIN(MotorElectricalDemandKw, PrimarySourcePowerKw)
    AvailableElectricalPowerKw = DieselPowerKw
END IF
BatteryPowerKw = 0  // No battery in diesel-electric
```

**Key Behavior:** Speed/force unchanged from diesel-only operation. Only energy source accounting changes.

### MODE: DieselElectric + SustainSpeed

**Trucks:** Liebherr T236, CAT 793F AC, Liebherr T264 diesel, CAT 794 AC

**Objective:** Trolley + Diesel COMBINE (productivity boost)  
**Performance:** Speed increase 1.3x-1.78x, fuel consumption MAXIMUM (diesel at 100%)

```pseudocode
IF (TrolleyAvailablePowerKw > 0):
    // On trolley: diesel at maximum + trolley supplements
    DieselPowerKw = PrimarySourcePowerKw  // Diesel at full power
    TrolleyPowerDrawKw = MIN(MotorElectricalDemandKw - DieselPowerKw, TrolleyAvailablePowerKw)
    AvailableElectricalPowerKw = DieselPowerKw + TrolleyPowerDrawKw
    // This combined power enables higher tractive force via P=F×V
ELSE:
    // Off trolley: diesel only
    DieselPowerKw = MIN(MotorElectricalDemandKw, PrimarySourcePowerKw)
    TrolleyPowerDrawKw = 0
    AvailableElectricalPowerKw = DieselPowerKw
END IF
BatteryPowerKw = 0  // No battery in diesel-electric
```

**Note:** `AvailableElectricalPowerKw` feeds into power-limited force calculation (see [02-physics-speed-force.md](02-physics-speed-force.md#step-4b-apply-power-limited-scaling-sustainspeed-modes-only)).

### MODE: BatteryElectric + StandAlone

**Trucks:** Liebherr T 264 BE

**Objective:** Battery only - no trolley interaction

```pseudocode
// Use case: Routes without trolley infrastructure
AvailableElectricalPowerKw = PrimarySourcePowerKw
BatteryPowerKw = MIN(MotorElectricalDemandKw, AvailableElectricalPowerKw)
TrolleyPowerDrawKw = 0
DieselPowerKw = 0
```

**Note:** NOT RECOMMENDED for standard operations (high battery stress, 1-2 year battery life).

### MODE: BatteryElectric + PreserveBattery

**Trucks:** Liebherr T 264 BE

**Objective:** Trolley PRIORITY - minimize battery stress  
**Battery Life:** 200,000+ cycles (truck lifetime), DoD per cycle 2-5%

```pseudocode
IF (TrolleyAvailablePowerKw >= MotorElectricalDemandKw):
    // Trolley provides all power - battery not used
    TrolleyPowerDrawKw = MotorElectricalDemandKw
    BatteryPowerKw = 0  // Battery not used (or charging if excess power - see below)
    AvailableElectricalPowerKw = TrolleyAvailablePowerKw
ELSE IF (TrolleyAvailablePowerKw > 0):
    // Trolley + Battery supplement (battery bridges gap)
    TrolleyPowerDrawKw = TrolleyAvailablePowerKw
    BatteryPowerKw = MIN(MotorElectricalDemandKw - TrolleyPowerDrawKw, PrimarySourcePowerKw)
    AvailableElectricalPowerKw = TrolleyPowerDrawKw + BatteryPowerKw
ELSE:
    // Off trolley - battery provides all power
    TrolleyPowerDrawKw = 0
    BatteryPowerKw = MIN(MotorElectricalDemandKw, PrimarySourcePowerKw)
    AvailableElectricalPowerKw = BatteryPowerKw
END IF
DieselPowerKw = 0
```

**Special Case - Trolley Charging:**
```pseudocode
// If trolley has excess power, charge the battery
IF (TrolleyAvailablePowerKw > MotorElectricalDemandKw AND CurrentBatterySOCPct < 100):
    ExcessTrolleyPowerKw = TrolleyAvailablePowerKw - MotorElectricalDemandKw
    BatteryChargePowerKw = MIN(ExcessTrolleyPowerKw, MaxBatteryChargePowerKw)
    NetBatteryPowerKw = BatteryPowerKw - BatteryChargePowerKw  // Negative = charging
    // Detailed in battery-management.md
END IF
```

**Key Behavior:** Think of as "continuously connected electric truck with battery bridging" (not "battery truck that recharges").

### MODE: BatteryElectric + SustainSpeed

**Trucks:** Liebherr T 264 BE

**Objective:** Battery + Trolley COMBINE (max performance)  
**Battery Life:** 30,000-50,000 cycles (3-5 years), DoD per cycle 10-15%

```pseudocode
IF (TrolleyAvailablePowerKw > 0):
    TrolleyPowerDrawKw = TrolleyAvailablePowerKw
    BatteryPowerKw = MIN(MotorElectricalDemandKw - TrolleyPowerDrawKw, PrimarySourcePowerKw)
    AvailableElectricalPowerKw = TrolleyPowerDrawKw + BatteryPowerKw
    // This combined power enables higher tractive force via P=F×V
ELSE:
    TrolleyPowerDrawKw = 0
    BatteryPowerKw = MIN(MotorElectricalDemandKw, PrimarySourcePowerKw)
    AvailableElectricalPowerKw = BatteryPowerKw
END IF
DieselPowerKw = 0
```

**Note:** `AvailableElectricalPowerKw` feeds into power-limited force calculation. Battery degradation factor already applied to `PrimarySourcePowerKw`.

---

## Motor Power Limiting

**Purpose:** Ensure actual motor power respects thermal limits

```pseudocode
// Apply motor power limit
ActualMotorElectricalPowerKw = IF (MotorElectricalDemandKw > 0):
    MIN(MotorElectricalDemandKw, MotorPowerLimitKw)
ELSE:
    MAX(MotorElectricalDemandKw, -MotorPowerLimitKw)
END IF

// Adjust power draws if motor is limiting factor
IF (ABS(ActualMotorElectricalPowerKw) < ABS(MotorElectricalDemandKw)):
    // Motor is limiting - scale back power draws proportionally
    ScaleFactor = ActualMotorElectricalPowerKw / MotorElectricalDemandKw
    BatteryPowerKw = BatteryPowerKw × ScaleFactor
    DieselPowerKw = DieselPowerKw × ScaleFactor
    TrolleyPowerDrawKw = TrolleyPowerDrawKw × ScaleFactor
END IF
```

---

## Output Variables

```
BatteryPowerKw                    // Battery discharge (positive) or charge (negative)
DieselPowerKw                     // Diesel generator electrical output
TrolleyPowerDrawKw                // Trolley system power draw
ActualMotorElectricalPowerKw      // Actual motor electrical power (may be limited)
AvailableElectricalPowerKw        // Total available power (for SustainSpeed modes)
MotorThermalStatePercent          // Updated thermal state (0-100%)
MotorPeakModeActive               // Updated peak mode status
```

---

## Related Documents

- [01-fleet-and-modes.md](01-fleet-and-modes.md) - Operating mode definitions
- [02-physics-speed-force.md](02-physics-speed-force.md) - Uses TotalAvailablePowerKw for SustainSpeed modes
- [04-battery-management.md](04-battery-management.md) - Battery SOC calculations
- [05-fuel-systems.md](05-fuel-systems.md) - Diesel consumption
