# proc_PhysicsUpdates_DieselElectric_RefuelDiesel

This process handles the physics updates for trucks while refueling at a diesel station. The truck is stationary during refueling, so speed physics are bypassed and only fuel level updates are performed.

## Overview

The process is triggered by `tmr_TimeStep.Event` when:
- Truck is DieselElectric type at a refueling station
- Refueling is in progress
- The truck is stationary

> **Implementation Status:** The current XML implementation has an empty process (no steps). This document describes the intended design per `design/concept/05-fuel-systems.md`.

## Token Variables

Uses `tkn_TimeStepCalculations` shared token with 66 variables. Key variables for refueling:

**Properties (Read from tables):**
- `DieselTankCapacityL`, `RefuelRateLPerMin`

**Fuel State:**
- `FuelAddedL`, `NewDieselLevelL` (writes to `var_DieselLevelL`)

---

## Section 1: Read Current State (Refuel Updates Step)

### 1.1 Truck Properties

Lookup row index and read refueling properties:

```
tkn_TimeStepCalculations.RowIndex = tbl_TruckTypes.TruckType.RowForKey(String.FromList(list_TruckTypes, prop_TruckType))
tkn_TimeStepCalculations.DieselTankCapacityL = tbl_TruckTypes[tkn_TimeStepCalculations.RowIndex].DieselTankCapacityL
tkn_TimeStepCalculations.RefuelRateLPerMin = tbl_TruckTypes[tkn_TimeStepCalculations.RowIndex].RefuelRateLPerMin
```

### 1.2 Current Diesel State

```
// var_DieselLevelL read directly in calculations
```

---

## Section 2: Refueling Calculation

### 2.1 Fuel Added This Timestep

**Note:** `prop_TimeStepSeconds` is internally stored in hours in Simio, convert to minutes:

```
tkn_TimeStepCalculations.FuelAddedL = tkn_TimeStepCalculations.RefuelRateLPerMin * prop_TimeStepSeconds * 60
```

### 2.2 New Diesel Level

Clamp to tank capacity:

```
tkn_TimeStepCalculations.NewDieselLevelL = Math.Min(
    tkn_TimeStepCalculations.DieselTankCapacityL,
    var_DieselLevelL + tkn_TimeStepCalculations.FuelAddedL
)
```

---

## Section 3: State Updates

### 3.1 Refuel Complete Check

```
var_RefuelComplete = Math.If(
    tkn_TimeStepCalculations.NewDieselLevelL >= tkn_TimeStepCalculations.DieselTankCapacityL,
    True,
    False
)
```

### 3.2 Diesel State Write-Back

```
var_DieselLevelL = tkn_TimeStepCalculations.NewDieselLevelL
var_DieselLevelPct = 100 * tkn_TimeStepCalculations.NewDieselLevelL / tkn_TimeStepCalculations.DieselTankCapacityL
```

### 3.3 Clear Refuel Flag (When Complete)

```
var_SwapRefuelChargeFlag = Math.If(
    var_RefuelComplete,
    False,
    var_SwapRefuelChargeFlag
)
```

---

## Process Flow

1. **Always Execute**: No decision steps - refueling always runs when this process is triggered
2. **Exit Condition**: External process monitors `var_RefuelComplete` to release truck from station

This process is simpler than driving processes as the truck is stationary.

---

## Notes

- **Stationary Process**: No speed physics - truck is parked at refueling station
- **Refuel Rate**: Typical diesel refueling rates are 200-500 L/min for mining trucks
- **Tank Capacity**: CAT 794 AC: ~3,800 L, CAT 793F AC: ~4,730 L, Liebherr T264: ~5,680 L
- **Refuel Time**: Full tank from empty typically 10-20 minutes depending on truck size and pump rate
- **Unit Conversions (Simio internal)**:
  - `prop_TimeStepSeconds` is in hours, multiply by 60 to get minutes for RefuelRateLPerMin
  - Alternatively, use `RefuelRateLPerHr` property to avoid conversion
- **Completion Flag**: `var_RefuelComplete` signals external logic to release truck from station
- **Swap/Refuel Flag**: Cleared when refueling completes to prevent immediate re-triggering

## Example Calculation

For CAT 794 AC with 3,800 L tank, refueling at 300 L/min from 20% to 100%:

```
Fuel needed = 3,800 L × (100% - 20%) = 3,040 L
Refuel time = 3,040 L ÷ 300 L/min = 10.1 minutes

With 5-second timestep (5/3600 = 0.00139 hr):
FuelAddedL per step = 300 L/min × 0.00139 hr × 60 = 25 L
SOC increase per step = 25 L / 3,800 L × 100% = 0.66%

Steps to complete = 80% / 0.66% ≈ 121 steps = 10.1 minutes ✓
```
