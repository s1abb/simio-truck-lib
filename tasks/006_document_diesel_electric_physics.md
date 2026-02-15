# Task 006: Document DieselElectric Physics Processes

## Objective

Create markdown documentation for the three DieselElectric physics processes, matching the format of `proc_PhysicsUpdates_BatterySwap.md`.

## Files to Create

| File                                                                | Status     |
| ------------------------------------------------------------------- | ---------- |
| `design/simio/proc_PhysicsUpdates_DieselElectric_PreserveEnergy.md` | ✅ Complete |
| `design/simio/proc_PhysicsUpdates_DieselElectric_SustainSpeed.md`   | ✅ Complete |
| `design/simio/proc_PhysicsUpdates_DieselElectric_RefuelDiesel.md`   | ✅ Complete |

## Current XML State

- **PreserveEnergy**: Speed Updates implemented (identical to BatterySwap), FuelUpdates step is empty placeholder
- **SustainSpeed**: Speed Updates implemented (identical to PreserveEnergy), FuelUpdates step is empty placeholder  
- **RefuelDiesel**: Empty process (no steps)

## Design Reference

Per `design/concept/03-power-flow.md` and `design/concept/05-fuel-systems.md`:

### PreserveEnergy Mode
- Trolley power replaces diesel generator
- Diesel engine idles (minimal fuel consumption)
- 97-98% fuel savings on trolley segments

### SustainSpeed Mode (renamed from IncreaseSpeed)
- Trolley power combines with diesel generator
- Power-limited force calculation: `F = min(RimpullForceN, (DieselPowerKw + TrolleyPowerKw) * 1000 / Speed)`
- 1.3-1.78x speed increase on grades

### Fuel Consumption
- `FuelConsumedL = DieselPowerKw * TimeStepHours * DieselFuelConsumptionRateLKwh`
- Typical rate: ~0.11 L/kWh

## Documentation Approach

1. Document current XML implementation exactly
2. Add "Not Yet Implemented" sections for empty steps
3. Include intended design from concept docs as implementation guide

## Acceptance

- [x] Three `.md` files created in `design/simio/`
- [x] Format matches `proc_PhysicsUpdates_BatterySwap.md`
- [x] Current implementation documented accurately
- [x] Intended design clearly marked for future implementation

---

## Method Implementation Check (December 2025)

### Gap Analysis: Trolley Power Sharing

**Reference:** `design/concept/07-trolley-power-sharing.md` (Model B: Power Sharing)

The concept document specifies dynamic power sharing based on active truck count:

```pseudocode
ActiveTrucksOnSection = CurrentPath.NumberTravelers
SharedPowerPerTruckKw = TrolleySectionTotalPowerKw / ActiveTrucksOnSection
AvailablePowerPerTruckKw = min(SharedPowerPerTruckKw, TrolleyMaxPowerPerTruckKw)
TrolleyPowerKw = AvailablePowerPerTruckKw × (TrolleyEfficiencyPct / 100)
```

**Updated Simio Doc State:**

| Process Document                                    | Reads TrolleySectionTotalPowerKw? | Counts ActiveTrucks? | Calculates SharedPower? |
| --------------------------------------------------- | --------------------------------- | -------------------- | ----------------------- |
| `proc_PhysicsUpdates_DieselElectric_SustainSpeed`   | ✅ Yes (Section 1.4)               | ✅ Yes                | ✅ Yes                   |
| `proc_PhysicsUpdates_DieselElectric_PreserveEnergy` | ✅ Yes (Section 1.4)               | ✅ Yes                | ✅ Yes                   |

**Issue:** ~~Both documents use `TrolleyMaxPowerKw` directly from `tbl_TruckTypes` without accounting for section sharing~~ **RESOLVED**

### Token Variables Status

| Variable Name                  | Purpose                               | Status   |
| ------------------------------ | ------------------------------------- | -------- |
| `TrolleySectionTotalPowerKw`   | Total substation capacity (from path) | ✅ Added  |
| `TrolleyActiveTrucksOnSection` | Count of trucks on current section    | ✅ Exists |
| `TrolleySharedPowerPerTruckKw` | Calculated shared power per truck     | ✅ Added  |
| `TrolleyMaxPowerPerTruckKw`    | Truck pantograph limit (from path)    | ✅ Added  |
| `TrolleyAvailablePowerKw`      | min(shared, pantograph) × efficiency  | ✅ Added  |
| `TotalDemandKw`                | Motor + auxiliary power demand        | ✅ Added  |

### Action Items

- [x] Add trolley power sharing calculation to `proc_PhysicsUpdates_DieselElectric_SustainSpeed.md` (Section 1.4)
- [x] Add trolley power sharing calculation to `proc_PhysicsUpdates_DieselElectric_PreserveEnergy.md` (Section 1.4)
- [x] Add missing token variables to `properties_variables_tables.md`
- [ ] Verify BatterySwap/BatteryElectric processes also need this update

### Additional Findings (December 2025)

**BatteryElectric Process Docs (Empty Files):**

Per `design/concept/01-fleet-and-modes.md`, BatteryElectric trucks (Liebherr T 264 BE) also use trolley power sharing:

| File                                                     | Status    | Needs Trolley Power Sharing? |
| -------------------------------------------------------- | --------- | ---------------------------- |
| `proc_PhysicsUpdates_BatteryElectric_PreserveEnergy.md`  | ⚠️ Empty   | ✅ Yes (per concept)          |
| `proc_PhysicsUpdates_BatteryElectric_SustainSpeed.md`    | ⚠️ Empty   | ✅ Yes (per concept)          |
| `proc_PhysicsUpdates_BatteryElectric_RechargeBattery.md` | ⚠️ Unknown | ❓ Check                      |

**BatterySwap Process Doc:**
| File                                 | Status     | Needs Trolley Power Sharing? |
| ------------------------------------ | ---------- | ---------------------------- |
| `proc_PhysicsUpdates_BatterySwap.md` | ✅ Complete | ❌ No (does not use trolley)  |

**Next Task Required:** Create Task 007 to document BatteryElectric physics processes with trolley power sharing.

---

## Comprehensive Concept-to-Simio Gap Analysis

### Concept Documents Reviewed

| Concept Doc                   | Description                           | Simio Coverage |
| ----------------------------- | ------------------------------------- | -------------- |
| `01-fleet-and-modes.md`       | Fleet composition, 12 configurations  | Partial        |
| `02-physics-speed-force.md`   | 11-step speed physics                 | Partial        |
| `03-power-flow.md`            | Power source combining, motor thermal | Partial        |
| `04-battery-management.md`    | SOC tracking, swap/charge triggers    | Good           |
| `05-fuel-systems.md`          | Fuel consumption, savings tracking    | Partial        |
| `06-infrastructure.md`        | obj_ElectricPath, stations            | Good           |
| `07-trolley-power-sharing.md` | Model B power sharing                 | ✅ Updated      |
| `08-degradation-models.md`    | Throughput & cycle-life degradation   | Good           |

---

### Gap 1: Traction Limit (02-physics-speed-force.md, Steps 5-6)

**Concept (02-physics-speed-force.md):**
```pseudocode
GradeAngleRad = ATAN(CurrentGrade / 100)
NormalForceN = CurrentWeightKg × 9.81 × COS(GradeAngleRad)
TractionLimitN = RoadFrictionCoefficient × NormalForceN
TractiveForceN = MIN(ABS(TractiveForceN), TractionLimitN) × SIGN(TractiveForceN)
```

**Simio Doc State:**

| Process Document                                    | Calculates TractionLimit? | Applies to TractiveForce? |
| --------------------------------------------------- | ------------------------- | ------------------------- |
| `proc_PhysicsUpdates_BatterySwap.md`                | ❌ No                      | ❌ No                      |
| `proc_PhysicsUpdates_DieselElectric_PreserveEnergy` | ❌ No                      | ❌ No                      |
| `proc_PhysicsUpdates_DieselElectric_SustainSpeed`   | ❌ No                      | ❌ No                      |

**Token Variables:** `GradeAngleRad`, `NormalForceN`, `TractionLimitN`, `TractionLimitedForceN`, `TractionLimitActive` - defined in `properties_variables_tables.md` but NOT used in process docs.

**Impact:** Low-speed dynamics on wet/muddy roads unrealistic. Wheel slip not modeled.

---

### Gap 2: Motor Thermal Management (03-power-flow.md, Steps 1-3)

**Concept (03-power-flow.md):**
```pseudocode
CurrentPowerRatio = ABS(MotorElectricalDemandKw) / MaxMotorPowerKw_Continuous
IF MotorPeakModeActive: ThermalAccumulationRatePerSec = 100 / MaxMotorPeakDurationSec
ELSE: CoolingRatePerSec = f(CurrentPowerRatio)  // 0.03 to 1.2 %/sec
MotorThermalStatePercent += Rate × TimeStepSeconds
MotorPowerLimitKw = MaxMotorPowerKw_Peak if thermal OK else MaxMotorPowerKw_Continuous
```

**Simio Doc State:**

| Process Document                                    | Tracks MotorThermalState? | Enforces Peak Duration? | Applies MotorPowerLimit? |
| --------------------------------------------------- | ------------------------- | ----------------------- | ------------------------ |
| `proc_PhysicsUpdates_BatterySwap.md`                | ❌ No                      | ❌ No                    | ❌ No                     |
| `proc_PhysicsUpdates_DieselElectric_PreserveEnergy` | ❌ No                      | ❌ No                    | ❌ No                     |
| `proc_PhysicsUpdates_DieselElectric_SustainSpeed`   | ❌ No                      | ❌ No                    | ❌ No                     |

**Token Variables:** `MotorElectricalDemandKw`, `CurrentPowerRatio`, `ThermalAccumulationRatePctPerSec`, `CoolingRatePctPerSec`, `MotorPowerLimitKw` - defined in `properties_variables_tables.md` but NOT used in process docs.

**Impact:** Motors can operate at peak power indefinitely. No thermal throttling.

---

### Gap 3: Power-Limited Force (02-physics-speed-force.md, Step 4b)

**Concept (02-physics-speed-force.md):**
```pseudocode
IF ElectricAssistMode == "SustainSpeed":
    PowerLimitedForceN = (TotalAvailablePowerKw × 1000) / SpeedMs
    TractiveForceN = MIN(BaselineForceN, PowerLimitedForceN)
```

**Simio Doc State:**

| Process Document                                    | Calculates PowerLimitedForce? | Applies min(curve, power)? |
| --------------------------------------------------- | ----------------------------- | -------------------------- |
| `proc_PhysicsUpdates_BatterySwap.md`                | N/A (not SustainSpeed)        | N/A                        |
| `proc_PhysicsUpdates_DieselElectric_PreserveEnergy` | N/A (PreserveEnergy)          | N/A                        |
| `proc_PhysicsUpdates_DieselElectric_SustainSpeed`   | ✅ Yes (Section 2.3)           | ✅ Yes                      |

**Status:** ✅ Implemented for DieselElectric SustainSpeed. BatteryElectric SustainSpeed docs are empty.

---

### Gap 4: Regenerative Braking (03-power-flow.md)

**Concept (03-power-flow.md):**
```pseudocode
IF MotorMechanicalPowerKw < 0:  // Retarding
    RegenPowerKw = MotorMechanicalPowerKw × RegenEfficiencyPct / 100
    BatteryPowerKw = RegenPowerKw  // Negative = charging
```

**Simio Doc State:**

| Process Document                                    | Calculates RegenPower? | Charges Battery on Retard? |
| --------------------------------------------------- | ---------------------- | -------------------------- |
| `proc_PhysicsUpdates_BatterySwap.md`                | ✅ Yes (Section 3.2)    | ✅ Yes                      |
| `proc_PhysicsUpdates_DieselElectric_PreserveEnergy` | N/A (no battery)       | N/A                        |
| `proc_PhysicsUpdates_DieselElectric_SustainSpeed`   | N/A (no battery)       | N/A                        |

**Status:** ✅ Implemented for BatterySwap. DieselElectric has no battery to charge.

---

### Gap 5: BatteryElectric Trolley Charging (04-battery-management.md, Step 2)

**Concept (04-battery-management.md):**
```pseudocode
IF TruckMode == "BatteryElectric" AND ElectricAssistMode == "PreserveBattery":
    IF TrolleyPowerDrawKw < TrolleyAvailablePowerKw AND CurrentBatterySOCPct < 100:
        ExcessTrolleyPowerKw = TrolleyAvailablePowerKw - TrolleyPowerDrawKw
        BatteryChargePowerKw = MIN(ExcessTrolleyPowerKw, MaxBatteryChargePowerKw)
        NetBatteryPowerKw = -BatteryChargePowerKw  // Charging
```

**Simio Doc State:**

| Process Document                                     | Calculates ExcessTrolley? | Charges from Trolley? |
| ---------------------------------------------------- | ------------------------- | --------------------- |
| `proc_PhysicsUpdates_BatteryElectric_PreserveEnergy` | ⚠️ Empty file              | ⚠️ Empty file          |
| `proc_PhysicsUpdates_BatteryElectric_SustainSpeed`   | ⚠️ Empty file              | N/A (no charging)     |

**Status:** ❌ NOT implemented. BatteryElectric docs are empty.

---

### Gap 6: Cycle-Life Degradation (08-degradation-models.md)

**Concept (08-degradation-models.md):**
```pseudocode
// Advanced cycle-life for BatteryElectric
ThetaDoD = (CycleDoD / ReferenceDOD)^Xi
ThetaDischarge = (AvgDischargeCRate / ReferenceDischargeCRate)^Gamma1
ThetaCharge = (AvgChargeCRate / ReferenceChargeCRate)^Gamma2
ThetaTemperature = exp(Psi × (1/ReferenceT - 1/OperatingT))^Alpha
CycleImpactFactor = ThetaDoD × ThetaDischarge × ThetaCharge × ThetaTemperature
```

**Simio Doc State:**

| Process Document                                     | Implements Cycle-Life Degradation? |
| ---------------------------------------------------- | ---------------------------------- |
| `proc_PhysicsUpdates_BatterySwap.md`                 | ✅ Simple throughput model          |
| `proc_PhysicsUpdates_BatteryElectric_PreserveEnergy` | ⚠️ Empty file                       |
| `proc_PhysicsUpdates_BatteryElectric_SustainSpeed`   | ⚠️ Empty file                       |

**Token Variables:** `CycleDoD`, `ThetaDoD`, `ThetaDischarge`, `ThetaCharge`, `ThetaTemperature`, `CycleImpactFactor`, `EquivalentCycleFraction` - defined in `properties_variables_tables.md`.

**Status:** ❌ NOT implemented. Advanced degradation requires BatteryElectric docs.

---

### Summary: Simio Doc Gaps vs Concept Docs

| Gap # | Feature                          | Concept Doc              | Priority | Files Affected                 |
| ----- | -------------------------------- | ------------------------ | -------- | ------------------------------ |
| 1     | Traction Limit                   | 02-physics-speed-force   | Medium   | All proc_* docs                |
| 2     | Motor Thermal Management         | 03-power-flow            | Medium   | All proc_* docs                |
| 3     | Power-Limited Force              | 02-physics-speed-force   | High     | BatteryElectric_SustainSpeed   |
| 4     | Regenerative Braking             | 03-power-flow            | ✅ Done   | BatterySwap                    |
| 5     | BatteryElectric Trolley Charging | 04-battery-management    | High     | BatteryElectric_PreserveEnergy |
| 6     | Cycle-Life Degradation           | 08-degradation-models    | Medium   | BatteryElectric_* docs         |
| 7     | Trolley Power Sharing            | 07-trolley-power-sharing | ✅ Done   | DieselElectric_* docs          |

---

### Recommended Next Tasks

1. **Task 007: Document BatteryElectric Physics Processes** (HIGH priority)
   - Fill empty `proc_PhysicsUpdates_BatteryElectric_PreserveEnergy.md`
   - Fill empty `proc_PhysicsUpdates_BatteryElectric_SustainSpeed.md`
   - Fill empty `proc_PhysicsUpdates_BatteryElectric_RechargeBattery.md`
   - Include trolley power sharing, trolley charging, cycle-life degradation

2. **Task 008: Add Traction Limit to All Processes** (MEDIUM priority)
   - Add Step 5-6 from concept 02-physics-speed-force to all proc_* docs
   - Use existing token variables

3. **Task 009: Add Motor Thermal Management** (MEDIUM priority)
   - Add thermal tracking from concept 03-power-flow to all proc_* docs
   - Implement peak mode duration limits
