# Fuel Systems

**Applies to:** DieselElectric (T236, 793F AC, T264 diesel, 794 AC)  
**Purpose:** Track diesel fuel consumption and trigger refueling events  
**Related:** [01-fleet-and-modes.md](01-fleet-and-modes.md), [03-power-flow.md](03-power-flow.md), [06-infrastructure.md](06-infrastructure.md)

---

## Overview

Fuel systems management determines:
- Diesel fuel consumption based on generator power output
- Current fuel level in tank (liters and percentage)
- When to trigger refueling operations
- Cumulative fuel statistics (consumed, saved)

**Note:** Only applies to DieselElectric trucks. BatterySwap and BatteryElectric trucks have no fuel system.

---

## Input Parameters

```
Fuel System Specifications:
├─ DieselTankCapacityL                 // Fuel tank capacity (liters)
├─ DieselGeneratorMaxPowerKw           // Generator electrical output (kW)
├─ DieselGeneratorEfficiencyPct        // Generator efficiency (typically 40%)
├─ DieselFuelConsumptionRateLKwh       // Fuel consumption rate (L/kWh, typically 0.11)
└─ RefuelDieselLevelPct                // Refuel threshold (typically 10%)

Current State:
├─ CurrentDieselLevelL                 // Current fuel level (liters)
├─ CurrentDieselLevelPct               // Current fuel level (%)
└─ DieselPowerKw                       // From power flow management

Simulation Control:
└─ TimeStepSeconds                     // Simulation timestep (seconds)
```

---

## Fuel Consumption Calculations (5-Step Process)

### STEP 1: Calculate Fuel Consumed This Timestep

```pseudocode
IF (DieselPowerKw > 0):
    // Generator is running - convert electrical energy to fuel consumption
    EnergyGeneratedKwh = DieselPowerKw × (TimeStepSeconds / 3600)
    FuelConsumedL = EnergyGeneratedKwh × DieselFuelConsumptionRateLKwh
ELSE:
    // Generator idle/off
    FuelConsumedL = 0
END IF
```

**Note:** `DieselFuelConsumptionRateLKwh` accounts for generator efficiency. Typical value ~0.11 L/kWh means ~40% efficiency.

### STEP 2: Update Fuel Level

```pseudocode
NewDieselLevelL = CurrentDieselLevelL - FuelConsumedL
NewDieselLevelPct = (NewDieselLevelL / DieselTankCapacityL) × 100
```

### STEP 3: Apply Limits [0 to Tank Capacity]

```pseudocode
NewDieselLevelL = MAX(0, MIN(DieselTankCapacityL, NewDieselLevelL))
NewDieselLevelPct = MAX(0, MIN(100, NewDieselLevelPct))
```

### STEP 4: Check Refuel Trigger

```pseudocode
RefuelThresholdL = (RefuelDieselLevelPct / 100) × DieselTankCapacityL
SwapRefuelChargeFlag = (NewDieselLevelL < RefuelThresholdL)
```

**Note:** Flag triggers navigation to refuel station (see [06-infrastructure.md](06-infrastructure.md#diesel-refuel-stations)).

### STEP 5: Update State and Cumulative Statistics

```pseudocode
CurrentDieselLevelL = NewDieselLevelL
CurrentDieselLevelPct = NewDieselLevelPct

// Accumulate total fuel consumed
TotalDieselConsumedL = TotalDieselConsumedL + FuelConsumedL
TotalDieselEnergyKwh = TotalDieselEnergyKwh + EnergyGeneratedKwh
```

---

## Fuel Savings (PreserveEnergy Mode)

**Purpose:** Track diesel fuel saved when trolley replaces diesel generator

### Fuel Savings Calculation

```pseudocode
IF (ElectricAssistMode == "PreserveEnergy"):
    // Calculate what fuel WOULD have been consumed without trolley
    IF (TrolleyPowerDrawKw > 0):
        // Trolley is providing power - calculate fuel saved
        EnergyPreservedKwh = TrolleyPowerDrawKw × (TimeStepSeconds / 3600)
        FuelSavedL = EnergyPreservedKwh × DieselFuelConsumptionRateLKwh
        
        // Accumulate savings
        TotalDieselEnergyPreservedKwh = TotalDieselEnergyPreservedKwh + EnergyPreservedKwh
        TotalDieselFuelSavedL = TotalDieselFuelSavedL + FuelSavedL
    END IF
END IF
```

**Key Insight:** In PreserveEnergy mode on trolley, diesel generator typically idles (10% fuel consumption) while trolley provides driving power.

---

## Fuel Consumption by Mode

### DieselElectric + PreserveEnergy (Fuel Savings Priority)

**Objective:** Minimize diesel consumption by replacing with trolley power

| Truck       | Generator Power | Tank Capacity | Off Trolley Rate | On Trolley Rate | Savings |
| ----------- | --------------- | ------------- | ---------------- | --------------- | ------- |
| T236        | 895 kW          | 750 L         | 98.5 L/hr        | 3 L/hr          | 97%     |
| 793F AC     | 1,950 kW        | 1,514 L       | 214.5 L/hr       | 4 L/hr          | 98%     |
| T264 diesel | 2,013 kW        | 3,028 L       | 221.4 L/hr       | 4 L/hr          | 98%     |
| 794 AC      | 2,539 kW        | 3,028 L       | 279.3 L/hr       | 5 L/hr          | 98%     |

**Notes:**
- Off trolley: Diesel at full power for driving
- On trolley: Diesel idles (10% consumption) while trolley drives
- 95-98% fuel savings on trolley sections

### DieselElectric + SustainSpeed (Productivity Priority)

**Objective:** Maximize performance - diesel + trolley both at maximum

| Truck       | Generator Power | Off Trolley Rate | On Trolley Rate | Additional Consumption |
| ----------- | --------------- | ---------------- | --------------- | ---------------------- |
| T236        | 895 kW          | 98.5 L/hr        | 98.5 L/hr       | 0% (diesel always max) |
| 793F AC     | 1,950 kW        | 214.5 L/hr       | 214.5 L/hr      | 0% (diesel always max) |
| T264 diesel | 2,013 kW        | 221.4 L/hr       | 221.4 L/hr      | 0% (diesel always max) |
| 794 AC      | 2,539 kW        | 279.3 L/hr       | 279.3 L/hr      | 0% (diesel always max) |

**Notes:**
- Diesel generator always at maximum output
- Trolley adds to diesel power (not replacing)
- No fuel savings - focus is on productivity gain

---

## Example: CAT 794 AC PreserveEnergy Mode

```
Truck Specifications:
├─ Diesel generator: 2,539 kW
├─ Tank capacity: 3,028 L
├─ Fuel consumption rate: 0.11 L/kWh
├─ Refuel threshold: 10% (302.8 L)

12-Hour Shift Scenario:
├─ 20% of time on trolley (2.4 hours)
├─ 80% of time off trolley (9.6 hours)

Off Trolley Consumption:
├─ Average power: 2,539 kW (full power)
├─ Energy generated: 2,539 kW × 9.6 hr = 24,374 kWh
├─ Fuel consumed: 24,374 kWh × 0.11 L/kWh = 2,681 L
└─ Rate: 279.3 L/hr

On Trolley Consumption:
├─ Average power: 254 kW (10% for idling)
├─ Energy generated: 254 kW × 2.4 hr = 610 kWh
├─ Fuel consumed: 610 kWh × 0.11 L/kWh = 67 L
└─ Rate: 27.9 L/hr (90% savings vs off trolley)

Total Shift:
├─ Fuel consumed: 2,748 L
├─ Fuel saved by trolley: 537 L (would have been 3,285 L)
├─ Final tank level: 280 L (9.2% < 10% threshold)
└─ Refuel flag: TRUE

Economics (20% trolley coverage):
├─ Daily fuel saved: 537 L × $1.50/L = $806/day
├─ Annual fuel saved: $294,000/year per truck
└─ Fleet (10 trucks): $2.94M/year in fuel savings
```

---

## Example: Liebherr T236 SustainSpeed Mode

```
Truck Specifications:
├─ Diesel generator: 895 kW
├─ Tank capacity: 750 L
├─ Fuel consumption rate: 0.11 L/kWh
├─ Refuel threshold: 10% (75 L)

12-Hour Shift Scenario:
├─ 20% of time on trolley (2.4 hours)
├─ 80% of time off trolley (9.6 hours)

Off Trolley Consumption:
├─ Diesel power: 895 kW (full power)
├─ Energy: 895 kW × 9.6 hr = 8,592 kWh
├─ Fuel: 8,592 kWh × 0.11 L/kWh = 945 L
└─ Rate: 98.5 L/hr

On Trolley Consumption:
├─ Diesel power: 895 kW (STILL full power - combines with trolley)
├─ Energy: 895 kW × 2.4 hr = 2,148 kWh
├─ Fuel: 2,148 kWh × 0.11 L/kWh = 236 L
└─ Rate: 98.5 L/hr (NO SAVINGS)

Total Shift:
├─ Fuel consumed: 1,181 L (exceeds tank capacity!)
├─ Requires mid-shift refuel: Yes (after ~7.6 hours)
├─ Fuel saved by trolley: 0 L
└─ Benefit: Increased speed/productivity, not fuel savings

Performance vs Fuel Trade-off:
├─ Speed increase on trolley: 1.3x-1.5x
├─ Productivity gain: ~8-12% overall (20% coverage × 40-60% speed boost)
└─ Fuel cost: Same as diesel-only operation
```

**Key Insight:** SustainSpeed mode trades fuel economy for productivity. Use when ore value justifies increased fuel consumption.

---

## State Variables Summary

```
Persistent State:
├─ var_DieselLevelL              // Current fuel level (liters)
├─ var_DieselLevelPct            // Current fuel level (%)
├─ var_AssignRefuelStationNode   // Assigned refuel station reference

Cumulative Statistics:
├─ var_TotalDieselConsumedL      // Total fuel consumed (liters)
├─ var_TotalDieselEnergyKwh      // Total electrical energy generated (kWh)
├─ var_DieselEnergyPreservedKwh  // Energy saved by trolley (kWh)
└─ var_DieselFuelSavedL          // Fuel saved by trolley (liters)
```

---

## Related Documents

- [01-fleet-and-modes.md](01-fleet-and-modes.md) - DieselElectric mode definitions
- [03-power-flow.md](03-power-flow.md) - Diesel power calculations
- [06-infrastructure.md](06-infrastructure.md) - Refuel station operations
