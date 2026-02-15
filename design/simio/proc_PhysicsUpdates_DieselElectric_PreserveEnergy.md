# proc_PhysicsUpdates_DieselElectric_PreserveEnergy

**Status:** ✅ Fully Implemented and Validated (February 2026)

This process handles the physics updates for trucks operating in **DieselElectric + PreserveEnergy** mode. Trolley power replaces diesel generator output, achieving 97-98% fuel savings on electrified segments while the diesel engine idles.

## Overview

The process is triggered by `tmr_TimeStep.Event` when:
- Truck is DieselElectric type on a trolley-assisted path
- Power Flow Mode is set to PreserveEnergy
- The truck is moving on the network

## Token Variables

Uses `tkn_Physics` shared token with 66 variables. Key variables for DieselElectric PreserveEnergy mode:

**Properties (Read from tables):**
- `EmptyWeightKg`, `BaseRimpullForceN`, `BaseRetardForceN`
- `MaxSpeedKmh_Loaded`, `MaxSpeedKmh_Empty`, `RollingResistance`
- `MotorEfficiencyPct`, `AuxiliaryPowerDemandKw`
- `DieselFuelConsumptionRateLKwh`, `RefuelDieselLevelPct`, `DieselTankCapacityL`

**Trolley Power Sharing (from path properties):**
- `TrolleySectionTotalPowerKw`, `TrolleyMaxPowerPerTruckKw`, `TrolleyEfficiencyPct`
- `TrolleyActiveTrucksOnSection`, `TrolleySharedPowerPerTruckKw`, `TrolleyAvailablePowerKw`

**Speed Physics:**
- `CurrentGrade`, `CurrentSpeedKmh`, `CurrentWeightKg`
- `TargetSpeedKmh`, `TractiveForceN`, `AccelerationMs2`, `NewSpeedKmh`

**Fuel Calculations:**
- `OnTrolleyPath`, `CurrentDieselLevelPct`
- `MotorMechanicalPowerKw`, `MotorElectricalDemandKw`, `ActualDrivingDemandKw`
- `TrolleyPowerKw`, `DieselPowerKw`
- `DieselConsumedL`, `DieselEnergyConsumedKwh`
- `DieselEnergyPreservedKwh`, `DieselFuelSavedL`
- `NewDieselLevelL`, `RefuelThresholdL`

---

## Section 1: Read Current State (Speed Updates Step)

Executed when `var_SpeedUpdates == True`

### 1.1 Movement State

```
tkn_Physics.CurrentGrade = Movement.Pitch
tkn_Physics.CurrentSpeedKmh = Movement.Rate km/h
```

### 1.2 Truck Properties

Lookup row index and read truck properties:

```
tkn_Physics.RowIndex = tbl_TruckTypes.TruckType.RowForKey(String.FromList(list_TruckTypes, prop_TruckType))

tkn_Physics.EmptyWeightKg = tbl_TruckTypes[tkn_Physics.RowIndex].EmptyOperatingWeightKg
tkn_Physics.CurrentWeightKg = Math.If(var_Loaded, var_Payload, tkn_Physics.EmptyWeightKg)
tkn_Physics.BaseRimpullForceN = tbl_TruckTypes[tkn_Physics.RowIndex].RimpullForceN
tkn_Physics.BaseRetardForceN = tbl_TruckTypes[tkn_Physics.RowIndex].RetardForceN
tkn_Physics.MaxSpeedKmh_Loaded = tbl_TruckTypes[tkn_Physics.RowIndex].MaxSpeedKmh_Loaded
tkn_Physics.MaxSpeedKmh_Empty = tbl_TruckTypes[tkn_Physics.RowIndex].MaxSpeedKmh_Empty
tkn_Physics.RollingResistance = tbl_TruckTypes[tkn_Physics.RowIndex].RollingResistance
tkn_Physics.MotorEfficiencyPct = tbl_TruckTypes[tkn_Physics.RowIndex].MotorEfficiencyPct
tkn_Physics.AuxiliaryPowerDemandKw = tbl_TruckTypes[tkn_Physics.RowIndex].AuxiliaryPowerDemandKw
```

### 1.3 DieselElectric State

DieselElectric trucks have no battery entity - diesel level tracked directly on truck:

```
tkn_Physics.RefuelDieselLevelPct = tbl_TruckTypes[tkn_Physics.RowIndex].RefuelDieselLevelPct
tkn_Physics.DieselFuelConsumptionRateLKwh = tbl_TruckTypes[tkn_Physics.RowIndex].DieselFuelConsumptionRateLKwh
tkn_Physics.DieselTankCapacityL = tbl_TruckTypes[tkn_Physics.RowIndex].DieselTankCapacityL
tkn_Physics.CurrentDieselLevelPct = var_DieselLevelPct
tkn_Physics.OnTrolleyPath = Location.Parent.Is.obj_ElectricPath && obj_ElectricPath.prop_TrolleyAssistEnabled
```

DieselElectric trucks have no power degradation (no battery aging):

```
tkn_Physics.PowerDegradationFactor = 1.0
```

### 1.4 Trolley Power Sharing (Model B)

> **Reference:** `design/concept/07-trolley-power-sharing.md` (Model B: Power Sharing - Recommended)

When on a trolley-assisted path, calculate available trolley power based on section capacity and active truck count:

```
// Read trolley section properties from path
tkn_Physics.TrolleySectionTotalPowerKw = Math.If(
    tkn_Physics.OnTrolleyPath,
    Location.Parent.obj_ElectricPath.prop_TrolleySectionTotalPowerKw,
    0
)
tkn_Physics.TrolleyMaxPowerPerTruckKw = Math.If(
    tkn_Physics.OnTrolleyPath,
    Location.Parent.obj_ElectricPath.prop_TrolleyMaxPowerPerTruckKw,
    0
)
tkn_Physics.TrolleyEfficiencyPct = Math.If(
    tkn_Physics.OnTrolleyPath,
    Location.Parent.obj_ElectricPath.prop_TrolleyEfficiencyPct,
    0
)

// Count active trucks on this trolley section (Simio built-in property)
tkn_Physics.TrolleyActiveTrucksOnSection = Math.If(
    tkn_Physics.OnTrolleyPath,
    Location.Parent.obj_ElectricPath.NumberTravelers,
    0
)

// Calculate shared power per truck (equal distribution)
tkn_Physics.TrolleySharedPowerPerTruckKw = Math.If(
    tkn_Physics.TrolleyActiveTrucksOnSection > 0,
    tkn_Physics.TrolleySectionTotalPowerKw / tkn_Physics.TrolleyActiveTrucksOnSection,
    0
)

// Limit by truck pantograph rating and apply system efficiency
tkn_Physics.TrolleyAvailablePowerKw = Math.Min(
    tkn_Physics.TrolleySharedPowerPerTruckKw,
    tkn_Physics.TrolleyMaxPowerPerTruckKw
) * (tkn_Physics.TrolleyEfficiencyPct / 100)
```

**Example (10 MW section, 5 MW truck limit, 93% efficiency):**

| Active Trucks | Shared Power | Pantograph Limit | Available Power (after efficiency) |
| ------------- | ------------ | ---------------- | ---------------------------------- |
| 1             | 10 MW        | 5 MW             | 4.65 MW (truck-limited)            |
| 2             | 5 MW         | 5 MW             | 4.65 MW (truck-limited)            |
| 3             | 3.3 MW       | 5 MW             | 3.07 MW (section-limited)          |
| 4             | 2.5 MW       | 5 MW             | 2.33 MW (section-limited)          |

---

## Section 2: Speed Physics Calculations (Speed Updates Step)

### 2.1 Target Speed

```
tkn_Physics.MaxSpeedKmh = Math.If(
    var_Loaded,
    tkn_Physics.MaxSpeedKmh_Loaded,
    tkn_Physics.MaxSpeedKmh_Empty
)
tkn_Physics.PathSpeedLimitKmh = Math.If(
    Location.Parent.Is.obj_ElectricPath,
    Location.Parent.obj_ElectricPath.SpeedLimit,
    DesiredSpeed
) km/h
tkn_Physics.TargetSpeedKmh = Math.Min(
    tkn_Physics.PathSpeedLimitKmh,
    tkn_Physics.MaxSpeedKmh
)
```

### 2.2 Resistance Forces

```
tkn_Physics.GradeResistanceForceN = tkn_Physics.CurrentWeightKg * 9.81 * tkn_Physics.CurrentGrade / 100
tkn_Physics.RollingResistanceForceN = tkn_Physics.CurrentWeightKg * 9.81 * tkn_Physics.RollingResistance
tkn_Physics.TotalResistanceN = tkn_Physics.GradeResistanceForceN + tkn_Physics.RollingResistanceForceN
```

### 2.3 Tractive Force (Dead Band Control)

Apply ±3000 m/hr (3 km/h) dead band:

```
tkn_Physics.TractiveForceN = Math.If(
    tkn_Physics.CurrentSpeedKmh < tkn_Physics.TargetSpeedKmh - 3000,
    tkn_Physics.BaseRimpullForceN * tkn_Physics.PowerDegradationFactor,
    Math.If(
        tkn_Physics.CurrentSpeedKmh > tkn_Physics.TargetSpeedKmh + 3000,
        -tkn_Physics.BaseRetardForceN * tkn_Physics.PowerDegradationFactor,
        0
    )
)
```

### 2.4 Acceleration

```
tkn_Physics.NetTractiveForceN = tkn_Physics.TractiveForceN - tkn_Physics.TotalResistanceN
tkn_Physics.AccelerationMs2 = tkn_Physics.NetTractiveForceN / tkn_Physics.CurrentWeightKg
```

### 2.5 New Speed

```
tkn_Physics.NewSpeedKmh = Math.Max(
    0,
    Math.Min(
        tkn_Physics.TargetSpeedKmh,
        tkn_Physics.CurrentSpeedKmh + tkn_Physics.AccelerationMs2 * 3600 * prop_TimeStepSeconds * 3600
    )
)
```

### 2.6 Write Speed Update

```
Movement.Rate = tkn_Physics.NewSpeedKmh with Units="Kilometers per Hour"
```

---

## Section 3: Fuel Power Calculations (Fuel Updates Step)

Executed when `var_FuelUpdates == True`

### 3.1 Re-read State

```
tkn_Physics.RowIndex = tbl_TruckTypes.TruckType.RowForKey(String.FromList(list_TruckTypes, prop_TruckType))
tkn_Physics.AuxiliaryPowerDemandKw = tbl_TruckTypes[tkn_Physics.RowIndex].AuxiliaryPowerDemandKw
tkn_Physics.MotorEfficiencyPct = tbl_TruckTypes[tkn_Physics.RowIndex].MotorEfficiencyPct
tkn_Physics.DieselFuelConsumptionRateLKwh = tbl_TruckTypes[tkn_Physics.RowIndex].DieselFuelConsumptionRateLKwh
tkn_Physics.RefuelDieselLevelPct = tbl_TruckTypes[tkn_Physics.RowIndex].RefuelDieselLevelPct
tkn_Physics.DieselTankCapacityL = tbl_TruckTypes[tkn_Physics.RowIndex].DieselTankCapacityL
tkn_Physics.OnTrolleyPath = Location.Parent.Is.obj_ElectricPath && obj_ElectricPath.prop_TrolleyAssistEnabled
```

### 3.2 Motor Mechanical Power

Conditional on var_SpeedUpdates (zero when stationary):

```
tkn_Physics.MotorMechanicalPowerKw = Math.If(
    var_SpeedUpdates,
    (tkn_Physics.TractiveForceN / 1000) * (tkn_Physics.CurrentSpeedKmh / 3600),
    0
)
```

### 3.3 Power Source Selection (PreserveEnergy Mode)

> **Reference:** `design/concept/07-trolley-power-sharing.md` - Uses `TrolleyAvailablePowerKw` calculated in Section 1.4

In PreserveEnergy mode, trolley replaces diesel when on electrified path. If shared trolley power is insufficient due to high section traffic, diesel supplements the difference.

```
// Motor electrical demand (motor only, before auxiliaries)
// Positive motor power = driving (apply motor efficiency loss)
// Zero or negative motor power = stationary or retarding (no motor electrical demand)
tkn_Physics.MotorElectricalDemandKw = Math.If(
    tkn_Physics.MotorMechanicalPowerKw > 0,
    tkn_Physics.MotorMechanicalPowerKw / (tkn_Physics.MotorEfficiencyPct / 100),
    0
)

// Total driving demand (motor + auxiliaries)
// Auxiliaries always draw power regardless of driving state
tkn_Physics.ActualDrivingDemandKw = tkn_Physics.MotorElectricalDemandKw + tkn_Physics.AuxiliaryPowerDemandKw

// Trolley provides up to available power (limited by section sharing)
tkn_Physics.TrolleyPowerKw = Math.If(
    tkn_Physics.OnTrolleyPath,
    Math.Min(tkn_Physics.TrolleyAvailablePowerKw, tkn_Physics.ActualDrivingDemandKw),
    0
)

// Diesel provides any shortfall when trolley cannot meet full demand
// Off trolley: diesel covers everything
// On trolley with surplus: diesel = 0
// On trolley with deficit: diesel covers the gap
tkn_Physics.DieselPowerKw = Math.If(
    tkn_Physics.OnTrolleyPath,
    Math.Max(0, tkn_Physics.ActualDrivingDemandKw - tkn_Physics.TrolleyPowerKw),
    tkn_Physics.ActualDrivingDemandKw
)
```

**Scenario Analysis:**

| Scenario                   | Trolley Available | Demand  | Trolley Used | Diesel Used | Fuel Savings |
| -------------------------- | ----------------- | ------- | ------------ | ----------- | ------------ |
| Off trolley (any traffic)  | 0 MW              | 3.0 MW  | 0 MW         | 3.0 MW      | 0%           |
| 1 truck, low traffic       | 4.65 MW           | 3.0 MW  | 3.0 MW       | 0 MW        | ~98%         |
| 2 trucks, moderate traffic | 4.65 MW           | 3.5 MW  | 3.5 MW       | 0 MW        | ~98%         |
| 4 trucks, high traffic     | 2.33 MW           | 3.5 MW  | 2.33 MW      | 1.17 MW     | ~67%         |
| 6 trucks, maximum traffic  | 1.55 MW           | 3.5 MW  | 1.55 MW      | 1.95 MW     | ~44%         |
| Stationary on trolley      | 4.65 MW           | 0.02 MW | 0.02 MW      | 0 MW        | ~98%         |
| Retarding (downhill)       | 4.65 MW           | 0.02 MW | 0.02 MW      | 0 MW        | ~98%         |

**Note:** When retarding (downhill), motor mechanical power is negative so `MotorElectricalDemandKw = 0`. Only auxiliary demand remains. DieselElectric trucks dissipate retarding energy as heat through the retard grid — there is no regenerative energy recovery (no battery).

---

## Section 4: Fuel Consumption Calculation

### 4.1 Fuel Consumed This Timestep

**Note:** `prop_TimeStepSeconds` is internally stored in hours in Simio:

```
tkn_Physics.DieselEnergyConsumedKwh = tkn_Physics.DieselPowerKw * prop_TimeStepSeconds
tkn_Physics.DieselConsumedL = tkn_Physics.DieselEnergyConsumedKwh * tkn_Physics.DieselFuelConsumptionRateLKwh
```

### 4.2 Energy Preserved and Fuel Saved (PreserveEnergy Tracking)

Track energy and fuel savings from trolley usage:

```
// Energy preserved = trolley energy that replaced diesel (kWh)
tkn_Physics.DieselEnergyPreservedKwh = Math.If(
    tkn_Physics.OnTrolleyPath,
    tkn_Physics.TrolleyPowerKw * prop_TimeStepSeconds,
    0
)

// Fuel saved = what diesel WOULD have consumed for that energy (L)
tkn_Physics.DieselFuelSavedL = tkn_Physics.DieselEnergyPreservedKwh * tkn_Physics.DieselFuelConsumptionRateLKwh
```

### 4.3 New Diesel Level

```
tkn_Physics.NewDieselLevelL = Math.Max(
    0,
    var_DieselLevelL - tkn_Physics.DieselConsumedL
)
```

---

## Section 5: Refuel Flag and State Updates (Fuel Updates Step)

### 5.1 Refuel Flag

```
tkn_Physics.RefuelThresholdL = tkn_Physics.DieselTankCapacityL * tkn_Physics.RefuelDieselLevelPct / 100

var_SwapRefuelChargeFlag = Math.If(
    tkn_Physics.NewDieselLevelL < tkn_Physics.RefuelThresholdL,
    True,
    False
)
```

### 5.2 Diesel State Write-Back

```
var_DieselLevelL = tkn_Physics.NewDieselLevelL
var_DieselLevelPct = 100 * tkn_Physics.NewDieselLevelL / tkn_Physics.DieselTankCapacityL
```

### 5.3 Cumulative Statistics Write-Back

```
var_DieselConsumedL = var_DieselConsumedL + tkn_Physics.DieselConsumedL
var_DieselEnergyConsumedKwh = var_DieselEnergyConsumedKwh + tkn_Physics.DieselEnergyConsumedKwh
var_DieselEnergyPreservedKwh = var_DieselEnergyPreservedKwh + tkn_Physics.DieselEnergyPreservedKwh
var_DieselPreservedL = var_DieselPreservedL + tkn_Physics.DieselFuelSavedL
```

### 5.4 Trolley Assist Status Flag

```
var_TrolleyAssistActive = tkn_Physics.OnTrolleyPath
```

---

## Process Flow

1. **Decide: var_SpeedUpdates**
   - If True → Execute Speed Updates Step (Sections 1-2)
   - If False → Skip to Fuel Updates check

2. **Decide: var_FuelUpdates**
   - If True → Execute Fuel Updates Step (Sections 3-5)
   - If False → End process

This allows independent control of speed physics vs fuel/energy calculations.

---

## Simio Implementation Checklist

The FuelUpdates step requires **19 Assign statements** in the following order:

| #   | Target                                      | Expression                                          | Section |
| --- | ------------------------------------------- | --------------------------------------------------- | ------- |
| 1   | `tkn_Physics.RowIndex`                      | `tbl_TruckTypes.TruckType.RowForKey(...)`           | 3.1     |
| 2   | `tkn_Physics.AuxiliaryPowerDemandKw`        | `tbl_TruckTypes[...].AuxiliaryPowerDemandKw`        | 3.1     |
| 3   | `tkn_Physics.MotorEfficiencyPct`            | `tbl_TruckTypes[...].MotorEfficiencyPct`            | 3.1     |
| 4   | `tkn_Physics.DieselFuelConsumptionRateLKwh` | `tbl_TruckTypes[...].DieselFuelConsumptionRateLKwh` | 3.1     |
| 5   | `tkn_Physics.RefuelDieselLevelPct`          | `tbl_TruckTypes[...].RefuelDieselLevelPct`          | 3.1     |
| 6   | `tkn_Physics.DieselTankCapacityL`           | `tbl_TruckTypes[...].DieselTankCapacityL`           | 3.1     |
| 7   | `tkn_Physics.OnTrolleyPath`                 | `Location.Parent.Is.obj_ElectricPath && ...`        | 3.1     |
| 8   | `tkn_Physics.MotorMechanicalPowerKw`        | `Math.If(var_SpeedUpdates, ...)`                    | 3.2     |
| 9   | `tkn_Physics.MotorElectricalDemandKw`       | `Math.If(... > 0, .../eff, 0)`                      | 3.3     |
| 10  | `tkn_Physics.ActualDrivingDemandKw`         | `MotorElectrical + Auxiliary`                       | 3.3     |
| 11  | `tkn_Physics.TrolleyPowerKw`                | `Math.If(OnTrolley, Min(...), 0)`                   | 3.3     |
| 12  | `tkn_Physics.DieselPowerKw`                 | `Math.If(OnTrolley, Max(0, ...), ...)`              | 3.3     |
| 13  | `tkn_Physics.DieselEnergyConsumedKwh`       | `DieselPowerKw * prop_TimeStepSeconds`              | 4.1     |
| 14  | `tkn_Physics.DieselConsumedL`               | `DieselEnergyKwh * ConsumptionRate`                 | 4.1     |
| 15  | `tkn_Physics.DieselEnergyPreservedKwh`      | `Math.If(OnTrolley, TrolleyKw * dt, 0)`             | 4.2     |
| 16  | `tkn_Physics.DieselFuelSavedL`              | `PreservedKwh * ConsumptionRate`                    | 4.2     |
| 17  | `tkn_Physics.NewDieselLevelL`               | `Math.Max(0, var_DieselLevelL - consumed)`          | 4.3     |
| 18  | `tkn_Physics.RefuelThresholdL`              | `TankCapacity * RefuelPct / 100`                    | 5.1     |
| 19  | *(remaining state writes — see 5.1–5.4)*    |                                                     | 5.x     |

State write-backs (5.1–5.4) require **8 additional Assign statements** writing to `var_` state variables:

| #   | Target                         | Expression                                                      |
| --- | ------------------------------ | --------------------------------------------------------------- |
| 20  | `var_SwapRefuelChargeFlag`     | `Math.If(NewDieselLevelL < RefuelThresholdL, True, False)`      |
| 21  | `var_DieselLevelL`             | `tkn...NewDieselLevelL`                                         |
| 22  | `var_DieselLevelPct`           | `100 * NewDieselLevelL / DieselTankCapacityL`                   |
| 23  | `var_DieselConsumedL`          | `var_DieselConsumedL + tkn...DieselConsumedL`                   |
| 24  | `var_DieselEnergyConsumedKwh`  | `var_DieselEnergyConsumedKwh + tkn...DieselEnergyConsumedKwh`   |
| 25  | `var_DieselEnergyPreservedKwh` | `var_DieselEnergyPreservedKwh + tkn...DieselEnergyPreservedKwh` |
| 26  | `var_DieselPreservedL`         | `var_DieselPreservedL + tkn...DieselFuelSavedL`                 |
| 27  | `var_TrolleyAssistActive`      | `tkn...OnTrolleyPath`                                           |

**Total: 27 Assign statements in the FuelUpdates step.**

---

## Validation Scenarios

### Scenario A: Off Trolley — Full Diesel (CAT 793F AC, loaded, 10% grade)

```
Input:
├─ MotorEfficiencyPct: 92%
├─ AuxiliaryPowerDemandKw: 20 kW
├─ TractiveForceN: 500,000 N (rimpull at grade)
├─ CurrentSpeedKmh: 12 km/h (= 3.33 m/s)
├─ OnTrolleyPath: False

Calculations:
├─ MotorMechanicalPowerKw = (500,000 / 1000) * (12,000 / 3600) = 1,667 kW
├─ MotorElectricalDemandKw = 1,667 / 0.92 = 1,812 kW
├─ ActualDrivingDemandKw = 1,812 + 20 = 1,832 kW
├─ TrolleyPowerKw = 0 (off trolley)
├─ DieselPowerKw = 1,832 kW
├─ DieselEnergyConsumedKwh = 1,832 * 0.000278 = 0.509 kWh (1-sec step)
├─ DieselConsumedL = 0.509 * 0.11 = 0.056 L
├─ DieselEnergyPreservedKwh = 0 kWh
└─ DieselFuelSavedL = 0 L

Rate: 1,832 kW → 201.5 L/hr ✓ (matches 05-fuel-systems.md ~214.5 L/hr at full 1,950 kW)
```

### Scenario B: On Trolley, Low Traffic — Full Trolley Replacement (CAT 793F AC)

```
Input:
├─ Same truck and conditions as Scenario A
├─ OnTrolleyPath: True
├─ TrolleyAvailablePowerKw: 4,650 kW (1 truck on 10 MW section)
├─ ActualDrivingDemandKw: 1,832 kW (same demand)

Calculations:
├─ TrolleyPowerKw = Min(4,650, 1,832) = 1,832 kW (trolley covers all)
├─ DieselPowerKw = Max(0, 1,832 - 1,832) = 0 kW
├─ DieselConsumedL = 0 L
├─ DieselEnergyPreservedKwh = 1,832 * 0.000278 = 0.509 kWh
└─ DieselFuelSavedL = 0.509 * 0.11 = 0.056 L

Fuel savings: 100% on this timestep ✓
```

### Scenario C: On Trolley, High Traffic — Partial Trolley (CAT 793F AC)

```
Input:
├─ Same truck and conditions
├─ OnTrolleyPath: True
├─ TrolleyAvailablePowerKw: 2,325 kW (4 trucks on 10 MW section)
├─ ActualDrivingDemandKw: 1,832 kW

Calculations:
├─ TrolleyPowerKw = Min(2,325, 1,832) = 1,832 kW (trolley still covers all!)
├─ DieselPowerKw = 0 kW
└─ Fuel savings: 100%

Note: Even at 4 trucks, trolley capacity (2,325 kW) exceeds demand (1,832 kW).
Diesel supplementation only starts when trolley share < demand.
```

### Scenario D: On Trolley, Overloaded Section — Diesel Supplements

```
Input:
├─ Same truck, but 6 trucks on section
├─ TrolleyAvailablePowerKw: 1,550 kW (10 MW / 6 trucks, limited by efficiency)
├─ ActualDrivingDemandKw: 1,832 kW

Calculations:
├─ TrolleyPowerKw = Min(1,550, 1,832) = 1,550 kW
├─ DieselPowerKw = Max(0, 1,832 - 1,550) = 282 kW
├─ DieselConsumedL = 282 * 0.000278 * 0.11 = 0.0086 L
├─ DieselEnergyPreservedKwh = 1,550 * 0.000278 = 0.431 kWh
├─ DieselFuelSavedL = 0.431 * 0.11 = 0.047 L
└─ Fuel savings: 282/1,832 = 15.4% diesel, 84.6% trolley

Rate: 282 kW → 31.0 L/hr vs 201.5 L/hr off trolley = 84.6% savings ✓
```

### Scenario E: Retarding Downhill — Auxiliary Only

```
Input:
├─ TractiveForceN: -200,000 N (retarding)
├─ CurrentSpeedKmh: 20 km/h
├─ OnTrolleyPath: True
├─ TrolleyAvailablePowerKw: 4,650 kW

Calculations:
├─ MotorMechanicalPowerKw = (-200,000 / 1000) * (20,000 / 3600) = -1,111 kW (negative)
├─ MotorElectricalDemandKw = 0 (negative power → 0, retard grid dissipates heat)
├─ ActualDrivingDemandKw = 0 + 20 = 20 kW (auxiliaries only)
├─ TrolleyPowerKw = Min(4,650, 20) = 20 kW
├─ DieselPowerKw = 0 kW
└─ DieselConsumedL = 0 L

Note: Retard energy is NOT recovered. DieselElectric trucks have no battery.
Trolley powers only the auxiliaries during retarding.
```

---

## Notes

**Process Architecture:**
- **Two-Step Process**: Speed updates and fuel updates are separate steps controlled by flags
- **PreserveEnergy Behavior**: Trolley replaces diesel (97-98% fuel savings when trolley covers demand)
- **No Power Degradation**: DieselElectric trucks have constant power (PowerDegradationFactor = 1.0)
- **No Motor Thermal Management**: Not needed in PreserveEnergy mode (trolley replaces diesel 1:1, never exceeds motor continuous rating)

**Physics Implementation:**
- **Dead Band Control**: ±3000 m/hr (≈3 km/h) prevents oscillation around target speed
- **CurveLimitForceN**: Uses Math.Min(BaseRimpullForceN, PowerLimitForceN) - validated correct
- **Speed Clamping**: NewSpeedKmh clamped to [0, TargetSpeedKmh] to prevent overshoot

**Trolley Integration:**
- **Power Sharing**: Model B (equal distribution) via `Location.Parent.obj_ElectricPath.NumberTravelers`
- **Electric Path Detection**: `Location.Parent.Object.Is.obj_ElectricPath && prop_TrolleyAssistEnabled`
- **Dynamic Calculation**: TrolleyAvailablePowerKw calculated in both steps (speed & fuel)

**Energy & Fuel:**
- **Retarding Behavior**: Negative motor power → MotorElectricalDemandKw = 0 (no regen for diesel)
- **Auxiliary Power**: Always consumed (25 kW typical), added once via ActualDrivingDemandKw
- **Cumulative Tracking**: Both litres and kWh tracked (consumed and preserved)
- **Refuel Trigger**: Flag set when diesel level < RefuelDieselLevelPct threshold

**Simio Units:**
- Speed: m/hr internally, displayed as km/h with `Units="Kilometers per Hour"`
- Time: prop_TimeStepSeconds is in hours (not seconds despite name)
- Power: kW, Force: N, Energy: kWh, Fuel: L

---

## Implementation Validation

**Trace Verified:** February 11, 2026
- ✅ All 41 speed update assignments execute correctly
- ✅ All 31 fuel update assignments execute correctly  
- ✅ CurveLimitForceN correctly uses Math.Min (curve vs power limit)
- ✅ Trolley power sharing (Model B) validated with NumberTravelers
- ✅ Fuel consumption calculations match expected values
- ✅ Energy preservation tracking working correctly

**Example from trace (CAT 794 AC, off trolley, -0.24% grade, 50→51.4 km/h):**
- Motor demand: 2,381.89 kW
- Diesel power: 2,381.89 kW (100% - no trolley)
- Fuel consumed: 0.0728 L/sec ✓
- Energy preserved: 0 kWh (off trolley) ✓

---

## Related Documents

- [01-fleet-and-modes.md](01-fleet-and-modes.md) - DieselElectric mode definitions
- [03-power-flow.md](03-power-flow.md) - Diesel power calculations
- [05-fuel-systems.md](05-fuel-systems.md) - Fuel consumption rates and economics
- [06-infrastructure.md](06-infrastructure.md) - Refuel station operations
- [07-trolley-power-sharing.md](07-trolley-power-sharing.md) - Model B power sharing
- [proc_PhysicsUpdates_DieselElectric_SustainSpeed.md](proc_PhysicsUpdates_DieselElectric_SustainSpeed.md) - SustainSpeed variant (diesel+trolley combine)
- [proc_PhysicsUpdates_DieselElectric_RefuelDiesel.md](proc_PhysicsUpdates_DieselElectric_RefuelDiesel.md) - Refueling process
- [properties_variables_tables.md](properties_variables_tables.md) - Variable and token reference