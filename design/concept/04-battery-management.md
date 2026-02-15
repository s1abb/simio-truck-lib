# Battery Management

**Applies to:** BatterySwap (TONLY), BatteryElectric (T 264 BE)  
**Purpose:** Track battery state of charge (SOC) and trigger swap/recharge events  
**Related:** [01-fleet-and-modes.md](01-fleet-and-modes.md), [03-power-flow.md](03-power-flow.md), [08-degradation-models.md](08-degradation-models.md)

---

## Overview

Battery management determines:
- Current state of charge (SOC) as a percentage
- Net battery power (discharge, charge, or regeneration)
- When to trigger swap/recharge operations
- Visual battery indicator (optional)

**Note:** Battery degradation modeling is covered separately in [08-degradation-models.md](08-degradation-models.md).

---

## Input Parameters

```
Battery Specifications:
├─ RatedBatteryStorageEnergyKwh    // Nominal battery capacity (kWh)
├─ SwapBatterySOCPct               // SOC threshold for battery swap (typically 80%)
├─ MaxBatteryPowerKw               // Maximum discharge power from tbl_TruckTypes (kW)
└─ MaxBatteryChargePowerKw         // Maximum charge power from tbl_TruckTypes (kW)

Current State:
├─ CurrentBatterySOCPct            // Current state of charge (%)
├─ BatteryHealthPct                // Current battery health (%)
└─ PowerDegradationFactor          // From speed dynamics

Power Flow:
├─ BatteryPowerKw                  // From power flow management (positive = discharge)
├─ TrolleyPowerDrawKw              // From power flow management
├─ TrolleyAvailablePowerKw         // From trolley power sharing
└─ MotorElectricalDemandKw         // Actual motor demand

Operating Mode:
├─ TruckMode                       // "BatterySwap" or "BatteryElectric"
└─ ElectricAssistMode              // "PreserveBattery", "SustainSpeed", etc.

Simulation Control:
└─ TimeStepSeconds                 // Simulation timestep (seconds)
```

---

## SOC Calculation (8-Step Process)

### STEP 1: Calculate Effective Battery Capacity

```pseudocode
EffectiveBatteryCapacityKwh = RatedBatteryStorageEnergyKwh × PowerDegradationFactor
```

**Note:** As battery ages, effective capacity decreases. At 80% health, effective capacity = 80% of rated.

### STEP 2: Determine Net Battery Power (Discharge or Charge)

```pseudocode
IF (TruckMode == "BatteryElectric" AND ElectricAssistMode == "PreserveBattery"):
    // Check if trolley has excess power available for charging
    IF (TrolleyPowerDrawKw < TrolleyAvailablePowerKw AND CurrentBatterySOCPct < 100):
        // Excess trolley power can charge battery
        ExcessTrolleyPowerKw = TrolleyAvailablePowerKw - TrolleyPowerDrawKw
        BatteryChargePowerKw = MIN(ExcessTrolleyPowerKw, MaxBatteryChargePowerKw)
        NetBatteryPowerKw = BatteryPowerKw - BatteryChargePowerKw  // Negative = charging
    ELSE:
        NetBatteryPowerKw = BatteryPowerKw  // Standard discharge
    END IF
ELSE:
    NetBatteryPowerKw = BatteryPowerKw  // Standard discharge (positive) or regen (negative)
END IF
```

**Sign Convention:**
- **Positive:** Battery discharging (providing power)
- **Negative:** Battery charging (receiving power)
- **Zero:** Battery idle

### STEP 3: Calculate Energy Delta

```pseudocode
EnergyDeltaKwh = NetBatteryPowerKw × (TimeStepSeconds / 3600)
```

**Note:** Converts power (kW) over timestep (seconds) to energy (kWh).

### STEP 4: Update SOC

```pseudocode
NewBatterySOCPct = CurrentBatterySOCPct - (100 × EnergyDeltaKwh / EffectiveBatteryCapacityKwh)
```

**Sign Logic:**
- Positive `EnergyDeltaKwh` (discharge) → SOC decreases
- Negative `EnergyDeltaKwh` (charge) → SOC increases

### STEP 5: Apply Limits [0-100%]

```pseudocode
NewBatterySOCPct = MAX(0, MIN(100, NewBatterySOCPct))
```

### STEP 6: Check Swap/Charge Trigger

```pseudocode
IF (TruckMode == "BatterySwap"):
    // Trigger battery swap at defined threshold (typically 80%)
    SwapRefuelChargeFlag = (NewBatterySOCPct < SwapBatterySOCPct)
ELSE IF (TruckMode == "BatteryElectric"):
    // Trigger emergency recharge at low SOC (typically 20%)
    SwapRefuelChargeFlag = (NewBatterySOCPct < 20)
END IF
```

**Note:** Flag triggers navigation to appropriate service station (see [06-infrastructure.md](06-infrastructure.md)).

### STEP 7: Update Battery SOC

```pseudocode
CurrentBatterySOCPct = NewBatterySOCPct
```

### STEP 8: Update Battery Visual Indicator (Optional)

```pseudocode
IF (NewBatterySOCPct >= 80):
    BatterySymbolIndex = 0      // Full (green)
ELSE IF (NewBatterySOCPct >= 60):
    BatterySymbolIndex = 1      // 3/4 (yellow-green)
ELSE IF (NewBatterySOCPct >= 40):
    BatterySymbolIndex = 2      // 1/2 (yellow)
ELSE IF (NewBatterySOCPct >= 20):
    BatterySymbolIndex = 3      // 1/4 (orange)
ELSE:
    BatterySymbolIndex = 4      // Low (red)
END IF
```

---

## SOC Management by Mode

| Mode                              | Typical SOC Range | Swap/Recharge Trigger | Charging Method              |
| --------------------------------- | ----------------- | --------------------- | ---------------------------- |
| BatterySwap (TONLY)               | 100% → 80%        | 80% SOC               | Station charging during swap |
| BatteryElectric + StandAlone      | 100% → 20%        | 20% SOC               | Plug-in charging station     |
| BatteryElectric + PreserveBattery | 95% → 90%         | 20% SOC (backup)      | Trolley dynamic charging     |
| BatteryElectric + SustainSpeed   | 100% → 70%        | 20% SOC (backup)      | Trolley dynamic charging     |

**Key Observations:**

- **BatterySwap:** Shallow cycling (20% DoD), swap before deep discharge
- **StandAlone:** Deep cycling (80% DoD), high battery stress
- **PreserveBattery:** Very shallow cycling (5% DoD), trolley provides majority of energy
- **SustainSpeed:** Moderate cycling (30% DoD), balanced performance/longevity

---

## PreserveBattery Mode: Trolley Charging Detail

**Unique Feature:** Can charge battery while driving using excess trolley power

### Scenario 1: Trolley Power > Driving Demand (Surplus)

```pseudocode
DrivingPowerDemand = MotorElectricalDemandKw
TrolleyAvailablePowerKw = <from power sharing>

IF (TrolleyAvailablePowerKw > DrivingPowerDemand):
    // Trolley covers driving + charges battery
    TrolleyDrivingPowerKw = DrivingPowerDemand
    ExcessPowerKw = TrolleyAvailablePowerKw - DrivingPowerDemand
    
    // Calculate how much power needed to reach 100% SOC
    PowerToReach100SOC = ((100 - CurrentBatterySOCPct) / 100) × EffectiveBatteryCapacityKwh × (3600 / TimeStepSeconds)
    
    // Charge at minimum of: excess power, max charge rate, or power to 100%
    TrolleyChargingPowerKw = MIN(ExcessPowerKw, MaxBatteryChargePowerKw, PowerToReach100SOC)
    
    // Battery receives negative power (charging)
    NetBatteryPowerKw = -TrolleyChargingPowerKw
    
    // Track energy contributions
    BatteryEnergyPreservedKwh += TrolleyDrivingPowerKw × TimeStepSeconds / 3600
    TrolleyChargingEnergyKwh += TrolleyChargingPowerKw × TimeStepSeconds / 3600
END IF
```

### Scenario 2: Trolley Power < Driving Demand (Deficit)

```pseudocode
IF (TrolleyAvailablePowerKw < DrivingPowerDemand):
    // Trolley helps, battery supplements
    TrolleyDrivingPowerKw = TrolleyAvailablePowerKw
    BatteryPowerKw = DrivingPowerDemand - TrolleyAvailablePowerKw
    NetBatteryPowerKw = BatteryPowerKw  // Positive (discharging)
    
    // Track preserved energy (what trolley provided)
    BatteryEnergyPreservedKwh += TrolleyDrivingPowerKw × TimeStepSeconds / 3600
END IF
```

### Scenario 3: Trolley Power = Driving Demand (Perfect Match)

```pseudocode
IF (TrolleyAvailablePowerKw == DrivingPowerDemand):
    // Trolley provides exact power needed
    TrolleyDrivingPowerKw = DrivingPowerDemand
    NetBatteryPowerKw = 0  // Battery neither charges nor discharges
    BatterySOCPct = CurrentBatterySOCPct  // Unchanged
    
    BatteryEnergyPreservedKwh += DrivingPowerDemand × TimeStepSeconds / 3600
END IF
```

---

## Example: BatterySwap Mode (TONLY DTE145)

```
Initial State:
├─ Battery capacity: 801 kWh
├─ Current SOC: 100%
├─ Battery health: 100%
├─ Swap threshold: 80%

Operating Cycle:
├─ Loaded climb: 150 kW discharge for 15 minutes → SOC: 96.9%
├─ Empty descent: 50 kW regen for 10 minutes → SOC: 97.9%
├─ Loaded climb: 150 kW discharge for 15 minutes → SOC: 94.8%
├─ Empty descent: 50 kW regen for 10 minutes → SOC: 95.8%
... (multiple cycles)

After 4 hours:
├─ Final SOC: 79.5% < 80% threshold
├─ SwapRefuelChargeFlag = True
└─ Navigate to battery swap station
```

---

## Example: BatteryElectric PreserveBattery Mode (T 264 BE)

```
Initial State:
├─ Battery capacity: 3,200 kWh
├─ Current SOC: 100%
├─ Battery health: 100%
├─ Trolley coverage: Both ramps (extended coverage)

Cycle 1 - On Trolley Sections:
├─ Driving demand: 2,000 kW
├─ Trolley available: 4,650 kW (1 truck on section)
├─ Trolley for driving: 2,000 kW
├─ Trolley for charging: 2,000 kW (limited by max charge rate)
├─ Net battery power: -2,000 kW (charging)
└─ SOC after 10 min: 100% (already full, can't charge more)

Cycle 1 - Off Trolley (queue/dump):
├─ Battery discharge: 100 kW for 10 minutes
├─ Energy consumed: 16.7 kWh
└─ SOC: 99.5%

End of Cycle 1:
├─ SOC range: 100% → 99.5% → 100%
├─ DoD: 0.5% (excellent - minimal stress)
└─ Expected battery life: 200,000+ cycles (truck lifetime)
```

---

## Related Documents

- [01-fleet-and-modes.md](01-fleet-and-modes.md) - Mode definitions and operating philosophy
- [03-power-flow.md](03-power-flow.md) - Power source calculations
- [06-infrastructure.md](06-infrastructure.md) - Swap/charge stations
- [07-trolley-power-sharing.md](07-trolley-power-sharing.md) - Dynamic trolley power
- [08-degradation-models.md](08-degradation-models.md) - Battery health tracking
