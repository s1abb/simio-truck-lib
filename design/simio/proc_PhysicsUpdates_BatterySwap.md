# proc_PhysicsUpdates_BatterySwap

This process handles the physics updates for trucks operating in **Battery Swap** mode. It calculates speed changes, battery consumption, and battery health degradation based on the current state of the truck and its battery.

## Overview

The process is triggered by `tmr_TimeStep.Event` when:
- Truck routing conditions determine Battery Swap mode is active
- The truck is moving on the network

## Token Variables

Uses `tkn_TimeStepCalculations` shared token with 66 variables. Key variables for BatterySwap mode:

**Properties (Read from tables):**
- `EmptyWeightKg`, `BaseRimpullForceN`, `BaseRetardForceN`
- `MaxSpeedKmh_Loaded`, `MaxSpeedKmh_Empty`, `RollingResistance`
- `MotorEfficiencyPct`, `RegenEfficiencyPct`, `AuxiliaryPowerDemandKw`
- `RatedBatteryStorageEnergyKwh`, `EndOfLifeBatteryHealthPct`, `SwapBatterySOCPct`

**Speed Physics:**
- `CurrentGrade`, `CurrentSpeedKmh`, `CurrentWeightKg`
- `TargetSpeedKmh`, `TractiveForceN`, `AccelerationMs2`, `NewSpeedKmh`

**Battery Calculations:**
- `BatteryPowerKw`, `EnergyDeltaKwh`, `NewBatterySOCPct`
- `AbsoluteEnergyThroughputKwh`, `NewCumulativeThroughputKwh`, `NewBatteryHealthPct`

---

## Section 1: Read Current State (Speed Updates Step)

Executed when `var_SpeedUpdates == True`

### 1.1 Movement State

```
tkn_TimeStepCalculations.CurrentGrade = Movement.Pitch
tkn_TimeStepCalculations.CurrentSpeedKmh = Movement.Rate km/h
```

### 1.2 Truck Properties

Lookup row index and read truck properties:

```
tkn_TimeStepCalculations.RowIndex = tbl_TruckTypes.TruckType.RowForKey(String.FromList(list_TruckTypes, prop_TruckType))

tkn_TimeStepCalculations.EmptyWeightKg = tbl_TruckTypes[tkn_TimeStepCalculations.RowIndex].EmptyOperatingWeightKg
tkn_TimeStepCalculations.CurrentWeightKg = Math.If(var_Loaded, var_Payload, tkn_TimeStepCalculations.EmptyWeightKg)
tkn_TimeStepCalculations.BaseRimpullForceN = tbl_TruckTypes[tkn_TimeStepCalculations.RowIndex].RimpullForceN
tkn_TimeStepCalculations.BaseRetardForceN = tbl_TruckTypes[tkn_TimeStepCalculations.RowIndex].RetardForceN
tkn_TimeStepCalculations.MaxSpeedKmh_Loaded = tbl_TruckTypes[tkn_TimeStepCalculations.RowIndex].MaxSpeedKmh_Loaded
tkn_TimeStepCalculations.MaxSpeedKmh_Empty = tbl_TruckTypes[tkn_TimeStepCalculations.RowIndex].MaxSpeedKmh_Empty
tkn_TimeStepCalculations.RollingResistance = tbl_TruckTypes[tkn_TimeStepCalculations.RowIndex].RollingResistance
tkn_TimeStepCalculations.MotorEfficiencyPct = tbl_TruckTypes[tkn_TimeStepCalculations.RowIndex].MotorEfficiencyPct
tkn_TimeStepCalculations.RegenEfficiencyPct = tbl_TruckTypes[tkn_TimeStepCalculations.RowIndex].RegenEfficiencyPct
tkn_TimeStepCalculations.AuxiliaryPowerDemandKw = tbl_TruckTypes[tkn_TimeStepCalculations.RowIndex].AuxiliaryPowerDemandKw
tkn_TimeStepCalculations.SwapBatterySOCPct = Math.If(tbl_TruckTypes[tkn_TimeStepCalculations.RowIndex].TruckMode==List.list_TruckMode.DieselElectric, 0, tbl_TruckTypes[tkn_TimeStepCalculations.RowIndex].SwapBatterySOCPct)
```

### 1.3 Battery State

Read battery properties from battery entity (with DieselElectric mode protection):

```
tkn_TimeStepCalculations.BatteryHealthPct = Math.If(tbl_TruckTypes[tkn_TimeStepCalculations.RowIndex].TruckMode==List.list_TruckMode.DieselElectric, 100, BatteryStation.Contents.FirstItem.obj_Battery.var_BatteryHealthPct)
tkn_TimeStepCalculations.RatedBatteryStorageEnergyKwh = Math.If(tbl_TruckTypes[tkn_TimeStepCalculations.RowIndex].TruckMode==List.list_TruckMode.DieselElectric, 0, BatteryStation.Contents.FirstItem.obj_Battery.var_RatedStorageEnergyKwh)
tkn_TimeStepCalculations.EndOfLifeBatteryHealthPct = Math.If(tbl_TruckTypes[tkn_TimeStepCalculations.RowIndex].TruckMode==List.list_TruckMode.DieselElectric, 0, BatteryStation.Contents.FirstItem.obj_Battery.var_EndOfLifeBatteryHealthPct)
tkn_TimeStepCalculations.CurrentBatterySOCPct = Math.If(tbl_TruckTypes[tkn_TimeStepCalculations.RowIndex].TruckMode==List.list_TruckMode.DieselElectric, 100, BatteryStation.Contents.FirstItem.obj_Battery.var_BatterySOCPct)
```

Calculate power degradation factor:

```
tkn_TimeStepCalculations.PowerDegradationFactor = Math.If(
    prop_PowerDegradationActive,
    Math.Max(
        tkn_TimeStepCalculations.BatteryHealthPct / 100,
        tkn_TimeStepCalculations.EndOfLifeBatteryHealthPct / 100
    ),
    1.0
)
```

---

## Section 2: Speed Physics Calculations (Speed Updates Step)

### 2.1 Target Speed

```
tkn_TimeStepCalculations.MaxSpeedKmh = Math.If(
    var_Loaded,
    tkn_TimeStepCalculations.MaxSpeedKmh_Loaded,
    tkn_TimeStepCalculations.MaxSpeedKmh_Empty
)
tkn_TimeStepCalculations.PathSpeedLimitKmh = Math.If(
    Location.Parent.Is.obj_ElectricPath,
    Location.Parent.obj_ElectricPath.SpeedLimit,
    DesiredSpeed
) km/h
tkn_TimeStepCalculations.TargetSpeedKmh = Math.Min(
    tkn_TimeStepCalculations.PathSpeedLimitKmh,
    tkn_TimeStepCalculations.MaxSpeedKmh
)
```

### 2.2 Resistance Forces

```
tkn_TimeStepCalculations.GradeResistanceForceN = tkn_TimeStepCalculations.CurrentWeightKg * 9.81 * tkn_TimeStepCalculations.CurrentGrade / 100
tkn_TimeStepCalculations.RollingResistanceForceN = tkn_TimeStepCalculations.CurrentWeightKg * 9.81 * tkn_TimeStepCalculations.RollingResistance
tkn_TimeStepCalculations.TotalResistanceN = tkn_TimeStepCalculations.GradeResistanceForceN + tkn_TimeStepCalculations.RollingResistanceForceN
```

### 2.3 Tractive Force (Dead Band Control with Power Degradation)

Apply ±3000 m/hr (3 km/h) dead band with power degradation factor:

```
tkn_TimeStepCalculations.TractiveForceN = Math.If(
    tkn_TimeStepCalculations.CurrentSpeedKmh < tkn_TimeStepCalculations.TargetSpeedKmh - 3000,
    tkn_TimeStepCalculations.BaseRimpullForceN * tkn_TimeStepCalculations.PowerDegradationFactor,
    Math.If(
        tkn_TimeStepCalculations.CurrentSpeedKmh > tkn_TimeStepCalculations.TargetSpeedKmh + 3000,
        -tkn_TimeStepCalculations.BaseRetardForceN * tkn_TimeStepCalculations.PowerDegradationFactor,
        0
    )
)
```

### 2.4 Acceleration

```
tkn_TimeStepCalculations.NetTractiveForceN = tkn_TimeStepCalculations.TractiveForceN - tkn_TimeStepCalculations.TotalResistanceN
tkn_TimeStepCalculations.AccelerationMs2 = tkn_TimeStepCalculations.NetTractiveForceN / tkn_TimeStepCalculations.CurrentWeightKg
```

### 2.5 New Speed

```
tkn_TimeStepCalculations.NewSpeedKmh = Math.Max(
    0,
    Math.Min(
        tkn_TimeStepCalculations.TargetSpeedKmh,
        tkn_TimeStepCalculations.CurrentSpeedKmh + tkn_TimeStepCalculations.AccelerationMs2 * 3600 * prop_TimeStepSeconds * 3600
    )
)
```

### 2.6 Write Speed Update

```
Movement.Rate = tkn_TimeStepCalculations.NewSpeedKmh with Units="Kilometers per Hour"
```

---

## Section 3: Battery Power Calculations (Battery Updates Step)

Executed when `var_BatteryUpdates == True`

### 3.1 Re-read Battery State

```
tkn_TimeStepCalculations.RowIndex = tbl_TruckTypes.TruckType.RowForKey(String.FromList(list_TruckTypes, prop_TruckType))
tkn_TimeStepCalculations.AuxiliaryPowerDemandKw = tbl_TruckTypes[tkn_TimeStepCalculations.RowIndex].AuxiliaryPowerDemandKw
tkn_TimeStepCalculations.SwapBatterySOCPct = Math.If(tbl_TruckTypes[tkn_TimeStepCalculations.RowIndex].TruckMode==List.list_TruckMode.DieselElectric, 0, tbl_TruckTypes[tkn_TimeStepCalculations.RowIndex].SwapBatterySOCPct)
tkn_TimeStepCalculations.CurrentBatterySOCPct = Math.If(tbl_TruckTypes[tkn_TimeStepCalculations.RowIndex].TruckMode==List.list_TruckMode.DieselElectric, 100, BatteryStation.Contents.FirstItem.obj_Battery.var_BatterySOCPct)
tkn_TimeStepCalculations.BatteryHealthPct = Math.If(tbl_TruckTypes[tkn_TimeStepCalculations.RowIndex].TruckMode==List.list_TruckMode.DieselElectric, 100, BatteryStation.Contents.FirstItem.obj_Battery.var_BatteryHealthPct)
tkn_TimeStepCalculations.RatedBatteryStorageEnergyKwh = Math.If(tbl_TruckTypes[tkn_TimeStepCalculations.RowIndex].TruckMode==List.list_TruckMode.DieselElectric, 0, BatteryStation.Contents.FirstItem.obj_Battery.var_RatedStorageEnergyKwh)
tkn_TimeStepCalculations.RatedLifetimeThroughputKwh = Math.If(tbl_TruckTypes[tkn_TimeStepCalculations.RowIndex].TruckMode==List.list_TruckMode.DieselElectric, 0, BatteryStation.Contents.FirstItem.obj_Battery.var_RatedLifetimeThroughputKwh)
tkn_TimeStepCalculations.EndOfLifeBatteryHealthPct = Math.If(tbl_TruckTypes[tkn_TimeStepCalculations.RowIndex].TruckMode==List.list_TruckMode.DieselElectric, 0, BatteryStation.Contents.FirstItem.obj_Battery.var_EndOfLifeBatteryHealthPct)
tkn_TimeStepCalculations.CurrentCumulativeThroughputKwh = Math.If(tbl_TruckTypes[tkn_TimeStepCalculations.RowIndex].TruckMode==List.list_TruckMode.DieselElectric, 0, BatteryStation.Contents.FirstItem.obj_Battery.var_BatteryCumulativeThroughputKwh)
```

Recalculate power degradation factor:

```
tkn_TimeStepCalculations.PowerDegradationFactor = Math.If(
    prop_PowerDegradationActive,
    Math.Max(
        tkn_TimeStepCalculations.BatteryHealthPct / 100,
        tkn_TimeStepCalculations.EndOfLifeBatteryHealthPct / 100
    ),
    1.0
)
```

### 3.2 Motor Mechanical Power

Conditional on var_SpeedUpdates (zero when stationary):

```
tkn_TimeStepCalculations.MotorMechanicalPowerKw = Math.If(
    var_SpeedUpdates,
    (tkn_TimeStepCalculations.TractiveForceN / 1000) * (tkn_TimeStepCalculations.CurrentSpeedKmh / 3600),
    0
)
```

### 3.3 Battery Power with Efficiency

```
tkn_TimeStepCalculations.BatteryPowerKw = Math.If(
    tkn_TimeStepCalculations.MotorMechanicalPowerKw > 0,
    tkn_TimeStepCalculations.MotorMechanicalPowerKw / (tkn_TimeStepCalculations.MotorEfficiencyPct / 100),
    Math.If(
        tkn_TimeStepCalculations.MotorMechanicalPowerKw < 0,
        tkn_TimeStepCalculations.MotorMechanicalPowerKw * (tkn_TimeStepCalculations.RegenEfficiencyPct / 100),
        tkn_TimeStepCalculations.AuxiliaryPowerDemandKw
    )
)
```

### 3.4 Energy Delta

**Note:** `prop_TimeStepSeconds` is internally stored in hours in Simio, so no division by 3600 needed:

```
tkn_TimeStepCalculations.EnergyDeltaKwh = tkn_TimeStepCalculations.BatteryPowerKw * prop_TimeStepSeconds
```

---

## Section 4: Battery SOC Update

### 4.1 Effective Capacity

```
tkn_TimeStepCalculations.EffectiveBatteryCapacityKwh = tkn_TimeStepCalculations.RatedBatteryStorageEnergyKwh * tkn_TimeStepCalculations.PowerDegradationFactor
```

### 4.2 New SOC

```
tkn_TimeStepCalculations.NewBatterySOCPct = Math.Max(
    0,
    Math.Min(
        100,
        tkn_TimeStepCalculations.CurrentBatterySOCPct - 100 * tkn_TimeStepCalculations.EnergyDeltaKwh / tkn_TimeStepCalculations.EffectiveBatteryCapacityKwh
    )
)
```

---

## Section 5: Battery Health Degradation (Battery Updates Step)

### 5.1 Energy Throughput

```
tkn_TimeStepCalculations.AbsoluteEnergyThroughputKwh = Math.Abs(tkn_TimeStepCalculations.EnergyDeltaKwh)
tkn_TimeStepCalculations.NewCumulativeThroughputKwh = tkn_TimeStepCalculations.CurrentCumulativeThroughputKwh + tkn_TimeStepCalculations.AbsoluteEnergyThroughputKwh
```

### 5.2 Health Calculation

```
tkn_TimeStepCalculations.NewBatteryHealthPct = Math.Max(
    tkn_TimeStepCalculations.EndOfLifeBatteryHealthPct,
    100 - (
        tkn_TimeStepCalculations.NewCumulativeThroughputKwh / 
        (tkn_TimeStepCalculations.RatedLifetimeThroughputKwh * (100 - tkn_TimeStepCalculations.EndOfLifeBatteryHealthPct))
    )
)
```

---

## Section 6: Swap Flag and State Updates (Battery Updates Step)

### 6.1 Swap Flag

```
var_SwapRefuelChargeFlag = Math.If(
    tkn_TimeStepCalculations.NewBatterySOCPct < tkn_TimeStepCalculations.SwapBatterySOCPct,
    True,
    False
)
```

### 6.2 Battery State Write-Back

```
BatteryStation.Contents.FirstItem.obj_Battery.var_BatterySOCPct = tkn_TimeStepCalculations.NewBatterySOCPct
BatteryStation.Contents.FirstItem.obj_Battery.var_BatteryCumulativeThroughputKwh = tkn_TimeStepCalculations.NewCumulativeThroughputKwh
BatteryStation.Contents.FirstItem.obj_Battery.var_BatteryHealthPct = tkn_TimeStepCalculations.NewBatteryHealthPct
```

### 6.3 Battery Visual Symbol

```
BatteryStation.Contents.FirstItem.obj_Battery.var_CurrentSymbolIndex = Math.If(
    tkn_TimeStepCalculations.NewBatterySOCPct >= 80, obj_Battery.List.list_CurrentSymbolIndex.Green,
    Math.If(
        tkn_TimeStepCalculations.NewBatterySOCPct >= 60, obj_Battery.List.list_CurrentSymbolIndex.Yellow,
        Math.If(
            tkn_TimeStepCalculations.NewBatterySOCPct >= 40, obj_Battery.List.list_CurrentSymbolIndex.Orange,
            Math.If(
                tkn_TimeStepCalculations.NewBatterySOCPct >= 20, obj_Battery.List.list_CurrentSymbolIndex.DarkOrange,
                obj_Battery.List.list_CurrentSymbolIndex.Red
            )
        )
    )
)
```

---

## Process Flow

1. **Decide: var_SpeedUpdates**
   - If True → Execute Speed Updates Step
   - If False → Skip to Battery Updates check

2. **Decide: var_BatteryUpdates**
   - If True → Execute Battery Updates Step
   - If False → End process

This allows independent control of speed physics vs battery/energy calculations.

---

## Notes

- **Two-Step Process**: Speed updates and battery updates are separate steps controlled by flags
- **DieselElectric Protection**: Battery reads protected with Math.If checks for DieselElectric trucks (no battery entity)
- **Dead Band Control**: ±3000 m/hr (≈3 km/h in Simio internal units) prevents oscillation around target speed
- **Power Degradation**: Applied to both rimpull and retard forces, reducing available acceleration/braking as battery ages
- **Electric Path Detection**: Uses `Location.Parent.Is.obj_ElectricPath` to check for trolley paths
- **Motor Power Conditional**: `Math.If(var_SpeedUpdates, formula, 0)` ensures zero power when stationary
- **Unit Conversions (Simio internal)**: 
  - Speed stored internally as m/hr, displayed as km/h with `Units="Kilometers per Hour"`
  - NewSpeedKmh: `AccelerationMs2 * 3600 * prop_TimeStepSeconds * 3600` converts m/s² to m/hr per timestep
  - MotorPower: `CurrentSpeedKmh / 3600` converts km/h display units back to m/s for power calculation
  - EnergyDelta: `BatteryPowerKw * prop_TimeStepSeconds` works because prop_TimeStepSeconds property unit is Hours internally
- **Regenerative Braking**: Negative motor power charges battery at `RegenEfficiencyPct` efficiency
- **Auxiliary Load**: Only applied when MotorMechanicalPowerKw == 0 (stationary); not added to motor power during driving
- **Health Degradation**: Formula: `100 - (NewCumulativeThroughput / (RatedLifetime * (100 - EndOfLife)))`
- **Swap Trigger**: Flag set when SOC drops below `SwapBatterySOCPct` threshold
- **Visual Symbol**: 5 states using list enum (Green≥80%, Yellow≥60%, Orange≥40%, DarkOrange≥20%, Red<20%)
- **Speed Clamping**: NewSpeedKmh clamped to [0, TargetSpeedKmh] to prevent overshoot
