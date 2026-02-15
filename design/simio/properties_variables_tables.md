# Simio Properties, Variables, and Tables Reference

**Version:** 1.2  
**Last Updated:** December 1, 2025  
**Status:** Current Implementation

---

## Overview

This document catalogs all properties, state variables, token variables, and table parameters currently implemented in the Simio model for the electric truck fleet simulation.

**Objects Documented:**
- `obj_BatteryElectricTruck` - Main truck agent
- `obj_Battery` - Battery entity
- `obj_ElectricPath` - Trolley-assisted path
- `obj_BatterySwapChargeStation` - Battery swap facility

---

## 1. obj_BatteryElectricTruck

### 1.1 Properties

| Property Name                      | Type                  | Description                                                 | Default/Source                                          |
| ---------------------------------- | --------------------- | ----------------------------------------------------------- | ------------------------------------------------------- |
| `prop_TruckType`                   | List                  | Truck model selection from `list_TruckTypes`                | `tbl_BatteryElectricTrucks.TruckType`                   |
| `prop_TimeStepSeconds`             | Real                  | Physics update interval in seconds (recommended 1.0)        | 1 second                                                |
| `prop_AveragePayload`              | Real                  | Average payload weight in kg when loaded                    | `tbl_BatteryElectricTrucks.AveragePayload`              |
| `prop_PayloadDistribution`         | Expression            | Statistical distribution for payload variation              | `tbl_BatteryElectricTrucks.PayloadDistribution`         |
| `prop_BatteryEntityReference`      | DynamicObjectInstance | Reference to battery entity object definition               | `tbl_BatteryElectricTrucks.BatteryEntityReference`      |
| `prop_PowerDegradationActive`      | Boolean               | Enable/disable power degradation as battery health declines | `tbl_BatteryElectricTrucks.PowerDegradationActive`      |
| `prop_ElectricAssistMode`          | List                  | Electric assist mode from `list_ElectricAssistMode`         | `tbl_BatteryElectricTrucks.ElectricAssistMode`          |
| `prop_InitialSwapRefuelChargeNode` | Node                  | Initial assignment of swap/refuel/charge station node       | `tbl_BatteryElectricTrucks.InitialSwapRefuelChargeNode` |

**Lists Referenced:**
- `list_TruckTypes`: "TONLY_DTE145_BatterySwap", "CAT_793F_AC_DieselElectric", "CAT_794_AC_DieselElectric", "Liebherr_T236_DieselElectric", "Liebherr_T264_DieselElectric", "Liebherr_T264_BE_BatteryElectric"
- `list_TruckMode`: "BatterySwap", "DieselElectric", "BatteryElectric"
- `list_ElectricAssistMode`: "PreserveEnergy", "SustainSpeed"
- `list_CurrentSymbolIndex`: Visual symbols for different truck states/modes

### 1.2 State Variables

| Variable Name                      | Type             | Description                                               |
| ---------------------------------- | ---------------- | --------------------------------------------------------- |
| `var_CurrentSymbolIndex`           | List             | Current visual symbol index (truck tray/pantograph state) |
| `var_Loaded`                       | Boolean          | True when truck is loaded with payload, False when empty  |
| `var_Payload`                      | Discrete         | Current payload weight in kg                              |
| `var_BatteryIndex`                 | Integer          | Battery instance index (used during initialization)       |
| `var_SpeedUpdates`                 | Boolean          | Flag to enable/disable speed physics updates              |
| `var_BatteryUpdates`               | Boolean          | Flag to enable/disable battery SOC/health updates         |
| `var_FuelUpdates`                  | Boolean          | Flag to enable/disable fuel consumption updates           |
| `var_CurrentGrade`                 | Discrete         | Current path grade (%)                                    |
| `var_CurrentSpeedKmh`              | Discrete         | Current truck speed (km/h)                                |
| `var_DieselLevelL`                 | Discrete         | Current diesel fuel level (liters)                        |
| `var_DieselLevelPct`               | Discrete         | Current diesel fuel level (%)                             |
| `var_DieselEnergyConsumedKwh`      | Discrete         | Cumulative diesel energy consumed (kWh)                   |
| `var_DieselConsumedL`              | Discrete         | Cumulative diesel fuel consumed (liters)                  |
| `var_DieselEnergyPreservedKwh`     | Discrete         | Diesel energy saved by trolley assist (kWh)               |
| `var_DieselPreservedL`             | Discrete         | Diesel fuel saved by trolley assist (liters)              |
| `var_SwapRefuelChargeFlag`         | Boolean          | True when service needed (swap/refuel/charge)             |
| `var_SwapRefuelChargeNode`         | ElementReference | Assigned service station node for this truck              |
| `var_ManualControlDestinationNode` | ElementReference | Current target destination node                           |
| `var_Debug`                        | Boolean          | Debug flag for development/troubleshooting                |

### 1.3 Token Variables (tkn_TimeStepCalculations)

**Truck Specifications:**
| Variable Name            | Type     | Description                                 |
| ------------------------ | -------- | ------------------------------------------- |
| `EmptyWeightKg`          | Discrete | Truck empty weight (kg)                     |
| `CurrentWeightKg`        | Discrete | Current total weight (empty + payload, kg)  |
| `MaxSpeedKmh_Loaded`     | Discrete | Maximum speed when loaded (km/h)            |
| `MaxSpeedKmh_Empty`      | Discrete | Maximum speed when empty (km/h)             |
| `RollingResistance`      | Discrete | Rolling resistance coefficient              |
| `MotorEfficiencyPct`     | Discrete | Motor efficiency (%)                        |
| `RegenEfficiencyPct`     | Discrete | Regenerative braking efficiency (%)         |
| `AuxiliaryPowerDemandKw` | Discrete | Auxiliary power demand (HVAC, controls, kW) |

**Performance Curves:**
| Variable Name       | Type     | Description                         |
| ------------------- | -------- | ----------------------------------- |
| `BaseRimpullForceN` | Discrete | Base rimpull force from curve (N)   |
| `BaseRetardForceN`  | Discrete | Base retarding force from curve (N) |
| `RowIndex`          | Integer  | Current row index for curve lookup  |

**Battery Parameters:**
| Variable Name                    | Type     | Description                                                |
| -------------------------------- | -------- | ---------------------------------------------------------- |
| `BatteryHealthPct`               | Discrete | Current battery health (100-80%)                           |
| `RatedBatteryStorageEnergyKwh`   | Discrete | Nominal battery capacity (kWh)                             |
| `EndOfLifeBatteryHealthPct`      | Discrete | End-of-life threshold (typically 80%)                      |
| `CurrentBatterySOCPct`           | Discrete | Current state of charge (%)                                |
| `MaxBatteryPowerKw`              | Discrete | Maximum battery discharge power from `tbl_TruckTypes` (kW) |
| `SwapBatterySOCPct`              | Discrete | SOC threshold for battery swap (%)                         |
| `RatedLifetimeThroughputKwh`     | Discrete | Total lifetime energy throughput (kWh)                     |
| `CurrentCumulativeThroughputKwh` | Discrete | Accumulated energy cycled (kWh)                            |
| `NewCumulativeThroughputKwh`     | Discrete | Updated cumulative throughput (kWh)                        |
| `AbsoluteEnergyThroughputKwh`    | Discrete | Absolute energy this timestep (kWh)                        |
| `NewBatteryHealthPct`            | Discrete | Updated battery health (%)                                 |

**Diesel Parameters:**
| Variable Name                   | Type     | Description                                   |
| ------------------------------- | -------- | --------------------------------------------- |
| `DieselFuelConsumptionRateLKwh` | Discrete | Fuel consumption rate (L/kWh, typically 0.11) |
| `DieselTankCapacityL`           | Discrete | Diesel tank capacity (liters)                 |
| `InitialDieselLevelL`           | Discrete | Initial diesel level (liters)                 |
| `DieselGeneratorMaxPowerKw`     | Discrete | Diesel generator max power (kW)               |
| `DieselGeneratorEfficiencyPct`  | Discrete | Diesel generator efficiency (%)               |
| `RefuelDieselLevelPct`          | Discrete | Refuel trigger threshold (%)                  |
| `RefuelThresholdL`              | Discrete | Refuel trigger in liters                      |
| `DieselConsumedL`               | Discrete | Diesel consumed this timestep (L)             |
| `NewDieselLevelL`               | Discrete | Updated diesel level (L)                      |

**Motor Thermal Parameters:**
| Variable Name                | Type     | Description                                        |
| ---------------------------- | -------- | -------------------------------------------------- |
| `MaxMotorPowerKw_Continuous` | Discrete | Motor continuous power rating (kW)                 |
| `MaxMotorPowerKw_Peak`       | Discrete | Motor peak power rating for short duration (kW)    |
| `MaxMotorPeakDurationSec`    | Discrete | Maximum duration for peak mode (seconds, typ. 60s) |

**Trolley Parameters:**
| Variable Name                  | Type     | Description                                               |
| ------------------------------ | -------- | --------------------------------------------------------- |
| `OnTrolleyPath`                | Boolean  | True when on obj_ElectricPath with trolley assist enabled |
| `TrolleyAssistEnabled`         | Boolean  | Trolley assist available on current path                  |
| `TrolleyEfficiencyPct`         | Discrete | Trolley efficiency (%) - from path property               |
| `TrolleyActiveTrucksOnSection` | Discrete | Number of trucks on section (from path.NumberTravelers)   |

**Trolley Power Sharing (Dynamic - from path properties):**
| Variable Name                  | Type     | Description                                                           |
| ------------------------------ | -------- | --------------------------------------------------------------------- |
| `TrolleySectionTotalPowerKw`   | Discrete | Total substation capacity for section (kW) - from path property       |
| `TrolleyMaxPowerPerTruckKw`    | Discrete | Maximum pantograph rating per truck (kW) - from path property         |
| `TrolleySharedPowerPerTruckKw` | Discrete | Section total / active truck count (kW) - calculated                  |
| `TrolleyAvailablePowerKw`      | Discrete | min(shared, pantograph) × efficiency (kW) - actual available to truck |

**Trolley Power Usage:**
| Variable Name            | Type     | Description                                              |
| ------------------------ | -------- | -------------------------------------------------------- |
| `TrolleyPowerKw`         | Discrete | Total trolley power used this timestep (kW)              |
| `TrolleyContributionKw`  | Discrete | Trolley's share of driving power (kW)                    |
| `TrolleyChargingPowerKw` | Discrete | Trolley power for charging battery (kW)                  |
| `TotalAvailablePowerKw`  | Discrete | Combined power from all sources (battery/diesel/trolley) |

**Diesel/Fuel Calculations (DieselElectric mode):**
| Variable Name           | Type     | Description                                   |
| ----------------------- | -------- | --------------------------------------------- |
| `CurrentDieselLevelPct` | Discrete | Current diesel tank level (%)                 |
| `RefuelRateLPerMin`     | Discrete | Refueling flow rate (L/min)                   |
| `FuelAddedL`            | Discrete | Fuel added this timestep during refueling (L) |
| `TotalDemandKw`         | Discrete | Total power demand (motor + auxiliaries, kW)  |

**Speed & Force Calculations:**
| Variable Name             | Type     | Description                                     |
| ------------------------- | -------- | ----------------------------------------------- |
| `CurrentSpeedKmh`         | Discrete | Current speed (km/h)                            |
| `CurrentGrade`            | Discrete | Current path grade (%)                          |
| `MaxSpeedKmh`             | Discrete | Applicable max speed (km/h)                     |
| `PathSpeedLimitKmh`       | Discrete | Path speed limit (km/h)                         |
| `TargetSpeedKmh`          | Discrete | Target speed (min of path and truck max, km/h)  |
| `PowerDegradationFactor`  | Discrete | Power reduction due to battery health (0.8-1.0) |
| `GradeResistanceForceN`   | Discrete | Grade resistance force (N)                      |
| `RollingResistanceForceN` | Discrete | Rolling resistance force (N)                    |
| `TotalResistanceN`        | Discrete | Total resistance force (N)                      |
| `CurveLimitForceN`        | Discrete | Curve-limited tractive force (N)                |
| `TotalAvailablePowerKw`   | Discrete | Total available power (battery + trolley, kW)   |
| `PowerLimitForceN`        | Discrete | Power-limited tractive force (N)                |
| `TractiveForceN`          | Discrete | Actual tractive force applied (N)               |
| `NetTractiveForceN`       | Discrete | Net force (tractive - resistance, N)            |
| `AccelerationMs2`         | Discrete | Acceleration (m/s²)                             |
| `NewSpeedKmh`             | Discrete | Updated speed (km/h)                            |

**Traction Limit Calculations:**
| Variable Name           | Type     | Description                                                   |
| ----------------------- | -------- | ------------------------------------------------------------- |
| `GradeAngleRad`         | Discrete | Grade angle in radians: ATAN(CurrentGrade / 100)              |
| `NormalForceN`          | Discrete | Normal force perpendicular to surface: m × g × cos(θ) (N)     |
| `TractionLimitN`        | Discrete | Maximum traction force before wheel slip: μ × NormalForce (N) |
| `TractionLimitedForceN` | Discrete | Tractive force after applying traction limit (N)              |
| `TractionLimitActive`   | Discrete | True (1) when force was limited by traction (for diagnostics) |

**Power Flow Calculations:**
| Variable Name                 | Type     | Description                                                 |
| ----------------------------- | -------- | ----------------------------------------------------------- |
| `MotorMechanicalPowerKw`      | Discrete | Motor mechanical power output (kW)                          |
| `ActualDrivingDemandKw`       | Discrete | Total driving power demand (motor + auxiliary, kW)          |
| `BaseDrivingDemandKw`         | Discrete | Baseline driving power demand (kW)                          |
| `TrolleyDrivingPowerKw`       | Discrete | Trolley power for driving (kW)                              |
| `TrolleyChargingPowerKw`      | Discrete | Trolley power for charging battery (kW)                     |
| `TrolleyContributionKw`       | Discrete | Trolley's share of power (kW)                               |
| `DieselPowerKw`               | Discrete | Diesel generator output (kW)                                |
| `DieselContributionKw`        | Discrete | Diesel's share of power (kW)                                |
| `MotorMechanicalPowerKw`      | Discrete | Motor mechanical output power (kW)                          |
| `DieselEnergyPreservedKwh`    | Discrete | Diesel energy saved this timestep (kWh)                     |
| `SurplusPowerKw`              | Discrete | Excess trolley power available (kW)                         |
| `PowerToFullChargeKw`         | Discrete | Power needed to reach 100% SOC (kW)                         |
| `NetBatteryPowerKw`           | Discrete | Net battery power (positive=discharge, negative=charge, kW) |
| `BatteryContributionKw`       | Discrete | Battery's share of power (kW)                               |
| `BatteryPowerKw`              | Discrete | Battery power (kW)                                          |
| `BatteryEnergyPreservedKwh`   | Discrete | Battery energy saved this timestep (kWh)                    |
| `EnergyDeltaKwh`              | Discrete | Battery energy change this timestep (kWh)                   |
| `EffectiveBatteryCapacityKwh` | Discrete | Effective capacity accounting for health (kWh)              |
| `NewBatterySOCPct`            | Discrete | Updated battery SOC (%)                                     |

**Motor Thermal Management:**
| Variable Name                   | Type     | Description                                                |
| ------------------------------- | -------- | ---------------------------------------------------------- |
| `MotorElectricalDemandKw`       | Discrete | Motor electrical power demand before thermal limiting (kW) |
| `CurrentPowerRatio`             | Discrete | Current power / continuous rating (0-2+)                   |
| `ThermalAccumulationRatePerSec` | Discrete | Heating rate during peak mode (%/s)                        |
| `CoolingRatePerSec`             | Discrete | Cooling rate during normal operation (%/s)                 |
| `MotorPowerLimitKw`             | Discrete | Effective motor power limit after thermal limits (kW)      |
| `CanUsePeakMode`                | Boolean  | Whether motor can enter/maintain peak mode (thermal < 80%) |
| `MustStopPeakMode`              | Boolean  | Whether motor must exit peak mode (thermal >= 100%)        |

**Battery Charging (PreserveBattery mode):**
| Variable Name          | Type     | Description                                               |
| ---------------------- | -------- | --------------------------------------------------------- |
| `ExcessTrolleyPowerKw` | Discrete | Trolley power available after meeting driving demand (kW) |
| `BatteryChargePowerKw` | Discrete | Actual battery charging power from trolley (kW)           |
| `MaxChargeRateKw`      | Discrete | Maximum safe charge rate based on SOC and C-rate (kW)     |

**Cycle-Life Degradation (Per-Cycle Calculations):**
| Variable Name             | Type     | Description                                            |
| ------------------------- | -------- | ------------------------------------------------------ |
| `CycleDoD`                | Discrete | Depth of discharge this cycle (fraction 0-1)           |
| `AvgDischargeCRate`       | Discrete | Average discharge C-rate this cycle                    |
| `AvgChargeCRate`          | Discrete | Average charge C-rate this cycle                       |
| `ThetaDoD`                | Discrete | DoD degradation factor (θ_DoD)                         |
| `ThetaDischarge`          | Discrete | Discharge rate degradation factor (θ_i_dis)            |
| `ThetaCharge`             | Discrete | Charge rate degradation factor (θ_i_ch)                |
| `ThetaTemperature`        | Discrete | Temperature degradation factor (θ_T)                   |
| `CycleImpactFactor`       | Discrete | Combined cycle impact (θ_DoD × θ_i_dis × θ_i_ch × θ_T) |
| `EquivalentCycleFraction` | Discrete | Fraction of reference cycle this cycle represents      |

---

## 2. obj_Battery

### 2.1 Properties

No custom properties (uses default Entity properties).

### 2.2 State Variables

| Variable Name                        | Type             | Description                                                                                            |
| ------------------------------------ | ---------------- | ------------------------------------------------------------------------------------------------------ |
| `var_OriginalObjectReference`        | ElementReference | Original parent object that created this battery                                                       |
| `var_CurrentObjectReference`         | ElementReference | Current parent object holding this battery                                                             |
| `var_BatteryID`                      | String           | Unique battery identifier                                                                              |
| `var_BatteryType`                    | String           | Battery type key (e.g., "Lithium_Iron_Phosphate_801")                                                  |
| `var_RatedStorageEnergyKwh`          | Discrete         | Nominal battery capacity in kWh (e.g., 801)                                                            |
| `var_ReferenceLifeChargingCycles`    | Integer          | Reference lifetime charging cycles (e.g., 5000)                                                        |
| `var_RatedLifetimeThroughputKwh`     | Discrete         | Total lifetime energy throughput threshold (capacity × cycles)                                         |
| `var_EndOfLifeBatteryHealthPct`      | Discrete         | End-of-life capacity threshold percentage (typically 80%)                                              |
| `var_BatterySOCPct`                  | Discrete         | Current state of charge percentage (0-100%)                                                            |
| `var_BatteryCumulativeThroughputKwh` | Discrete         | Total energy cycled through battery (charge + discharge, kWh)                                          |
| `var_BatteryHealthPct`               | Discrete         | Current battery health percentage (100% new, degrades to EOL)                                          |
| `var_BatteryResourceState`           | List             | Current resource state (ReadyToDeploy, Deployed, ReadyToCharge, Charging, OutOfService)                |
| `var_ReferenceDOD`                   | Discrete         | Reference depth of discharge (from tbl_BatteryTypes)                                                   |
| `var_ReferenceDischargeCRate`        | Discrete         | Reference discharge C-rate (from tbl_BatteryTypes)                                                     |
| `var_ReferenceChargeCRate`           | Discrete         | Reference charge C-rate (from tbl_BatteryTypes)                                                        |
| `var_ReferenceTemperatureK`          | Discrete         | Reference temperature in Kelvin (from tbl_BatteryTypes)                                                |
| `var_OperatingTemperatureK`          | Discrete         | Operating temperature in Kelvin (from tbl_BatteryTypes)                                                |
| `var_CycleLife_Xi`                   | Discrete         | DoD exponent ξ (from tbl_BatteryTypes)                                                                 |
| `var_CycleLife_Gamma1`               | Discrete         | Discharge rate exponent γ₁ (from tbl_BatteryTypes)                                                     |
| `var_CycleLife_Gamma2`               | Discrete         | Charge rate exponent γ₂ (from tbl_BatteryTypes)                                                        |
| `var_CycleLife_Psi`                  | Discrete         | Temperature coefficient ψ (from tbl_BatteryTypes)                                                      |
| `var_CycleLife_Alpha`                | Discrete         | Temperature exponent α (from tbl_BatteryTypes)                                                         |
| `var_ChargingCycleCount`             | Integer          | Number of complete charging cycles experienced                                                         |
| `var_ChargeStartSOC`                 | Discrete         | SOC percentage when current charging cycle started                                                     |
| `var_ChargeStartTimeHrs`             | Discrete         | Simulation time when current charging cycle started (hours)                                            |
| `var_CurrentStateEntryTimeHrs`       | Discrete         | Simulation time when battery entered current resource state (hours)                                    |
| `var_TimeInCurrentStateHrs`          | Discrete         | Duration in current resource state (hours)                                                             |
| `var_BatteryStationEntryTimeHrs`     | Discrete         | Simulation time when battery entered current station (hours)                                           |
| `var_CurrentSymbolIndex`             | Integer          | Visual symbol index (0=green 80-100%, 1=yellow 60-79%, 2=orange 40-59%, 3=red 20-39%, 4=critical <20%) |

### 2.3 Tables

#### tbl_BatteryTypes

Central battery specification table (stored in obj_Battery, referenced by trucks and swap stations).

| Column                                  | Type       | Description                                   |
| --------------------------------------- | ---------- | --------------------------------------------- |
| `BatteryType`                           | List (key) | Battery model identifier                      |
| `RatedStorageEnergyKwh`                 | Real       | Nominal battery capacity (kWh)                |
| `RatedLifetimeThroughputKwh`            | Real       | Lifetime energy throughput threshold (kWh)    |
| `EndOfLifeBatteryHealthPct`             | Real       | End-of-life capacity threshold (%)            |
| `InitialBatterySOCPct`                  | Real       | Initial state of charge (%)                   |
| `InitialBatteryCumulativeThroughputKwh` | Real       | Initial cumulative throughput (kWh)           |
| `InitialBatteryHealthPct`               | Real       | Initial battery health (%)                    |
| `ReferenceLifeChargingCycles`           | Real       | Reference cycle count at reference conditions |
| `ReferenceDOD`                          | Real       | Reference depth of discharge (fraction)       |
| `ReferenceDischargeCRate`               | Real       | Reference discharge C-rate                    |
| `ReferenceChargeCRate`                  | Real       | Reference charge C-rate                       |
| `ReferenceTemperatureK`                 | Real       | Reference temperature (K)                     |
| `OperatingTemperatureK`                 | Real       | Typical operating temperature (K)             |
| `CycleLife_Xi`                          | Real       | DoD exponent (ξ)                              |
| `CycleLife_Gamma1`                      | Real       | Discharge rate exponent (γ₁)                  |
| `CycleLife_Gamma2`                      | Real       | Charge rate exponent (γ₂)                     |
| `CycleLife_Psi`                         | Real       | Temperature coefficient (ψ)                   |
| `CycleLife_Alpha`                       | Real       | Temperature exponent (α)                      |

**Lists Referenced:**
- `list_BatteryResourceState`: "ReadyToDeploy", "Deployed", "ReadyToCharge", "Charging", "OutOfService"
- `list_BatteryTypes`: "Lithium_Iron_Phosphate_801", "Lithium_Iron_Phosphate_1700"
- `list_CurrentSymbolIndex`: "Green", "Yellow", "Orange", "DarkOrange", "Red"

---

## 3. obj_ElectricPath

### 3.1 Properties

| Property Name                     | Type    | Description                                                             | Default/Source                   |
| --------------------------------- | ------- | ----------------------------------------------------------------------- | -------------------------------- |
| `prop_TrolleyAssistEnabled`       | Boolean | Enable/disable trolley assist for this path                             | `tbl_Paths.TrolleyAssistEnabled` |
| `prop_TrolleySectionTotalPowerKw` | Real    | Total substation/section capacity (kW) - shared among all active trucks | 0.0                              |
| `prop_TrolleyMaxPowerPerTruckKw`  | Real    | Maximum power per truck (kW) - pantograph/collector rating limit        | 0.0                              |
| `prop_TrolleyMaxConcurrentTrucks` | Integer | Maximum number of trucks simultaneously on section                      | 0                                |
| `prop_TrolleyVoltageV`            | Real    | Trolley system voltage (V) - for reference/validation                   | 0.0                              |
| `prop_TrolleyEfficiencyPct`       | Real    | Trolley power delivery efficiency (%)                                   | 0.0                              |
| `prop_RoadFrictionCoefficient`    | Real    | Surface friction coefficient μ for traction limits                      | 0.7 (dry compacted gravel)       |

### 3.2 State Variables

No custom state variables.

**Built-in Simio Properties Used:**
- `NumberTravelers` - Count of trucks currently on this path segment (used for power sharing)

---

## 4. obj_BatterySwapChargeStation

### 4.1 Properties

| Property Name                     | Type                  | Description                                                | Default/Source                                             |
| --------------------------------- | --------------------- | ---------------------------------------------------------- | ---------------------------------------------------------- |
| `prop_BatteryType`                | List                  | Battery model selection from `list_BatteryTypes`           | `tbl_BatterySwapChargeStations.BatteryType`                |
| `prop_TimeStepSeconds`            | Real                  | Charging update interval in seconds                        | 1 second                                                   |
| `prop_BatteryEntityReference`     | DynamicObjectInstance | Reference to battery entity object definition              | `tbl_BatterySwapChargeStations.BatteryEntityReference`     |
| `prop_InitialBatteryInventory`    | List                  | Number of batteries to create at initialization            | `tbl_BatterySwapChargeStations.InitialBatteryInventory`    |
| `prop_MaxConcurrentChargingPorts` | Integer               | Maximum number of batteries that can charge simultaneously | `tbl_BatterySwapChargeStations.MaxConcurrentChargingPorts` |
| `prop_ChargingPortMaxPowerKw`     | Real                  | Maximum power per charging port in kW (e.g., 200-500 kW)   | `tbl_BatterySwapChargeStations.ChargingPortMaxPowerKw`     |
| `prop_ChargingEfficiencyPct`      | Real                  | Charging efficiency percentage (e.g., 90%)                 | `tbl_BatterySwapChargeStations.ChargingEfficiencyPct`      |
| `prop_ChargeDegradationActive`    | Boolean               | Enable/disable battery degradation during charging         | `tbl_BatterySwapChargeStations.ChargeDegradationActive`    |

**Lists Referenced:**
- `list_BatteryTypes`: "Lithium_Iron_Phosphate_801"
- `list_InitialBatteryInventory`: "1", "2", "3", "4", "5", "6", "7", "8"

### 4.2 State Variables

| Variable Name                             | Type             | Description                                                             |
| ----------------------------------------- | ---------------- | ----------------------------------------------------------------------- |
| `var_BatteryIndex`                        | Integer          | Battery instance counter (used during initialization)                   |
| `var_BatteryUpdates`                      | Boolean          | Flag to enable/disable battery charging updates (default True)          |
| `var_CurrentSymbolIndex`                  | Integer          | Visual symbol index for station status                                  |
| `var_BatteryElectricTruckObjectReference` | ElementReference | Reference to truck object currently at station                          |
| `var_UnavailableFlag`                     | Boolean          | True when station is unavailable (e.g., during swap operation)          |
| `var_Debug`                               | Boolean          | Debug flag for development/troubleshooting                              |
| `var_ChargingPortsInUse`                  | Integer          | Current number of charging ports actively in use                        |
| `var_TotalEnergyDeliveredKwh`             | Discrete         | Cumulative energy delivered to all batteries (kWh)                      |
| `var_TotalBatteriesSwapped`               | Integer          | Total count of battery swap operations completed                        |
| `var_BatteriesReadyToDeploy`              | Integer          | Current count of fully charged batteries available for deployment       |
| `var_BatteriesReadyToCharge`              | Integer          | Current count of depleted batteries waiting for available charging port |
| `var_BatteriesCharging`                   | Integer          | Current count of batteries actively charging                            |

---

## 5. Key Tables Referenced

### 5.1 tbl_BatteryElectricTrucks

Primary configuration table for truck fleet. Columns include:
- `TruckType` - Truck model selection
- `AveragePayload` - Average payload weight
- `PayloadDistribution` - Payload variation distribution
- `BatteryEntityReference` - Battery object reference
- `PowerDegradationActive` - Enable power degradation
- `ElectricAssistMode` - Assist mode selection
- `InitialSwapRefuelChargeNode` - Initial service station assignment
- `InitialNode` - Starting node
- `InitialNumberInSystem` - Fleet size
- Various operating parameters and process assignments

### 5.2 tbl_Paths

Path configuration table. Columns include:
- `TrolleyAssistEnabled` - Enable trolley for path
- `LinkType` - Path type
- `SpeedLimit` - Path speed limit
- `AllowPassing` - Passing permission
- Other standard Simio path properties

### 5.3 tbl_BatterySwapChargeStations

Station configuration table. Columns include:
- `BatteryType` - Battery model
- `BatteryEntityReference` - Battery object reference
- `InitialBatteryInventory` - Initial battery count
- `MaxConcurrentChargingPorts` - Charging capacity
- `ChargingPortMaxPowerKw` - Charging power
- `ChargingEfficiencyPct` - Charging efficiency
- `ChargeDegradationActive` - Enable degradation
- `InitialNode` - Station location
- Process assignments

---

## Notes

**Variable Naming Conventions:**
- `prop_*` - Properties (configuration parameters)
- `var_*` - State variables (persistent truck/object state)
- `tkn_*` - Token variables (temporary process variables)
- `list_*` - String lists (enumerated values)
- `tbl_*` - Data tables (configuration data)

**Units:**
- Power: kW (kilowatts)
- Energy: kWh (kilowatt-hours)
- Force: N (newtons)
- Speed: km/h (kilometers per hour)
- Distance: m (meters)
- Weight: kg (kilograms)
- Time: seconds (unless specified)
- Volume: L (liters)
- Percentage: % (0-100)

---

## 6. Missing Variables - Gap Analysis

**Purpose:** This section identifies variables specified in the design concept documents (01-08) that are not yet implemented in the current Simio model.

**References:**
- [03-power-flow.md](../concept/03-power-flow.md) - Motor thermal management
- [04-battery-management.md](../concept/04-battery-management.md) - PreserveBattery charging logic
- [05-fuel-systems.md](../concept/05-fuel-systems.md) - Enhanced fuel tracking
- [06-infrastructure.md](../concept/06-infrastructure.md) - Infrastructure routing
- [08-degradation-models.md](../concept/08-degradation-models.md) - Advanced cycle-life degradation

---

### 6.1 Motor Thermal Management (✅ Implemented)

**Source:** [03-power-flow.md](../concept/03-power-flow.md#motor-thermal-management)

**Implemented Properties:**
| Property Name                     | Type | Description                                         | Default/Source                                | Status |
| --------------------------------- | ---- | --------------------------------------------------- | --------------------------------------------- | ------ |
| `prop_MaxMotorPowerKw_Continuous` | Real | Motor continuous rating (kW)                        | `tbl_TruckTypes.MaxMotorPowerKw_Continuous`   | ✅      |
| `prop_MaxMotorPowerKw_Peak`       | Real | Motor peak rating for short duration (kW)           | `tbl_TruckTypes.MaxMotorPowerKw_Peak`         | ✅      |
| `prop_MaxMotorPeakDurationSec`    | Real | Maximum peak mode duration before thermal limit (s) | `tbl_TruckTypes.MaxMotorPeakDurationSec` (60) | ✅      |

**Implemented State Variables:**
| Variable Name                | Type     | Description                                       | Initial Value | Status |
| ---------------------------- | -------- | ------------------------------------------------- | ------------- | ------ |
| `var_MotorThermalStatePct`   | Discrete | Motor thermal accumulation (0-100%)               | 0             | ✅      |
| `var_MotorPeakModeActive`    | Boolean  | True when motor operating above continuous rating | False         | ✅      |
| `var_MotorPeakModeStartTime` | Discrete | Simulation time when peak mode started (hours)    | 0             | ✅      |

**Required Token Variables:**
| Variable Name                   | Type     | Description                                                   |
| ------------------------------- | -------- | ------------------------------------------------------------- |
| `MotorElectricalDemandKw`       | Discrete | Motor electrical power demand before thermal limiting (kW)    |
| `CurrentPowerRatio`             | Discrete | Current power / continuous rating (0-2+)                      |
| `ThermalAccumulationRatePerSec` | Discrete | Heating rate during peak mode (%/s)                           |
| `CoolingRatePerSec`             | Discrete | Cooling rate during normal operation (%/s)                    |
| `MotorPowerLimitKw`             | Discrete | Effective motor power limit after thermal considerations (kW) |
| `CanUsePeakMode`                | Boolean  | Whether motor can enter/maintain peak mode (thermal < 80%)    |
| `MustStopPeakMode`              | Boolean  | Whether motor must exit peak mode (thermal >= 100%)           |

**Implementation Notes:**
- ✅ All variables implemented in Simio model
- 3-step process: Calculate power demand → Thermal accumulation/dissipation → Determine power limit
- Cooling rates: Very slow (0.1%/s) at 100% load → Very fast (1.5%/s) during regeneration
- Peak mode control: Use thermal state directly (< 80% to enter peak, >= 100% forced to continuous)
- Thermal state interpretation: 0-50% cool, 50-80% warm, 80-100% hot, 100% thermal limit
- No separate boolean flags needed - compare `var_MotorThermalStatePct` directly in logic
- **Note:** Variable named `var_MotorThermalStatePct` in model (abbreviated)

---

### 6.2 PreserveBattery Charging Logic (Partially Implemented)

**Source:** [04-battery-management.md](../concept/04-battery-management.md#mode-batteryelectric--preservebattery)

**Implemented Properties:**
| Property Name                  | Type | Description                                                 | Default/Source                           | Status |
| ------------------------------ | ---- | ----------------------------------------------------------- | ---------------------------------------- | ------ |
| `prop_MaxBatteryChargePowerKw` | Real | Maximum battery charge power (kW) - separate from discharge | `tbl_TruckTypes.MaxBatteryChargePowerKw` | ✅      |

**Required Token Variables:**
| Variable Name          | Type     | Description                                               |
| ---------------------- | -------- | --------------------------------------------------------- |
| `ExcessTrolleyPowerKw` | Discrete | Trolley power available after meeting driving demand (kW) |
| `BatteryChargePowerKw` | Discrete | Actual battery charging power from trolley (kW)           |
| `MaxChargeRateKw`      | Discrete | Maximum safe charge rate based on SOC and C-rate (kW)     |

**Implementation Notes:**
- Currently implemented: Basic trolley charging in PreserveBattery mode
- Missing: Safe charge rate limiting based on battery SOC and C-rate constraints
- Required logic: 3 scenarios (driving demand < trolley, driving demand = trolley, driving demand > trolley)
- **Note:** `MaxBatteryPowerKw` (discharge, from tbl_TruckTypes) and `MaxBatteryChargePowerKw` (charge, from tbl_TruckTypes) are different - charge power typically 10-20% of discharge power
- See 04-battery-management.md Step 6 for detailed calculation process
- **Note:** `MaxBatteryPowerKw` (discharge) and `MaxBatteryChargePowerKw` (charge) are different - charge power typically 10-20% of discharge power
- See 04-battery-management.md Step 6 for detailed calculation process

---

### 6.3 Advanced Cycle-Life Degradation Model (✅ Implemented)

**Source:** [08-degradation-models.md](../concept/08-degradation-models.md#advanced-model-cycle-life-physics)

**Note:** Current implementation uses simple throughput-based degradation. Advanced physics-based model variables are now fully implemented and ready for logic development.

**Implemented Properties - Physics Constants (obj_BatteryElectricTruck, tbl_TruckTypes):**
| Property Name                  | Type    | Description                                   | Default Value | Status |
| ------------------------------ | ------- | --------------------------------------------- | ------------- | ------ |
| `prop_ReferenceLifeCycles`     | Integer | Reference cycle count at reference conditions | 5000          | ✅      |
| `prop_ReferenceDOD`            | Real    | Reference depth of discharge (fraction)       | 0.5           | ✅      |
| `prop_ReferenceDischargeCRate` | Real    | Reference discharge C-rate                    | 0.5           | ✅      |
| `prop_ReferenceChargeCRate`    | Real    | Reference charge C-rate                       | 0.5           | ✅      |
| `prop_ReferenceTemperatureK`   | Real    | Reference temperature (K)                     | 298           | ✅      |
| `prop_OperatingTemperatureK`   | Real    | Typical operating temperature (K)             | 318           | ✅      |
| `prop_CycleLife_Xi`            | Real    | DoD exponent (ξ)                              | 0.8           | ✅      |
| `prop_CycleLife_Gamma1`        | Real    | Discharge rate exponent (γ₁)                  | 0.8           | ✅      |
| `prop_CycleLife_Gamma2`        | Real    | Charge rate exponent (γ₂)                     | 2.34          | ✅      |
| `prop_CycleLife_Psi`           | Real    | Temperature coefficient (ψ)                   | 3700          | ✅      |
| `prop_CycleLife_Alpha`         | Real    | Temperature exponent (α)                      | 0.9708        | ✅      |

**Implemented State Variables - Cycle Tracking (obj_Battery):**
| Variable Name                        | Type     | Description                                  | Initial Value | Status |
| ------------------------------------ | -------- | -------------------------------------------- | ------------- | ------ |
| `var_CycleInProgress`                | Boolean  | True during active haul cycle                | False         | ✅      |
| `var_CurrentCycleStartSOCPct`        | Discrete | SOC when cycle started (%)                   | 0             | ✅      |
| `var_CurrentCycleMinSOCPct`          | Discrete | Minimum SOC reached this cycle (%)           | 100           | ✅      |
| `var_CurrentCycleMaxSOCPct`          | Discrete | Maximum SOC reached this cycle (%)           | 0             | ✅      |
| `var_CurrentCycleDischargeEnergyKwh` | Discrete | Total discharge energy this cycle (kWh)      | 0             | ✅      |
| `var_CurrentCycleDischargeTimeHrs`   | Discrete | Total discharge time this cycle (hours)      | 0             | ✅      |
| `var_CurrentCycleChargeEnergyKwh`    | Discrete | Total charge energy this cycle (kWh)         | 0             | ✅      |
| `var_CurrentCycleChargeTimeHrs`      | Discrete | Total charge time this cycle (hours)         | 0             | ✅      |
| `var_EquivalentCyclesAccumulated`    | Discrete | Weighted cycle count accounting for severity | 0             | ✅      |

**Required Token Variables (Per-Cycle Calculations):**
| Variable Name             | Type     | Description                                            |
| ------------------------- | -------- | ------------------------------------------------------ |
| `CycleDoD`                | Discrete | Depth of discharge this cycle (fraction 0-1)           |
| `AvgDischargeCRate`       | Discrete | Average discharge C-rate this cycle                    |
| `AvgChargeCRate`          | Discrete | Average charge C-rate this cycle                       |
| `ThetaDoD`                | Discrete | DoD degradation factor (θ_DoD)                         |
| `ThetaDischarge`          | Discrete | Discharge rate degradation factor (θ_i_dis)            |
| `ThetaCharge`             | Discrete | Charge rate degradation factor (θ_i_ch)                |
| `ThetaTemperature`        | Discrete | Temperature degradation factor (θ_T)                   |
| `CycleImpactFactor`       | Discrete | Combined cycle impact (θ_DoD × θ_i_dis × θ_i_ch × θ_T) |
| `EquivalentCycleFraction` | Discrete | Fraction of reference cycle this cycle represents      |

**Implementation Notes:**
- ✅ All variables implemented in Simio model (physics constants in tbl_TruckTypes, state tracking in obj_Battery)
- ⏳ Process logic pending implementation
- 9-step process: Cycle detection → Data accumulation → DoD calculation → C-rate calculation → Degradation factors → Equivalent cycles → Health update → Reset
- Physics-based model accounts for: Depth of discharge, charge/discharge rates, temperature, cycle count
- Interpretation: Shallow cycling (5% DoD) = 0.223 equivalent cycles, Deep cycling (90% DoD) = 10+ equivalent cycles
- Significantly more accurate than simple throughput model for battery life prediction
- See 08-degradation-models.md for full mathematical formulation and example scenarios

---

### 6.4 Infrastructure Routing Variables (✅ Implemented)

**Source:** [06-infrastructure.md](../concept/06-infrastructure.md)

**Implementation Status:**
- ✅ **Unified service flag:** `var_SwapRefuelChargeFlag` (Boolean) - Triggers service need for any infrastructure type
- ✅ **Unified node assignment:** `var_SwapRefuelChargeNode` (ElementReference) - Assigned service station node

**Design Decision:**
Current implementation uses a **unified approach** where a single flag and node variable handle all infrastructure types (battery swap, diesel refuel, depot charge). This simplifies routing logic and avoids redundant state tracking, as trucks only visit one service type at a time based on their TruckMode.

---

### 6.5 Enhanced Fuel Tracking (Partially Implemented)

**Source:** [05-fuel-systems.md](../concept/05-fuel-systems.md)

**Current Status:**
- ✅ Basic fuel consumption tracking implemented (`var_DieselConsumedL`, `var_DieselEnergyConsumedKwh`)
- ✅ Fuel savings tracking implemented (`var_DieselPreservedL`, `var_DieselEnergyPreservedKwh`)
- ✅ Refuel trigger logic implemented (`var_SwapRefuelChargeFlag`)

**Potential Enhancements (Optional):**
| Variable Name                 | Type     | Description                                  |
| ----------------------------- | -------- | -------------------------------------------- |
| `var_TotalDieselCostUSD`      | Discrete | Cumulative diesel fuel cost ($)              |
| `var_TotalElectricityCostUSD` | Discrete | Cumulative electricity cost ($)              |
| `var_TotalCostSavingsUSD`     | Discrete | Total operating cost savings vs baseline ($) |

**Implementation Notes:**
- Economic tracking requires diesel price ($/L) and electricity price ($/kWh) parameters
- See 05-fuel-systems.md for cost calculation examples and savings validation
- Current implementation sufficient for technical simulation; economic tracking optional for financial analysis

---

### 6.6 Trolley State Tracking (Partially Implemented)

**Source:** [06-infrastructure.md](../concept/06-infrastructure.md), [07-trolley-power-sharing.md](../concept/07-trolley-power-sharing.md)

**Current Status:**
- ✅ Trolley power calculation implemented (`TrolleyPowerKw`)
- ✅ Active trucks tracking implemented (`TrolleyActiveTrucksOnSection`)
- ✅ Dynamic power sharing logic implemented

**Potential Enhancement:**
| Variable Name             | Type    | Description                                    |
| ------------------------- | ------- | ---------------------------------------------- |
| `var_TrolleyAssistActive` | Boolean | True when truck actively drawing trolley power |

**Implementation Notes:**
- Current implementation tracks trolley power availability and usage
- Explicit state variable could improve diagnostics and statistics collection
- Not critical for physics calculations (can be inferred from `TrolleyPowerKw > 0`)

---

### 6.7 Traction Limit Calculations (NEW)

**Source:** [02-physics-speed-force.md](../concept/02-physics-speed-force.md#step-5-calculate-traction-limit)

**Purpose:** Limits tractive force (rimpull and retarding) based on tire-ground friction to prevent wheel slip or lock-up.

**New Path Property:**
| Property Name                  | Type | Description                                        | Default Value    | Status |
| ------------------------------ | ---- | -------------------------------------------------- | ---------------- | ------ |
| `prop_RoadFrictionCoefficient` | Real | Surface friction coefficient μ for traction limits | 0.7 (dry gravel) | 🆕 NEW  |

**Typical Friction Coefficients:**
| Surface Condition    | μ Value   |
| -------------------- | --------- |
| Dry compacted gravel | 0.7 - 0.8 |
| Wet gravel           | 0.4 - 0.6 |
| Muddy conditions     | 0.3 - 0.4 |
| Icy conditions       | 0.1 - 0.2 |

**New Token Variables:**
| Variable Name             | Type     | Description                                                   |
| ------------------------- | -------- | ------------------------------------------------------------- |
| `RoadFrictionCoefficient` | Discrete | Surface friction coefficient μ (from path property)           |
| `GradeAngleRad`           | Discrete | Grade angle in radians: ATAN(CurrentGrade / 100)              |
| `NormalForceN`            | Discrete | Normal force perpendicular to surface: m × g × cos(θ) (N)     |
| `TractionLimitN`          | Discrete | Maximum traction force before wheel slip: μ × NormalForce (N) |
| `TractionLimitedForceN`   | Discrete | Tractive force after applying traction limit (N)              |
| `TractionLimitActive`     | Boolean  | True when force was limited by traction (for diagnostics)     |

**Physics Equation:**
```
F_max = μ × N = μ × m × g × cos(θ)

Where:
  μ = coefficient of friction (tire-to-road)
  N = normal force (perpendicular to surface)
  m = truck mass (kg)
  g = 9.81 m/s²
  θ = grade angle (radians)
```

**When Traction Limiting Applies:**

| Condition                          | Rimpull (Accelerating) | Retarding (Braking) |
| ---------------------------------- | ---------------------- | ------------------- |
| Empty trucks, poor roads (μ < 0.5) | ✅ Likely limited       | ✅ Limited           |
| All trucks on wet/muddy roads      | ✅ Limited              | ✅ Limited           |
| Low speeds (0-10 km/h)             | ✅ Motor > traction     | ✅ Motor >> traction |
| Loaded trucks, dry roads           | ❌ Curves conservative  | ✅ Limited           |

**Example: CAT 794 AC Retarding at 1 km/h:**
```
Motor capability (curve):      8,000 kN
Traction (loaded, μ=0.7):      3,578 kN  → Actual limit
Traction (empty, μ=0.7):       1,527 kN  → Actual limit
```

**Implementation Notes:**
- Traction limit applies to BOTH rimpull (accelerating) and retarding (braking)
- For grades < 20%, cos(θ) ≈ 1.0 with < 2% error (can simplify)
- Diagnostic flag `TractionLimitActive` helps identify when traction is the limiting factor
- Critical for realistic low-speed dynamics and wet/muddy road simulation

---

### 6.8 Implementation Priority Recommendations

**✅ COMPLETED (Core Physics - All Variables Implemented):**
1. **Motor Thermal Management** - All properties and state variables implemented, process logic pending
2. **Advanced Cycle-Life Degradation** - All physics constants and state tracking variables implemented, process logic pending
3. **Battery Charge Power Property** - MaxBatteryChargePowerKw implemented in tbl_TruckTypes
4. **Traction Limit Variables** - Path property and token variables defined, ready for implementation

**MEDIUM Priority (Enhanced Functionality - Token Variables Pending):**
1. **PreserveBattery Charging Logic** - Property implemented, token variables for safe charge rate limiting pending

**LOW Priority (Optional Enhancements):**
4. **Economic Tracking** - Useful for financial analysis but not required for technical simulation
5. **Trolley State Tracking** - Diagnostic improvement but functionally redundant

---

### 6.9 Summary Statistics

**Current Implementation (December 2025):**
- Properties: 38 (obj_BatteryElectricTruck + obj_ElectricPath + obj_BatterySwapChargeStation)
- State Variables: 23 (obj_BatteryElectricTruck) + 20 (obj_Battery) + 12 (obj_BatterySwapChargeStation) = 55 total
- Token Variables: 101 (tkn_TimeStepCalculations)

**Token Variable Categories:**
- Truck Specifications: 8
- Performance Curves: 3
- Battery Parameters: 11
- Diesel Parameters: 9
- Trolley Parameters: 6 (including OnTrolleyPath)
- Trolley Power Sharing: 4 (TrolleySectionTotalPowerKw, TrolleyMaxPowerPerTruckKw, TrolleySharedPowerPerTruckKw, TrolleyAvailablePowerKw)
- Diesel/Fuel Calculations: 4 (CurrentDieselLevelPct, RefuelRateLPerMin, FuelAddedL, TotalDemandKw)
- Speed & Force Calculations: 13
- Traction Limit Calculations: 5
- Power Flow Calculations: 19
- Motor Thermal Management: 5
- Battery Charging: 3
- Cycle-Life Degradation: 9

**Completion Status:**
- ✅ Core speed/battery/fuel physics complete
- ✅ Infrastructure routing complete  
- ✅ Motor thermal management variables complete
- ✅ Advanced cycle-life degradation variables complete
- ✅ Traction limit variables complete
- ✅ DieselElectric fuel tracking variables complete
- ✅ Trolley power sharing variables complete (Model B per concept/07-trolley-power-sharing.md)
- ⏳ Process logic implementation in progress
