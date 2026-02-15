# proc_PhysicsUpdates_DieselElectric_SustainSpeed

**Implementation Status:**
- ✅ **Speed Updates Step**: Fully implemented (41 assigns)
- ⚠️ **Fuel Updates Step**: Empty in XML - design documented, implementation pending
- ⚠️ **Motor Thermal Management**: Design documented (Section 2.3), not implemented in XML

This process handles the physics updates for trucks operating in **DieselElectric + SustainSpeed** mode. Trolley power combines with diesel generator output to provide increased tractive effort, enabling 1.3-1.78x speed improvements on steep grades.

## Overview

The process is triggered by `tmr_TimeStep.Event` when:
- Truck is DieselElectric type on a trolley-assisted path
- Power Flow Mode is set to SustainSpeed
- The truck is moving on the network

## Token Variables

Uses `tkn_TimeStepCalculations` shared token with 66+ variables. Key variables for DieselElectric SustainSpeed mode:

**Properties (Read from tables):**
- `EmptyWeightKg`, `BaseRimpullForceN`, `BaseRetardForceN`
- `MaxSpeedKmh_Loaded`, `MaxSpeedKmh_Empty`, `RollingResistance`
- `MotorEfficiencyPct`, `AuxiliaryPowerDemandKw`
- `DieselFuelConsumptionRateLKwh`, `RefuelDieselLevelPct`
- `DieselGeneratorMaxPowerKw`
- `MaxMotorPowerKw_Continuous`, `MaxMotorPowerKw_Peak`, `MaxMotorPeakDurationSec`

**Trolley Power Sharing (from path properties):**
- `TrolleySectionTotalPowerKw`, `TrolleyMaxPowerPerTruckKw`, `TrolleyEfficiencyPct`
- `TrolleyActiveTrucksOnSection`, `TrolleySharedPowerPerTruckKw`, `TrolleyAvailablePowerKw`

**Speed Physics:**
- `CurrentGrade`, `CurrentSpeedKmh`, `CurrentWeightKg`
- `TargetSpeedKmh`, `TractiveForceN`, `AccelerationMs2`, `NewSpeedKmh`
- `PowerLimitForceN`, `TotalAvailablePowerKw`, `OnTrolleyPath`

**Motor Thermal Management:**
- `MotorElectricalDemandKw`, `CurrentPowerRatio`
- `ThermalAccumulationRatePerSec`, `CoolingRatePerSec`
- `MotorPowerLimitKw`, `CanUsePeakMode`, `MustStopPeakMode`

**Fuel Calculations:**
- `ActualDrivingDemandKw`, `MotorMechanicalPowerKw`
- `DieselPowerKw`, `DieselContributionKw`
- `TrolleyDrivingPowerKw`, `TrolleyContributionKw`
- `DieselConsumedL`, `NewDieselLevelL`

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
tkn_TimeStepCalculations.AuxiliaryPowerDemandKw = tbl_TruckTypes[tkn_TimeStepCalculations.RowIndex].AuxiliaryPowerDemandKw
tkn_TimeStepCalculations.DieselGeneratorMaxPowerKw = tbl_TruckTypes[tkn_TimeStepCalculations.RowIndex].DieselGeneratorMaxPowerKw
```

### 1.3 DieselElectric State

DieselElectric trucks have no battery entity - diesel level tracked directly on truck:

```
tkn_TimeStepCalculations.RefuelDieselLevelPct = tbl_TruckTypes[tkn_TimeStepCalculations.RowIndex].RefuelDieselLevelPct
tkn_TimeStepCalculations.DieselFuelConsumptionRateLKwh = tbl_TruckTypes[tkn_TimeStepCalculations.RowIndex].DieselFuelConsumptionRateLKwh
tkn_TimeStepCalculations.DieselTankCapacityL = tbl_TruckTypes[tkn_TimeStepCalculations.RowIndex].DieselTankCapacityL
tkn_TimeStepCalculations.OnTrolleyPath = Location.Parent.Is.obj_ElectricPath && obj_ElectricPath.prop_TrolleyAssistEnabled
```

DieselElectric trucks have no power degradation (no battery aging):

```
tkn_TimeStepCalculations.PowerDegradationFactor = 1.0
```

### 1.4 Trolley Power Sharing (Model B)

> **Reference:** `design/concept/07-trolley-power-sharing.md` (Model B: Power Sharing - Recommended)

When on a trolley-assisted path, calculate available trolley power based on section capacity and active truck count:

```
// Read trolley section properties from path
tkn_TimeStepCalculations.TrolleySectionTotalPowerKw = Math.If(
    tkn_TimeStepCalculations.OnTrolleyPath,
    Location.Parent.obj_ElectricPath.prop_TrolleySectionTotalPowerKw,
    0
)
tkn_TimeStepCalculations.TrolleyMaxPowerPerTruckKw = Math.If(
    tkn_TimeStepCalculations.OnTrolleyPath,
    Location.Parent.obj_ElectricPath.prop_TrolleyMaxPowerPerTruckKw,
    0
)
tkn_TimeStepCalculations.TrolleyEfficiencyPct = Math.If(
    tkn_TimeStepCalculations.OnTrolleyPath,
    Location.Parent.obj_ElectricPath.prop_TrolleyEfficiencyPct,
    0
)

// Count active trucks on this trolley section (Simio built-in property)
tkn_TimeStepCalculations.TrolleyActiveTrucksOnSection = Math.If(
    tkn_TimeStepCalculations.OnTrolleyPath,
    Location.Parent.obj_ElectricPath.NumberTravelers,
    0
)

// Calculate shared power per truck (equal distribution)
tkn_TimeStepCalculations.TrolleySharedPowerPerTruckKw = Math.If(
    tkn_TimeStepCalculations.TrolleyActiveTrucksOnSection > 0,
    tkn_TimeStepCalculations.TrolleySectionTotalPowerKw / tkn_TimeStepCalculations.TrolleyActiveTrucksOnSection,
    0
)

// Limit by truck pantograph rating and apply system efficiency
tkn_TimeStepCalculations.TrolleyAvailablePowerKw = Math.Min(
    tkn_TimeStepCalculations.TrolleySharedPowerPerTruckKw,
    tkn_TimeStepCalculations.TrolleyMaxPowerPerTruckKw
) * (tkn_TimeStepCalculations.TrolleyEfficiencyPct / 100)
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

### 2.3 Motor Thermal Management

> **Reference:** `design/concept/03-power-flow.md` - Motor Thermal Management (Section 3.2)  
> **Implementation Status:** ⚠️ NOT YET IMPLEMENTED - Design documented, XML implementation pending

Motor thermal management ensures the truck respects motor continuous and peak power ratings. In SustainSpeed mode with trolley assist, total available electrical power (diesel + trolley) can exceed motor capabilities, requiring thermal protection.

**Motor Specifications (from tbl_TruckTypes):**

```
tkn_TimeStepCalculations.MaxMotorPowerKw_Continuous = tbl_TruckTypes[tkn_TimeStepCalculations.RowIndex].MaxMotorPowerKw_Continuous
tkn_TimeStepCalculations.MaxMotorPowerKw_Peak = tbl_TruckTypes[tkn_TimeStepCalculations.RowIndex].MaxMotorPowerKw_Peak
tkn_TimeStepCalculations.MaxMotorPeakDurationSec = tbl_TruckTypes[tkn_TimeStepCalculations.RowIndex].MaxMotorPeakDurationSec
```

**Example Values (CAT 793F AC):**
- Continuous: 1,950 kW (indefinite)
- Peak: 2,730 kW (60 seconds max)
- Available from diesel+trolley: Up to 6,600 kW (1,950 + 4,650)

#### 2.3.1 Estimate Motor Electrical Demand (Based on Previous TimeStep)

Use previous timestep's tractive force and speed to estimate current motor demand:

```
tkn_TimeStepCalculations.MotorMechanicalPowerKw = Math.If(
    tkn_TimeStepCalculations.CurrentSpeedKmh > 0,
    (tkn_TimeStepCalculations.TractiveForceN / 1000) * (tkn_TimeStepCalculations.CurrentSpeedKmh / 3600),
    0
)

tkn_TimeStepCalculations.MotorElectricalDemandKw = Math.If(
    tkn_TimeStepCalculations.MotorMechanicalPowerKw > 0,
    tkn_TimeStepCalculations.MotorMechanicalPowerKw / (tkn_TimeStepCalculations.MotorEfficiencyPct / 100),
    0
)

tkn_TimeStepCalculations.CurrentPowerRatio = Math.If(
    tkn_TimeStepCalculations.MaxMotorPowerKw_Continuous > 0,
    tkn_TimeStepCalculations.MotorElectricalDemandKw / tkn_TimeStepCalculations.MaxMotorPowerKw_Continuous,
    0
)
```

**Note:** This uses previous timestep's `TractiveForceN` and current `CurrentSpeedKmh` to estimate demand before calculating new speed.

#### 2.3.2 Update Motor Thermal State

**Thermal Accumulation During Peak Mode:**

```
IF (var_MotorPeakModeActive == True):
    tkn_TimeStepCalculations.ThermalAccumulationRatePerSec = 100 / tkn_TimeStepCalculations.MaxMotorPeakDurationSec
    
    var_MotorThermalStatePct = var_MotorThermalStatePct + (
        tkn_TimeStepCalculations.ThermalAccumulationRatePerSec * prop_TimeStepSeconds * 3600
    )
ELSE:
    // Cooling rates based on power ratio (see design/concept/03-power-flow.md Table 3)
    IF (tkn_TimeStepCalculations.CurrentPowerRatio > 1.0):
        tkn_TimeStepCalculations.CoolingRatePerSec = -0.3       // Overload: heating
    ELSE IF (tkn_TimeStepCalculations.CurrentPowerRatio >= 0.95):
        tkn_TimeStepCalculations.CoolingRatePerSec = 0.03       // Near continuous: very slow cooling
    ELSE IF (tkn_TimeStepCalculations.CurrentPowerRatio >= 0.8):
        tkn_TimeStepCalculations.CoolingRatePerSec = 0.15       // High load: slow cooling
    ELSE IF (tkn_TimeStepCalculations.CurrentPowerRatio >= 0.5):
        tkn_TimeStepCalculations.CoolingRatePerSec = 0.4        // Medium load: moderate cooling
    ELSE IF (tkn_TimeStepCalculations.CurrentPowerRatio >= 0):
        tkn_TimeStepCalculations.CoolingRatePerSec = 0.8        // Light load: fast cooling
    ELSE:
        tkn_TimeStepCalculations.CoolingRatePerSec = 1.2        // Regenerating: very fast cooling
    END IF
    
    var_MotorThermalStatePct = var_MotorThermalStatePct - (
        tkn_TimeStepCalculations.CoolingRatePerSec * prop_TimeStepSeconds * 3600
    )
END IF

// Enforce limits [0-100%]
var_MotorThermalStatePct = Math.Max(0, Math.Min(100, var_MotorThermalStatePct))
```

**Note:** `prop_TimeStepSeconds` is in hours, multiply by 3600 to convert to seconds for %/sec rates.

#### 2.3.3 Determine Motor Power Limit Based on Thermal State

```
tkn_TimeStepCalculations.CanUsePeakMode = (var_MotorThermalStatePct < 80)
tkn_TimeStepCalculations.MustStopPeakMode = (var_MotorThermalStatePct >= 100)

IF (tkn_TimeStepCalculations.MotorElectricalDemandKw > tkn_TimeStepCalculations.MaxMotorPowerKw_Continuous):
    // Demand exceeds continuous rating - need peak mode
    IF (tkn_TimeStepCalculations.CanUsePeakMode == True AND tkn_TimeStepCalculations.MustStopPeakMode == False):
        // Activate or maintain peak mode
        IF (var_MotorPeakModeActive == False):
            var_MotorPeakModeStartTime = TimeNow
            var_MotorPeakModeActive = True
        END IF
        tkn_TimeStepCalculations.MotorPowerLimitKw = tkn_TimeStepCalculations.MaxMotorPowerKw_Peak
    ELSE:
        // Cannot use peak - too hot or timeout
        var_MotorPeakModeActive = False
        tkn_TimeStepCalculations.MotorPowerLimitKw = tkn_TimeStepCalculations.MaxMotorPowerKw_Continuous
    END IF
ELSE:
    // Within continuous rating - motor can cool
    var_MotorPeakModeActive = False
    tkn_TimeStepCalculations.MotorPowerLimitKw = tkn_TimeStepCalculations.MaxMotorPowerKw_Continuous
END IF
```

**Impact on SustainSpeed Mode:**

| Thermal State | Motor Limit | Diesel+Trolley Available | Effective Power | Result                       |
| ------------- | ----------- | ------------------------ | --------------- | ---------------------------- |
| 0-50% (cool)  | 2,730 kW    | 6,600 kW                 | 2,730 kW        | Peak mode enabled            |
| 50-80% (warm) | 2,730 kW    | 6,600 kW                 | 2,730 kW        | Peak mode reducing           |
| 80-100% (hot) | 1,950 kW    | 6,600 kW                 | 1,950 kW        | Forced to continuous         |
| 100% (limit)  | 1,950 kW    | 6,600 kW                 | 1,950 kW        | Thermal protection triggered |

**Note:** Without thermal management, the calculation would use full 6,600 kW, causing unrealistic motor overload.

### 2.4 Combined Power and Power-Limited Force (SustainSpeed Mode)

In SustainSpeed mode on trolley path, diesel and trolley power combine. Trolley power is dynamically calculated based on section capacity and active truck count (see Section 1.4). The combined power is then limited by motor thermal constraints (see Section 2.3):

```
// Calculate raw electrical power available (diesel + trolley)
tkn_TimeStepCalculations.TotalAvailablePowerKw = Math.If(
    tkn_TimeStepCalculations.OnTrolleyPath,
    tkn_TimeStepCalculations.DieselGeneratorMaxPowerKw + tkn_TimeStepCalculations.TrolleyAvailablePowerKw,
    tkn_TimeStepCalculations.DieselGeneratorMaxPowerKw
)

// Apply motor thermal limit (from Section 2.3.3)
tkn_TimeStepCalculations.TotalAvailablePowerKw = Math.Min(
    tkn_TimeStepCalculations.TotalAvailablePowerKw,
    tkn_TimeStepCalculations.MotorPowerLimitKw
)
```

Calculate power-limited force based on combined power and current speed using the relationship P = F × v:

```
tkn_TimeStepCalculations.PowerLimitForceN = Math.If(
    tkn_TimeStepCalculations.CurrentSpeedKmh > 0,
    tkn_TimeStepCalculations.TotalAvailablePowerKw * 1000 * (tkn_TimeStepCalculations.MotorEfficiencyPct / 100) / (tkn_TimeStepCalculations.CurrentSpeedKmh / 3600),
    tkn_TimeStepCalculations.BaseRimpullForceN  // At zero speed, power limit is infinite; use curve limit
)
```

### 2.5 Curve-Limited Force (Power and Rimpull Constraints)

The available tractive force is limited by both the rimpull curve and the power-speed relationship:

```
tkn_TimeStepCalculations.CurveLimitForceN = Math.Min(
    tkn_TimeStepCalculations.BaseRimpullForceN,
    tkn_TimeStepCalculations.PowerLimitForceN
)
```

### 2.6 Tractive Force (Dead Band Control)

Apply ±3000 m/hr (≈3 km/h) dead band with power degradation factor (always 1.0 for DieselElectric):

```
tkn_TimeStepCalculations.TractiveForceN = Math.If(
    tkn_TimeStepCalculations.CurrentSpeedKmh < tkn_TimeStepCalculations.TargetSpeedKmh - 3000,
    tkn_TimeStepCalculations.CurveLimitForceN * tkn_TimeStepCalculations.PowerDegradationFactor,
    Math.If(
        tkn_TimeStepCalculations.CurrentSpeedKmh > tkn_TimeStepCalculations.TargetSpeedKmh + 3000,
        -tkn_TimeStepCalculations.BaseRetardForceN * tkn_TimeStepCalculations.PowerDegradationFactor,
        0
    )
)
```

### 2.7 Acceleration

```
tkn_TimeStepCalculations.NetTractiveForceN = tkn_TimeStepCalculations.TractiveForceN - tkn_TimeStepCalculations.TotalResistanceN
tkn_TimeStepCalculations.AccelerationMs2 = tkn_TimeStepCalculations.NetTractiveForceN / tkn_TimeStepCalculations.CurrentWeightKg
```

### 2.8 New Speed

```
tkn_TimeStepCalculations.NewSpeedKmh = Math.Max(
    0,
    Math.Min(
        tkn_TimeStepCalculations.TargetSpeedKmh,
        tkn_TimeStepCalculations.CurrentSpeedKmh + tkn_TimeStepCalculations.AccelerationMs2 * 3600 * prop_TimeStepSeconds * 3600
    )
)
```

### 2.9 Visual Symbol Update

Update truck visual symbol based on trolley path status:

```
var_CurrentSymbolIndex = Math.If(
    tkn_TimeStepCalculations.OnTrolleyPath,
    List.list_CurrentSymbolIndex.DieselElectricTrayDownPantographUp,
    List.list_CurrentSymbolIndex.DieselElectricTrayDownPantographDown
)
```

### 2.10 Write Speed Update

```
Movement.Rate = tkn_TimeStepCalculations.NewSpeedKmh with Units="Kilometers per Hour"
```

---

## Section 3: Fuel Power Calculations (Fuel Updates Step)

Executed when `var_FuelUpdates == True`

> **Implementation Status:** The FuelUpdates step is currently empty in the XML. This section documents the intended design per `design/concept/03-power-flow.md` and `design/concept/05-fuel-systems.md`.

### 3.1 Re-read State

```
tkn_TimeStepCalculations.RowIndex = tbl_TruckTypes.TruckType.RowForKey(String.FromList(list_TruckTypes, prop_TruckType))
tkn_TimeStepCalculations.AuxiliaryPowerDemandKw = tbl_TruckTypes[tkn_TimeStepCalculations.RowIndex].AuxiliaryPowerDemandKw
tkn_TimeStepCalculations.MotorEfficiencyPct = tbl_TruckTypes[tkn_TimeStepCalculations.RowIndex].MotorEfficiencyPct
tkn_TimeStepCalculations.DieselFuelConsumptionRateLKwh = tbl_TruckTypes[tkn_TimeStepCalculations.RowIndex].DieselFuelConsumptionRateLKwh
tkn_TimeStepCalculations.RefuelDieselLevelPct = tbl_TruckTypes[tkn_TimeStepCalculations.RowIndex].RefuelDieselLevelPct
tkn_TimeStepCalculations.DieselTankCapacityL = tbl_TruckTypes[tkn_TimeStepCalculations.RowIndex].DieselTankCapacityL
tkn_TimeStepCalculations.DieselGeneratorMaxPowerKw = tbl_TruckTypes[tkn_TimeStepCalculations.RowIndex].DieselGeneratorMaxPowerKw
tkn_TimeStepCalculations.OnTrolleyPath = Location.Parent.Object.Is.obj_ElectricPath && Location.Parent.obj_ElectricPath.prop_TrolleyAssistEnabled
```

### 3.2 Power Source Allocation (SustainSpeed Mode)

> **Reference:** `design/concept/03-power-flow.md` - DieselElectric + SustainSpeed: Diesel at full power, trolley supplements

In SustainSpeed mode, diesel runs at maximum output and trolley supplements to provide additional power beyond diesel capacity. This combined power enables higher tractive force via P=F×v.

```
// Motor electrical demand (motor only, before auxiliaries)
tkn_TimeStepCalculations.MotorElectricalDemandKw = Math.If(
    tkn_TimeStepCalculations.MotorMechanicalPowerKw > 0,
    tkn_TimeStepCalculations.MotorMechanicalPowerKw / (tkn_TimeStepCalculations.MotorEfficiencyPct / 100),
    0
)

// Total driving demand (motor + auxiliaries)
tkn_TimeStepCalculations.ActualDrivingDemandKw = tkn_TimeStepCalculations.MotorElectricalDemandKw + tkn_TimeStepCalculations.AuxiliaryPowerDemandKw

// Diesel always runs at full load in SustainSpeed mode (on or off trolley)
tkn_TimeStepCalculations.DieselPowerKw = Math.Min(
    tkn_TimeStepCalculations.ActualDrivingDemandKw,
    tkn_TimeStepCalculations.DieselGeneratorMaxPowerKw
)

// Diesel contribution = actual diesel power used
tkn_TimeStepCalculations.DieselContributionKw = tkn_TimeStepCalculations.DieselPowerKw

// Trolley provides additional power beyond diesel capacity when on electrified path
tkn_TimeStepCalculations.TrolleyDrivingPowerKw = Math.If(
    tkn_TimeStepCalculations.OnTrolleyPath,
    Math.Min(
        Math.Max(0, tkn_TimeStepCalculations.ActualDrivingDemandKw - tkn_TimeStepCalculations.DieselPowerKw),
        tkn_TimeStepCalculations.TrolleyAvailablePowerKw
    ),
    0
)

// Trolley contribution = actual trolley power used
tkn_TimeStepCalculations.TrolleyContributionKw = tkn_TimeStepCalculations.TrolleyDrivingPowerKw
```

**Power Allocation Logic:**

| Scenario                        | Diesel Contribution | Trolley Contribution            | Total Power       |
| ------------------------------- | ------------------- | ------------------------------- | ----------------- |
| Off trolley, low demand         | 1.5 MW (demand)     | 0 MW                            | 1.5 MW            |
| Off trolley, high demand        | 1.95 MW (max)       | 0 MW                            | 1.95 MW           |
| On trolley, demand < diesel max | 1.5 MW (demand)     | 0 MW                            | 1.5 MW            |
| On trolley, demand > diesel max | 1.95 MW (max)       | Demand - 1.95 MW (up to 4.65MW) | Up to 6.6 MW      |
| On trolley, full acceleration   | 1.95 MW (max)       | 4.65 MW (trolley available)     | 6.6 MW (combined) |

**Note:** Unlike PreserveEnergy mode where trolley *replaces* diesel, SustainSpeed mode has diesel + trolley *combine* for maximum power output.

### 3.3 Diesel Consumption

Calculate diesel consumed based on actual diesel power used.

**Note:** `prop_TimeStepSeconds` is internally stored in hours in Simio:

```
tkn_TimeStepCalculations.DieselConsumedL = tkn_TimeStepCalculations.DieselPowerKw * prop_TimeStepSeconds * tkn_TimeStepCalculations.DieselFuelConsumptionRateLKwh
```

**Example:** Diesel at 1950 kW for 1 second (0.0002778 hours) with 0.11 L/kWh consumption:
- DieselConsumedL = 1950 × 0.0002778 × 0.11 = 0.0596 liters

### 3.4 Update Fuel State

Update diesel fuel level and check for refuel condition:

```
tkn_TimeStepCalculations.NewDieselLevelL = Math.Max(
    0,
    var_DieselLevelL - tkn_TimeStepCalculations.DieselConsumedL
)

tkn_TimeStepCalculations.RefuelThresholdL = tkn_TimeStepCalculations.DieselTankCapacityL * tkn_TimeStepCalculations.RefuelDieselLevelPct / 100

var_SwapRefuelChargeFlag = Math.If(
    tkn_TimeStepCalculations.NewDieselLevelL < tkn_TimeStepCalculations.RefuelThresholdL,
    True,
    False
)

var_DieselLevelL = tkn_TimeStepCalculations.NewDieselLevelL
var_DieselLevelPct = 100 * tkn_TimeStepCalculations.NewDieselLevelL / tkn_TimeStepCalculations.DieselTankCapacityL
var_DieselConsumedL = var_DieselConsumedL + tkn_TimeStepCalculations.DieselConsumedL
```

---

## Process Flow

1. **Decide: var_SpeedUpdates**
   - If True → Execute Speed Updates Step
   - If False → Skip to Fuel Updates check

2. **Decide: var_FuelUpdates**
   - If True → Execute Fuel Updates Step
   - If False → End process

This allows independent control of speed physics vs fuel/energy calculations.

---

## Implementation Notes

**What's Implemented:**
- Speed physics calculations (Section 2): Force limits, acceleration, power-speed relationship
- Trolley power sharing (Model B): Dynamic capacity distribution based on active truck count
- Visual symbol updates: Pantograph up/down based on trolley path status
- CurveLimitForceN: Uses Math.Min correctly (runtime verified)

**What's Pending:**
- Motor thermal management (Section 2.3): State variables exist, calculation logic needs ~20 XML assigns
  - ⚠️ **Risk**: Without thermal limits, motor can exceed peak rating (6.6 MW available vs 2.73 MW peak)
  - ✅ State variables available: var_MotorThermalStatePct, var_MotorPeakModeActive, var_MotorPeakModeStartTime (in obj_BatteryElectricTruck)
  - ❌ Missing: Calculation logic for thermal accumulation, cooling rates, power limit enforcement (~20 assigns, see Section 2.3)
  - **Effort**: 1-2 hours implementation + 1-2 hours testing
- Fuel calculations (Section 3): FuelUpdates step is empty
  - Missing: Diesel consumption, trolley power allocation, fuel level tracking
  - Missing: var_DieselEnergyConsumedKwh cumulative tracking

**Key Behaviors:**
- **SustainSpeed Mode**: Diesel + trolley power combine (additive) for maximum performance
- **Diesel Always Full Load**: Runs at max rated power (1.95 MW) whenever demand exists
- **Trolley Supplements**: Adds power beyond diesel capacity (up to 4.65 MW per truck)
- **No Fuel Savings**: Diesel consumption is maximum - trolley enables higher speeds, not efficiency
- **Speed Increase**: 1.3-1.78x improvement on steep grades vs diesel-only

---

## Notes

### Physics Calculations
- **Power-Limited Force**: Force = P / v, decreases as speed increases
- **Zero Speed Handling**: At v=0, power limit infinite; use BaseRimpullForceN instead
- **Dead Band Control**: ±3 km/h tolerance prevents oscillation around target speed
- **No Power Degradation**: DieselElectric trucks have PowerDegradationFactor = 1.0 (constant)

### Trolley System
- **Dynamic Power Sharing**: Capacity = min(section_capacity / active_trucks, pantograph_limit) × efficiency
- **Electric Path Detection**: `Location.Parent.Object.Is.obj_ElectricPath && prop_TrolleyAssistEnabled`
- **Typical Capacity**: 10 MW section → 5 MW per truck (2 trucks), 93% efficiency → 4.65 MW

### Simio Unit Conversions
- Speed: Stored as m/hr internally, displayed with `Units="Kilometers per Hour"`
- Acceleration to speed: `m/s² × 3600 × prop_TimeStepSeconds × 3600`
- Power to force: `kW × 1000 × efficiency / (km/h / 3600)` → Newtons
- Fuel consumption: `kW × hours × L/kWh` (prop_TimeStepSeconds is in hours)
- Thermal rates: `%/sec × prop_TimeStepSeconds × 3600` (hours → seconds)
