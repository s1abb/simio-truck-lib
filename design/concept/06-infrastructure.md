# Infrastructure Components

**Version:** 1.0  
**Last Updated:** November 2025  
**Status:** Design Specification

---

## Overview

This document describes the four infrastructure types that support multi-mode electric truck operations:

1. **Electric Paths** - Trolley-assisted overhead catenary sections
2. **Battery Swap Charge Stations** - Fast battery replacement (BatterySwap mode)
3. **Diesel Refuel Stations** - Diesel fuel replenishment (DieselElectric mode)
4. **Depot Charge Stations** - Stationary battery charging (BatteryElectric mode concept)

All infrastructure types use a **unified service flag system** (`var_SwapBattery_Refuel_ChargeBattery_Flag`) to trigger mode-specific service operations.

**Source Documents:**
- Complete_Physics_Implementation_Matrix.md (Section 8, infrastructure requirements)
- MultiTruckConcept.md (obj_ElectricPath, obj_BatterySwapChargeStation, trolley power sharing)
- Reference: Aitik mine operations (10 MW trolley, CAT 795F AC fleet)

---

## 1. Electric Paths (obj_ElectricPath)

### Purpose

Overhead catenary trolley sections that provide dynamic electrical power to trucks via pantograph connection. Enable both fuel/battery preservation (PreserveEnergy mode) and increased productivity (SustainSpeed mode).

### Key Properties

| Property                          | Type    | Default/Typical                | Description                                   |
| --------------------------------- | ------- | ------------------------------ | --------------------------------------------- |
| `prop_TrolleyAssistEnabled`       | Boolean | `tbl_Paths.ElectricAssistPath` | Enable/disable trolley for this path          |
| `prop_TrolleySectionTotalPowerKw` | Real    | 10000                          | Total substation capacity (kW)                |
| `prop_TrolleyMaxPowerPerTruckKw`  | Real    | 5000                           | Individual truck pantograph limit (kW)        |
| `prop_TrolleyMaxConcurrentTrucks` | Integer | 6                              | Physical capacity (path length / min spacing) |
| `prop_TrolleyVoltageV`            | Real    | 1200                           | System voltage (V)                            |
| `prop_TrolleyEfficiencyPct`       | Real    | 93                             | Power delivery efficiency (%)                 |

**Typical 1 km section configuration:**
- Section power: 10 MW (verified Aitik mine)
- Per-truck max: 5 MW (verified CAT 795F AC)
- Max trucks: 6 (based on 150-200m spacing)
- Voltage: 1200V DC (historical, modern systems vary)
- Efficiency: 93% (90-95% typical range)

### Power Sharing Model

**Dynamic Power Sharing (Recommended):**

Trolley section total power is divided among all active trucks on the section. As truck count increases, available power per truck decreases.

**Calculation:**
```
ActiveTrucksOnSection = CurrentPath.NumberTravelers  // Simio built-in
SharedPowerPerTruckKw = TrolleySectionTotalPowerKw / ActiveTrucksOnSection
AvailablePowerPerTruckKw = min(SharedPowerPerTruckKw, TrolleyMaxPowerPerTruckKw)
TrolleyPowerKw = AvailablePowerPerTruckKw × (TrolleyEfficiencyPct / 100)
```

**Example scenarios (10 MW section, 5 MW truck limit):**

| Active Trucks | Shared Power                 | Available per Truck (93% eff) | Section Behavior    |
| ------------- | ---------------------------- | ----------------------------- | ------------------- |
| 1             | 10 MW → 5 MW (truck-limited) | 4.65 MW                       | Optimal performance |
| 2             | 5 MW                         | 4.65 MW                       | Optimal performance |
| 3             | 3.3 MW                       | 3.07 MW                       | Section-limited     |
| 4             | 2.5 MW                       | 2.33 MW                       | Reduced performance |
| 6             | 1.7 MW                       | 1.58 MW                       | Maximum capacity    |

**Real-world validation:**
- Aitik mine: 10 MW DC capacity, CAT 795F AC fleet (4.5+ MW per truck)
- ABB systems: Up to 12 MW DC (premium)
- General industry: 8 MW DC (conventional)

**Transit time analysis (30 km/h average, 1 km section):**
- Transit time: 2 minutes
- Typical headway: 3-5 minutes
- Expected trucks on section: 1-2 (most common)
- Peak trucks: 3-4 (busy periods)

### Integration with Speed Calculations

**Critical:** Power-limited physics calculations **must use dynamically calculated `TrolleyPowerKw`**, not static property values.

**Correct pattern in `proc_SpeedBatteryUpdates`:**
```pseudocode
# Step 1: Calculate dynamic trolley power FIRST
if OnElectricPath AND prop_TrolleyAssistEnabled:
    ActiveTrucksOnSection = CurrentPath.NumberTravelers
    SharedPowerPerTruckKw = TrolleySectionTotalPowerKw / ActiveTrucksOnSection
    AvailablePowerPerTruckKw = min(SharedPowerPerTruckKw, TrolleyMaxPowerPerTruckKw)
    TrolleyPowerKw = AvailablePowerPerTruckKw × TrolleyEfficiency
else:
    TrolleyPowerKw = 0

# Step 2: Use TrolleyPowerKw in force calculations (SustainSpeed modes)
if ElectricAssistMode == "SustainSpeed":
    TotalAvailablePowerKw = OnboardPowerKw + TrolleyPowerKw  # Dynamic value
    PowerLimitForceN = (TotalAvailablePowerKw × 1000) / SpeedMs
    TractiveForceN = min(CurveLimitForceN, PowerLimitForceN)
```

**Physics validation:** Using dynamic `TrolleyPowerKw` ensures total section power consumption never exceeds `TrolleySectionTotalPowerKw`. Using static property values would cause non-physical behavior (section appearing to supply more power than available).

**See:** `02-physics-speed-force.md` for power-limited scaling factor details, `07-trolley-power-sharing.md` for detailed power sharing implementation.

---

## 2. Battery Swap Charge Stations (obj_BatterySwapChargeStation)

### Purpose

Fast battery replacement facility for BatterySwap mode trucks (TONLY DTE145). Swaps depleted battery with fully charged battery in 5-10 minutes, enabling continuous operation without charge downtime.

### Summary

Battery swap stations are **already implemented** in the current Simio model with comprehensive physics and service logic.

**Existing implementation includes:**
- Battery swap process (5-10 minute service time)
- Battery inventory management
- Charging queue for depleted batteries
- Service flag reset (`var_SwapBattery_Refuel_ChargeBattery_Flag = False`)

**Key characteristics:**
- Service time: 5-10 minutes (swap operation)
- Trigger: `var_BatterySOCPct < prop_SwapBatterySOCPct` (typically 80%)
- Destination: `var_AssignBatterySwapChargeStationNode`
- Battery charging: Controlled rate, parallel to truck operations

**Documentation reference:**
- See `/workspace/simproj/Models.obj_BatterySwapChargeStation.md` for full implementation details
- See `/workspace/models/Model v7 - Add obj_BatterySwapChargeStation Logic.spfx` for Simio logic
- See Complete_Physics_Implementation_Matrix.md Section 7.1 for operational profile

**Economics (per swap cycle):**
- Operating cost: $8-17 (electricity)
- vs Diesel equivalent: $360 (98% savings)
- Infrastructure requirement: Battery inventory + swap station

---

## 3. Diesel Refuel Stations (obj_DieselRefuelStation)

### Purpose

Diesel fuel replenishment facility for DieselElectric mode trucks. Provides fast refueling to minimize downtime while maintaining operational flexibility.

### Key Properties

| Property                     | Type    | Typical Value | Description                        |
| ---------------------------- | ------- | ------------- | ---------------------------------- |
| `prop_RefuelFlowRateLPerMin` | Real    | 200-300       | Fuel flow rate (L/min)             |
| `prop_RefuelStationCapacity` | Integer | 2-4           | Number of simultaneous refuel bays |
| `InitialCapacity`            | Integer | Same as above | Simio resource capacity            |

### Service Process

**Trigger condition:**
```pseudocode
if TruckMode == "DieselElectric":
    if var_DieselLevelL < prop_RefuelDieselLevelL:  // Typically 10% tank capacity
        var_SwapBattery_Refuel_ChargeBattery_Flag = True
        # Navigate to var_AssignRefuelStationNode
```

**Refuel operation:**
```pseudocode
# At diesel refuel station
AmountToRefuelL = prop_DieselTankCapacityL - var_DieselLevelL
RefuelTimeMinutes = AmountToRefuelL / prop_RefuelFlowRateLPerMin

# Delay for refuel time
Wait(RefuelTimeMinutes)

# Update truck state
var_DieselLevelL = prop_DieselTankCapacityL
var_DieselLevelPct = 100
var_SwapBattery_Refuel_ChargeBattery_Flag = False  // Reset service flag

# Release truck
```

### Capacity Planning

**Example: CAT 794 AC fleet (100 trucks)**

**Truck specifications:**
- Tank capacity: 3,028 L
- Refuel trigger: 10% (303 L remaining)
- Amount to refuel: 2,725 L
- Fuel consumption: 90 L/hr average (on trolley: 8 L/hr, off trolley: 150 L/hr)

**Fleet refuel demand:**
- Operating hours per truck: 20 hrs/day
- Off-trolley time: 80% of cycle (20% trolley coverage)
- Fuel consumption per shift: ~1,800 L/truck (off trolley: 150 L/hr × 16 hrs)
- Refuels per truck per day: 0.7 refuels (1,800 L / 2,725 L)
- Fleet refuels per day: 70 refuels

**Station capacity calculation:**
- Refuel time per truck: 2,725 L / 250 L/min = 10.9 minutes
- Station utilization: 70 refuels × 10.9 min = 763 minutes/day
- Operating hours: 24 hours = 1,440 minutes
- Required bays: 763 / 1,440 = **0.53 bays** (1 bay sufficient)
- Recommended: **2 bays** (redundancy, peak traffic handling)

**Refuel station configuration:**
```
obj_DieselRefuelStation:
  prop_RefuelFlowRateLPerMin = 250         // L/min (industry standard)
  prop_RefuelStationCapacity = 2           // Number of bays
  InitialCapacity = 2                       // Simio resource
```

### Economic Impact

**PreserveEnergy mode (20% trolley coverage):**
- Fuel consumption reduction: 95-98% while on trolley
- Fleet fuel savings: $13.4M-$36.0M/year (varies by truck type)
- Refuel frequency: Reduced vs diesel-only operation
- ROI: 2-3 years (trolley infrastructure vs fuel savings)

**SustainSpeed mode (20% trolley coverage):**
- Fuel consumption: MAXIMUM (diesel at 100% + trolley)
- No fuel savings vs diesel-only
- Refuel frequency: Same or higher than diesel-only
- Value: Production increase (4.4-8.8% more cycles)

---

## 4. Depot Charge Stations (Concept)

### Purpose

Stationary battery charging facility for BatteryElectric mode trucks operating in StandAlone mode (no trolley infrastructure) or as backup charging when PreserveBattery mode trucks require supplemental charging.

### Design Concept

**Not currently implemented** - BatteryElectric trucks in the current fleet design (Liebherr T 264 BE) operate in PreserveBattery or SustainSpeed modes with trolley infrastructure, charging opportunistically from excess trolley power.

**Potential use cases:**
1. **StandAlone mode** - BatteryElectric trucks operating without trolley (high battery stress, frequent charging)
2. **Emergency backup** - Supplemental charging when trolley coverage insufficient
3. **Depot overnight charging** - Top-up charging during maintenance periods

### Conceptual Properties

| Property                     | Type    | Typical Value | Description                       |
| ---------------------------- | ------- | ------------- | --------------------------------- |
| `prop_ChargeRatePowerKw`     | Real    | 500-1000      | Charging power (kW)               |
| `prop_ChargeStationCapacity` | Integer | 2-4           | Number of charging bays           |
| `prop_ChargeEfficiencyPct`   | Real    | 95            | Charging efficiency (%)           |
| `prop_ChargeBatterySOCPct`   | Real    | 20-30         | SOC threshold to trigger charging |
| `prop_TargetChargeSOCPct`    | Real    | 100           | Target SOC for charge completion  |

### Conceptual Service Process

**Trigger condition:**
```pseudocode
if TruckMode == "BatteryElectric":
    if var_BatterySOCPct < prop_ChargeBatterySOCPct:
        var_SwapBattery_Refuel_ChargeBattery_Flag = True
        # Navigate to var_AssignDepotChargeStationNode
```

**Charging operation:**
```pseudocode
# At depot charge station
CurrentSOC = var_BatterySOCPct
TargetSOC = prop_TargetChargeSOCPct
EffectiveCapacityKwh = prop_BatteryCapacityKwh × (var_BatteryHealthPct / 100)

EnergyRequiredKwh = ((TargetSOC - CurrentSOC) / 100) × EffectiveCapacityKwh
ChargeTimeHours = EnergyRequiredKwh / (prop_ChargeRatePowerKw × prop_ChargeEfficiencyPct / 100)

# Delay for charge time
Wait(ChargeTimeHours)

# Update truck state
var_BatterySOCPct = TargetSOC
var_SwapBattery_Refuel_ChargeBattery_Flag = False  // Reset service flag

# Release truck
```

### Operational Notes

**StandAlone mode characteristics:**
- Battery stress: HIGH (100% → 20% cycling, DoD = 80%)
- Charge frequency: Multiple times per shift
- Battery degradation: SEVERE (short lifespan, 1-2 years)
- Economics: NOT RECOMMENDED for standard operations

**Recommended approach:** Use PreserveBattery mode with trolley infrastructure instead of StandAlone + depot charging.

---

## 5. Unified Service Flag System

### Purpose

Single unified boolean flag (`var_SwapBattery_Refuel_ChargeBattery_Flag`) triggers mode-specific service operations, reducing code complexity and maintaining consistent behavior across all three truck modes.

### Flag Behavior by Mode

| Truck Mode          | Trigger Condition                              | Service Destination                      | Service Action                               |
| ------------------- | ---------------------------------------------- | ---------------------------------------- | -------------------------------------------- |
| **BatterySwap**     | `var_BatterySOCPct < prop_SwapBatterySOCPct`   | `var_AssignBatterySwapChargeStationNode` | Battery swap at obj_BatterySwapChargeStation |
| **DieselElectric**  | `var_DieselLevelL < prop_RefuelDieselLevelL`   | `var_AssignRefuelStationNode`            | Diesel refuel at obj_DieselRefuelStation     |
| **BatteryElectric** | `var_BatterySOCPct < prop_ChargeBatterySOCPct` | `var_AssignDepotChargeStationNode`       | Battery charge at depot (concept)            |

### Implementation in proc_SpeedBatteryUpdates

**Service flag trigger logic:**
```pseudocode
# After energy calculations in proc_SpeedBatteryUpdates

if prop_TruckMode == "BatterySwap":
    if var_BatterySOCPct < prop_SwapBatterySOCPct:
        var_SwapBattery_Refuel_ChargeBattery_Flag = True
        # Truck navigation uses var_AssignBatterySwapChargeStationNode
        
elif prop_TruckMode == "DieselElectric":
    if var_DieselLevelL < prop_RefuelDieselLevelL:
        var_SwapBattery_Refuel_ChargeBattery_Flag = True
        # Truck navigation uses var_AssignRefuelStationNode
        
elif prop_TruckMode == "BatteryElectric":
    if var_BatterySOCPct < prop_ChargeBatterySOCPct:
        var_SwapBattery_Refuel_ChargeBattery_Flag = True
        # Truck navigation uses var_AssignDepotChargeStationNode
```

### Service Station Responsibilities

Each service station (swap/refuel/charge) **must reset the flag** after service completion:

```pseudocode
# At end of service process (swap/refuel/charge):
ParentObject.obj_BatteryElectricTruck.var_SwapBattery_Refuel_ChargeBattery_Flag = False

# Release truck to resume normal operations
Transfer.To(ExitNode)
```

### Benefits

- ✅ **Single flag variable** - Reduces state variable count and complexity
- ✅ **Consistent pattern** - Same flag semantics across all three modes
- ✅ **Mode-specific destinations** - Each mode navigates to appropriate service location
- ✅ **Backward compatible** - BatterySwap mode behavior unchanged
- ✅ **Clear responsibility** - Service stations own flag reset logic

---

## State Variables Summary

### Infrastructure-Related State Variables

**obj_BatteryElectricTruck:**

| Variable                                    | Type    | Used By Modes                   | Description                               |
| ------------------------------------------- | ------- | ------------------------------- | ----------------------------------------- |
| `var_SwapBattery_Refuel_ChargeBattery_Flag` | Boolean | All modes                       | Unified service trigger flag              |
| `var_AssignBatterySwapChargeStationNode`    | Node    | BatterySwap                     | Target battery swap station               |
| `var_AssignRefuelStationNode`               | Node    | DieselElectric                  | Target diesel refuel station              |
| `var_AssignDepotChargeStationNode`          | Node    | BatteryElectric                 | Target depot charge station (concept)     |
| `var_TrolleyAssistActive`                   | Boolean | DieselElectric, BatteryElectric | Currently on electric path with assist    |
| `var_TrolleyPowerKw`                        | Real    | DieselElectric, BatteryElectric | Current trolley power available (dynamic) |

**obj_ElectricPath:**

| Property                          | Simio Built-in/Custom | Description                                    |
| --------------------------------- | --------------------- | ---------------------------------------------- |
| `NumberTravelers`                 | Built-in              | Count of trucks currently on this path segment |
| `prop_TrolleySectionTotalPowerKw` | Custom                | Total substation capacity (kW)                 |
| `prop_TrolleyMaxPowerPerTruckKw`  | Custom                | Individual truck pantograph limit (kW)         |

---

## Cross-References

**Related concept documents:**
- `01-fleet-and-modes.md` - Fleet composition and operating mode definitions
- `02-physics-speed-force.md` - Power-limited scaling factor integration with trolley power
- `03-power-flow.md` - Motor power limiting and mode-specific power combining patterns
- `04-battery-management.md` - PreserveBattery trolley charging scenarios
- `05-fuel-systems.md` - Diesel refuel station capacity and fuel savings economics
- `07-trolley-power-sharing.md` - Detailed power sharing implementation (Model A vs Model B)

**Source documents:**
- Complete_Physics_Implementation_Matrix.md Section 7 (operating scenarios), Section 8 (implementation notes)
- MultiTruckConcept.md (obj_ElectricPath power sharing, obj_BatterySwapChargeStation logic)


