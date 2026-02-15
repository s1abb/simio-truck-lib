# Parameter Mapping: Simio Tables to JSON Structure

This document maps Simio table columns to the JSON schema structure for equipment specifications.

## Battery Parameters

### Simio Table: BatteryType Table
| Simio Column | JSON Path | Example Value | Notes |
|-------------|-----------|---------------|-------|
| BatteryType | `battery.battery_type` | "Lithium_Iron_Phosphate" | Battery chemistry |
| RatedStorageEnergyKwh | `battery.rated_capacity_kwh` | 801.00 | Battery capacity in kWh |
| RatedChargingCycles | `battery.rated_charging_cycles` | 5000 | Number of charge cycles |
| RatedLifetimeThroughputKwh | `battery.rated_lifetime_throughput_kwh` | 4005000.00 | Total kWh over lifetime |
| EndOfLifeBatteryHealthPct | `battery.end_of_life_health_pct` | 70.00 | EOL health % |
| InitialBatterySOCPct | `battery.initial_soc_pct` | 100.00 | Initial state of charge |
| InitialBatteryCumulativeThroughputKwh | `battery.initial_cumulative_throughput_kwh` | 0.00 | Starting throughput |
| InitialBatteryHealthPct | `battery.initial_health_pct` | 100.00 | Starting health |
| InitialBatteryResourceState | `battery.initial_resource_state` | "ReadyToDeploy" | Resource state |

## Truck Parameters

### Simio Table: TruckType Table
| Simio Column | JSON Path | Example Value | Notes |
|-------------|-----------|---------------|-------|
| TruckType | `model` | "cat_794_ac" | Model identifier |
| TruckMode | `truck_mode` | "DieselElectric" | Operating mode |
| BatteryType | `battery.battery_type` | "Lithium_Iron_Phosphate_801" | Links to battery |
| EmptyOperatingWeightKg | `weights.empty_kg` | 217419.00 | Empty weight |
| RatedGrossMachineWeightKg | `weights.loaded_kg` | 521631.00 | GVM (loaded) |
| RimpullForceN | `performance_curves.rimpull_curve.data` | (lookup table) | Speed-based curve |
| RetardForceN | `performance_curves.retarding_curve.data` | (lookup table) | Speed-based curve |
| MaxSpeedKmh_Loaded | `drivetrain.max_speed_kmh_loaded` | 60 | Max speed when loaded |
| MaxSpeedKmh_Empty | `drivetrain.max_speed_kmh_empty` | 64 | Max speed when empty |
| RollingResistance | `drivetrain.rolling_resistance` | 0.02 | Rolling resistance coeff |
| MotorEfficiencyPct | `drivetrain.motor_efficiency_pct` | 92.00 | Motor efficiency |
| RegenEfficiencyPct | `drivetrain.regen_efficiency_pct` | 75.00 | Regen efficiency |
| AuxiliaryPowerDemandKw | `drivetrain.auxiliary_power_kw` | 20.00 | Aux power demand |
| BatteryMaxPowerKw | `battery.max_power_kw` | 0.00 | Battery max power |
| SwapBatterySOCPct | `battery.swap_soc_pct` | 80.00 | SOC for battery swap |
| DieselFuelConsumptionRateLKwh | `diesel_system.fuel_consumption_rate_l_kwh` | 0.11 | L per kWh |
| DieselTankCapacityL | `diesel_system.tank_capacity_l` | 4922.00 | Tank capacity |
| InitialDieselLevelL | `diesel_system.initial_fuel_level_l` | 4922.00 | Starting fuel |
| DieselGeneratorMaxPowerKw | `diesel_system.generator_max_power_kw` | 2539.00 | Gen max power |
| DieselGeneratorEfficiencyPct | `diesel_system.generator_efficiency_pct` | 40.00 | Gen efficiency |
| RefuelDieselLevelPct | `diesel_system.refuel_level_pct` | 10.00 | Refuel threshold |

## Performance Curves

Simio uses lookup tables referenced in the TruckType table:

### Rimpull (Tractive Force)
- **Simio:** `ltbl_[TruckType]_SpeedKmh_RimpullTractiveForceN[CurrentSpeedKmh/1000]`
- **JSON:** `performance_curves.rimpull_curve.data.{speed_kmh[], rimpull_kn[]}`
- **Conversion:** N → kN (divide by 1000)

### Retarding (Braking Force)
- **Simio:** `ltbl_[TruckType]_SpeedKmh_RetardForceN[CurrentSpeedKmh/1000]`
- **JSON:** `performance_curves.retarding_curve.data.{speed_kmh[], retarding_kn[]}`
- **Conversion:** N → kN (divide by 1000)

### Max Speed vs Grade (Loaded)
- **Simio:** `ltbl_[TruckType]_GradeP_MaxSpeedKmh_Loaded[CurrentGrade]`
- **JSON:** Can be derived from rimpull curve + gradeability data
- **Note:** Generated from gradeability chart data points

### Max Speed vs Grade (Empty)
- **Simio:** `ltbl_[TruckType]_GradeP_MaxSpeedKmh_Empty[CurrentGrade]`
- **JSON:** Can be derived from rimpull curve + gradeability data
- **Note:** Generated from gradeability chart data points

## Complete JSON Structure Example

```json
{
  "model": "cat_794_ac",
  "manufacturer": "Caterpillar",
  "truck_mode": "DieselElectric",
  "category": "ultra_class_haul_truck",
  "weights": {
    "empty_kg": 217419,
    "loaded_kg": 521631,
    "payload_kg": 304212
  },
  "drivetrain": {
    "type": "AC_electric_drive",
    "max_speed_kmh_loaded": 60,
    "max_speed_kmh_empty": 64,
    "motor_efficiency_pct": 92.0,
    "regen_efficiency_pct": 75.0,
    "rolling_resistance": 0.02,
    "auxiliary_power_kw": 20.0
  },
  "diesel_system": {
    "fuel_consumption_rate_l_kwh": 0.11,
    "tank_capacity_l": 4922.0,
    "initial_fuel_level_l": 4922.0,
    "generator_max_power_kw": 2539.0,
    "generator_efficiency_pct": 40.0,
    "refuel_level_pct": 10.0
  }
}
```

## Battery Electric Example

```json
{
  "model": "cat_793_xe",
  "truck_mode": "BatteryElectric",
  "battery": {
    "battery_type": "Lithium_Iron_Phosphate",
    "rated_capacity_kwh": 1700.0,
    "rated_charging_cycles": 6000,
    "rated_lifetime_throughput_kwh": 10200000.0,
    "end_of_life_health_pct": 70.0,
    "initial_soc_pct": 100.0,
    "initial_cumulative_throughput_kwh": 0.0,
    "initial_health_pct": 100.0,
    "initial_resource_state": "ReadyToDeploy",
    "max_power_kw": 0.0
  },
  "drivetrain": {
    "motor_efficiency_pct": 92.0,
    "regen_efficiency_pct": 75.0,
    "rolling_resistance": 0.02,
    "auxiliary_power_kw": 18.0
  }
}
```

## Battery Swap Example

```json
{
  "model": "tonly_dte145",
  "truck_mode": "BatterySwap",
  "battery": {
    "battery_type": "Lithium_Iron_Phosphate",
    "rated_capacity_kwh": 801.0,
    "swap_soc_pct": 80.0,
    "initial_soc_pct": 100.0
  }
}
```

## Parameter Coverage Status

| Parameter Category | Captured in JSON | Schema Updated | Notes |
|-------------------|------------------|----------------|-------|
| Battery specs | ✅ | ✅ | All 9 parameters |
| Truck weights | ✅ | ✅ | Empty, loaded, payload |
| Speed limits | ✅ | ✅ | Loaded and empty |
| Efficiencies | ✅ | ✅ | Motor, regen |
| Rolling resistance | ✅ | ✅ | Coefficient |
| Auxiliary power | ✅ | ✅ | kW demand |
| Diesel system | ✅ | ✅ | All 6 parameters |
| Performance curves | ✅ | ✅ | Rimpull, retarding |
| Gradeability data | ✅ | ✅ | Empty, loaded points |

## Notes

1. **Unit Conversions:**
   - Force: N → kN (divide by 1000)
   - Weight: Automatically in kg
   - Percentages: Stored as 0-100 scale

2. **Lookup Tables:**
   - Simio uses inline table lookups
   - JSON stores complete arrays
   - Import scripts can generate Simio lookup table format

3. **Truck Mode:**
   - "BatteryElectric" - Battery only, no diesel
   - "BatterySwap" - Swappable battery packs
   - "DieselElectric" - Diesel generator + electric drive
   - "TrolleyAssist" - Pantograph power on uphill
   - "Hybrid" - Combined systems

4. **Missing Parameters:**
   - All critical Simio parameters are now captured
   - Schema supports future expansion
   - Backwards compatible with existing data
