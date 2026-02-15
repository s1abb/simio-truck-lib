# Multi-Truck Mode Concept

**Version:** 1.0  
**Date:** November 20, 2025  
**Purpose:** Unified truck operation modes supporting battery swap, diesel-electric, and battery-electric configurations with electric path assist

## Overview

This document describes the conceptual design for extending `obj_BatteryElectricTruck` to support three distinct operational modes while maintaining backward compatibility with existing battery swap functionality. The design leverages a single `proc_SpeedBatteryUpdates` process with mode-specific logic controlled through properties and the existing event system.

### Truck Modes

1. **BatterySwap Mode** - Battery-electric trucks with battery swapping capability (existing functionality)
2. **DieselElectric Mode** - Diesel-electric hybrid trucks with electric path assist
3. **BatteryElectric Mode** - Battery-electric trucks with charging infrastructure (depot/path charging)

### Electric Assist Modes

When trucks interact with `obj_ElectricPath`, they can operate in one of two assist modes:

1. **PreserveEnergy** - Trolley takes over driving energy (motor + auxiliary), preserves onboard energy source (diesel/battery)
2. **IncreaseSpeed** - Trolley + onboard energy combined for maximum performance

---

## Operational Modes Matrix

| Truck Mode      | Electric Path Interaction | Assist Modes Available        | Primary Energy Source  | Backup Energy Source   |
| --------------- | ------------------------- | ----------------------------- | ---------------------- | ---------------------- |
| BatterySwap     | ❌ No interaction          | N/A                           | Battery (swappable)    | None                   |
| DieselElectric  | ✅ Yes                     | PreserveEnergy, IncreaseSpeed | Diesel generator       | Trolley (when on path) |
| BatteryElectric | ✅ Yes                     | PreserveEnergy, IncreaseSpeed | Battery (rechargeable) | Trolley (when on path) |

---

## Mode 1: BatterySwap (Existing Functionality)

### Characteristics
- Battery as primary energy source
- Swaps battery when SOC < `prop_SwapBatterySOCPct`
- **Does NOT interact with obj_ElectricPath** (passes through as regular path)
- Uses existing swap station logic in `obj_BatterySwapChargeStation`

### Key Properties
- `prop_TruckMode = "BatterySwap"`
- `prop_SwapBatterySOCPct` - SOC threshold for triggering swap
- `prop_InitialAssignBatterySwapChargeStationNode` - Assigned swap station

### Energy Flow (Existing)
```
Driving Power Demand → Battery Only
Battery SOC → Decreases during operation
When SOC < Threshold → var_SwapBattery_Refuel_ChargeBattery_Flag = True → Navigate to swap station
```

### proc_SpeedBatteryUpdates Logic
```
if prop_TruckMode == "BatterySwap":
    # Existing battery-only calculations
    BatteryPowerKw = MotorPowerKw / MotorEfficiency + AuxiliaryPowerKw
    BatteryEnergyDeltaKwh = BatteryPowerKw × TimeStep / 3600
    NewSOC = CurrentSOC - (EnergyDelta / EffectiveCapacity) × 100
    
    # Check swap threshold
    if NewSOC < prop_SwapBatterySOCPct:
        var_SwapBattery_Refuel_ChargeBattery_Flag = True
    
    # Electric path ignored - passes through as regular path
```

**Status:** ✅ Fully implemented and working

---

## Mode 2: DieselElectric

### Characteristics
- Diesel generator as primary energy source (always available)
- Interacts with `obj_ElectricPath` for trolley assist
- No battery swapping or depot charging
- Two assist modes: PreserveEnergy or IncreaseSpeed

### Key Properties
- `prop_TruckMode = "DieselElectric"`
- `prop_ElectricAssistMode = "PreserveEnergy" | "IncreaseSpeed"`
- `prop_DieselGeneratorMaxPowerKw` - Maximum diesel generator electrical output (kW)
- `prop_DieselGeneratorEfficiencyPct` - Generator efficiency percentage (typical 30-40%)
- `prop_DieselTankCapacityL` - Total diesel fuel tank capacity (liters)
- `prop_InitialDieselLevelL` - Initial fuel level at simulation start (liters)
- `prop_RefuelDieselLevelL` - Fuel level threshold to trigger refueling (liters)

### New State Variables

**Diesel Tank State:**
- `var_DieselLevelL` - Real, current diesel fuel level in tank (liters)
- `var_DieselLevelPct` - Real, current fuel level as percentage (0-100%)
- `var_AssignRefuelStationNode` - Node reference, assigned refuel station

**Diesel Energy Tracking:**
- `var_TotalDieselConsumedL` - Real, cumulative diesel fuel consumed (liters)
- `var_TotalDieselEnergyKwh` - Real, cumulative energy produced by diesel generator (kWh)
- `var_DieselEnergyPreservedKwh` - Real, diesel energy saved by trolley assist (kWh)
- `var_DieselFuelSavedL` - Real, diesel fuel saved by trolley assist (liters)

---

### Mode 2A: DieselElectric + PreserveEnergy

**Objective:** Minimize diesel consumption by letting trolley provide all driving energy (motor + auxiliary loads) when on electric path

**Note:** Total driving demand includes motor power AND auxiliary power (HVAC, lights, controls, etc.). Trolley serves total demand, preserving diesel fuel.

#### Energy Flow - On Electric Path
```
# Total demand includes motor + auxiliary
BaseDrivingDemandKw = (MotorPowerKw / MotorEfficiency) + AuxiliaryPowerKw

Trolley Available Power ≥ Driving Power Demand:
    TrolleyPowerKw = BaseDrivingDemandKw  // Trolley serves motor + auxiliary
    DieselPowerKw = 0                      // Diesel generator off/idle
    DieselEnergyPreservedKwh += (BaseDrivingDemandKw × TimeStep / 3600)
    
Trolley Available Power < Driving Power Demand:
    TrolleyPowerKw = TrolleyMaxPowerKw                    // Use max available
    DieselPowerKw = BaseDrivingDemandKw - TrolleyPowerKw  // Diesel supplements
    DieselEnergyPreservedKwh += (TrolleyPowerKw × TimeStep / 3600)
```

#### Energy Flow - Off Electric Path
```
DieselPowerKw = DrivingPowerDemand  // Diesel provides all energy
TrolleyPowerKw = 0
```

#### Tractive Force Calculation
```
# Calculate required motor power from driving resistance
RequiredMotorPowerKw = (TractiveForceN × SpeedMs) / 1000

# Determine energy sources
if OnElectricPath AND prop_ElectricAssistMode == "PreserveDiesel":
    if TrolleyMaxPowerKw >= RequiredMotorPowerKw:
        TrolleyPowerKw = RequiredMotorPowerKw
        DieselPowerKw = 0
    else:
        TrolleyPowerKw = TrolleyMaxPowerKw
        DieselPowerKw = RequiredMotorPowerKw - TrolleyPowerKw
else:
    DieselPowerKw = RequiredMotorPowerKw
    TrolleyPowerKw = 0

# Tractive force remains based on required power (speed unchanged from baseline)
# Energy source changes but performance characteristics don't
```

**Key Insight:** Speed/force calculations remain identical to diesel-only operation. Only the energy source accounting changes.

---

### Mode 2B: DieselElectric + IncreaseSpeed

**Objective:** Maximize performance by combining diesel and trolley power for higher speeds/forces

#### Physics Approach: Power-Limited Scaling Factor

**Design Decision:** Use **power-limited scaling** rather than new curves or direct curve scaling.

**Rationale:**
1. Existing rimpull/retard curves capture vehicle mechanical limits (tire adhesion, drivetrain capacity)
2. IncreaseSpeed mode changes **available power**, not fundamental vehicle mechanics
3. Power-limited approach respects both curve limits AND power limits
4. No new curve derivation required - reuses validated data
5. Physically accurate via Power = Force × Velocity relationship

**Alternatives Considered:**
- ❌ **New Curves:** Would require extensive data collection/validation for each truck+trolley combination
- ❌ **Direct Curve Scaling:** Simpler but assumes linear power-force relationship (not physically accurate at all speeds)
- ✅ **Power-Limited Scaling:** Combines curve reuse with physics accuracy

#### Energy Flow - On Electric Path
```
DieselPowerKw = DieselGeneratorMaxPowerKw      // Diesel at full output
TrolleyPowerKw = <calculated from power sharing>  // Dynamic based on active trucks
TotalAvailablePowerKw = DieselPowerKw + TrolleyPowerKw
```

#### Energy Flow - Off Electric Path
```
DieselPowerKw = DieselGeneratorMaxPowerKw  // Diesel only, limited performance
TrolleyPowerKw = 0
TotalAvailablePowerKw = DieselPowerKw
```

#### Tractive Force Calculation (Power-Limited Method)
```
# Step 1: Get baseline force from existing curves (unchanged)
BaseRimpullForceN = lookup_rimpull_curve(CurrentSpeedKmh, CurrentGrade, LoadState)
BaseRetardForceN = lookup_retard_curve(CurrentSpeedKmh, CurrentGrade, LoadState)

# Step 2: Determine total available power
if OnElectricPath AND prop_ElectricAssistMode == "IncreaseSpeed":
    TotalAvailablePowerKw = DieselGeneratorMaxPowerKw + TrolleyPowerKw  # Uses dynamic value
else:
    TotalAvailablePowerKw = DieselGeneratorMaxPowerKw

# Step 3: Apply power limit to curve-based force
if CurrentSpeedKmh < TargetSpeedKmh:
    # Accelerating - use minimum of curve limit and power limit
    SpeedMs = CurrentSpeedKmh / 3.6
    
    if SpeedMs > 0:
        PowerLimitedForceN = (TotalAvailablePowerKw × 1000) / SpeedMs
        TractiveForceN = min(BaseRimpullForceN, PowerLimitedForceN)
    else:
        TractiveForceN = BaseRimpullForceN  // At standstill, use curve value
else:
    # Braking - retard not affected by assist power
    TractiveForceN = -BaseRetardForceN

# Physics continues as normal with power-limited force capability
```

#### How Power Limiting Works at Different Speeds

**Low Speed (5 km/h on steep grade):**
- Curve rimpull: 800 kN (high force, low speed - tire adhesion limit)
- Power limit: (8000 kW × 1000) / 1.39 m/s = 5,755 kN
- **Result: Curve-limited** (800 kN used) - mechanical limits dominate

**Medium Speed (20 km/h on 8% grade):**
- Curve rimpull: 400 kN
- Power limit: (8000 kW × 1000) / 5.56 m/s = 1,439 kN
- **Result: Curve-limited** (400 kN used) - still within mechanical capability

**High Speed (35 km/h approaching max speed):**
- Curve rimpull: 150 kN
- Power limit: (8000 kW × 1000) / 9.72 m/s = 823 kN
- **Result: Curve-limited** (150 kN used)

**IncreaseSpeed Benefit:**
- Higher power enables **sustaining** higher speeds on grades where baseline truck would slow down
- Net effect: Faster average speed without violating mechanical constraints
- System naturally transitions between curve-limited (low speed) and power-limited (high speed) regimes

**Key Insight:** Power-limited scaling factor maintains physics accuracy while reusing existing validated curves. Trolley adds power capability, resulting in higher achievable speeds on grades.

---

## Mode 3: BatteryElectric

### Characteristics
- Battery as primary energy source (rechargeable, non-swappable)
- Charges at depot/pit charging stations between cycles
- Interacts with `obj_ElectricPath` for trolley assist AND charging
- Two assist modes: PreserveBattery or IncreaseSpeed

### Key Properties
- `prop_TruckMode = "BatteryElectric"`
- `prop_ElectricAssistMode = "PreserveBattery" | "IncreaseSpeed"`
- `prop_BatteryMaxChargePowerKw` - Maximum battery charging rate
- No swap-related properties (different from BatterySwap mode)

### New State Variables
- `var_TotalTrolleyEnergyKwh` - Cumulative trolley energy received
- `var_BatteryEnergyPreservedKwh` - Battery energy saved by trolley assist
- `var_TrolleyChargingEnergyKwh` - Energy charged to battery from trolley

---

### Mode 3A: BatteryElectric + PreserveEnergy

**Objective:** Preserve battery energy by using trolley for driving (motor + auxiliary) AND charge battery with excess trolley power

#### Energy Flow - On Electric Path

**Scenario 1: Trolley Power > Driving Demand (Surplus Available)**
```
# Total demand includes motor + auxiliary
DrivingPowerDemand = (MotorPowerKw / MotorEfficiency) + AuxiliaryPowerKw
TrolleyPowerKw = <calculated from power sharing>  // Dynamic based on active trucks

if TrolleyPowerKw > DrivingPowerDemand:
    # Trolley covers driving + charges battery
    TrolleyDrivingPowerKw = DrivingPowerDemand
    TrolleyChargingPowerKw = min(
        TrolleyPowerKw - DrivingPowerDemand,
        prop_BatteryMaxChargePowerKw,
        ChargePowerToReach100SOC  # Don't overcharge
    )
    
    # Battery receives charging power (negative = charging)
    NetBatteryPowerKw = -TrolleyChargingPowerKw
    BatterySOC → Increases
    
    var_BatteryEnergyPreservedKwh += TrolleyDrivingPowerKw × TimeStep / 3600
    var_TrolleyChargingEnergyKwh += TrolleyChargingPowerKw × TimeStep / 3600
```

**Scenario 2: Trolley Power < Driving Demand (Deficit)**
```
TrolleyDrivingPowerKw = TrolleyPowerKw  # Use dynamically calculated value
BatteryPowerKw = DrivingPowerDemand - TrolleyPowerKw  # Battery supplements

NetBatteryPowerKw = BatteryPowerKw  # Discharging
BatterySOC → Decreases (but less than without trolley)

var_BatteryEnergyPreservedKwh += TrolleyPowerKw × TimeStep / 3600
```

**Scenario 3: Trolley Power = Driving Demand (Perfect Match)**
```
TrolleyDrivingPowerKw = DrivingPowerDemand
NetBatteryPowerKw = 0  # Battery neither charges nor discharges
BatterySOC → Unchanged

var_BatteryEnergyPreservedKwh += DrivingPowerDemand × TimeStep / 3600
```

#### Energy Flow - Off Electric Path
```
BatteryPowerKw = DrivingPowerDemand  # Battery provides all energy
TrolleyPowerKw = 0
NetBatteryPowerKw = BatteryPowerKw
BatterySOC → Decreases
```

#### Tractive Force Calculation
```
# Calculate required motor power
RequiredMotorPowerKw = calculate_motor_power(speed, grade, weight)

# Determine energy sources and battery state
if OnElectricPath AND prop_ElectricAssistMode == "PreserveBattery":
    TrolleyPowerKw = TrolleyMaxPowerKw
    DrivingPowerDemand = RequiredMotorPowerKw + AuxiliaryPowerKw
    
    if TrolleyPowerKw >= DrivingPowerDemand:
        # Surplus: Trolley drives + charges battery
        TrolleyDrivingPowerKw = DrivingPowerDemand
        TrolleyChargingPowerKw = calculate_charging_power(
            TrolleyPowerKw - DrivingPowerDemand,
            prop_BatteryMaxChargePowerKw,
            CurrentSOC
        )
        NetBatteryPowerKw = -TrolleyChargingPowerKw  # Negative = charging
    else:
        # Deficit: Trolley helps, battery supplements
        TrolleyDrivingPowerKw = TrolleyPowerKw
        NetBatteryPowerKw = DrivingPowerDemand - TrolleyPowerKw  # Discharging
else:
    NetBatteryPowerKw = DrivingPowerDemand  # Battery-only operation

# Update battery SOC
BatteryEnergyDeltaKwh = NetBatteryPowerKw × TimeStep / 3600
NewSOC = CurrentSOC - (BatteryEnergyDeltaKwh / EffectiveCapacity) × 100

# Tractive force remains based on required power (speed unchanged from baseline)
```

**Key Insight:** Trolley can simultaneously power driving and charge battery. Energy accounting becomes critical - need to track trolley driving vs charging contributions separately.

---

### Mode 3B: BatteryElectric + IncreaseSpeed

**Objective:** Maximize performance by combining battery and trolley power for higher speeds/forces

#### Physics Approach: Power-Limited Scaling Factor (Same as DieselElectric)

**Design Decision:** Use **power-limited scaling** with battery degradation factor applied.

**Key Difference from DieselElectric:** Battery power capacity varies with SOC and health (PowerDegradationFactor), diesel is constant.

#### Energy Flow - On Electric Path
```
MaxBatteryPowerKw = BatteryMaxPowerKw × PowerDegradationFactor  // Degraded battery capacity
TrolleyPowerKw = TrolleyMaxPowerKw                               // Full trolley power
TotalAvailablePowerKw = MaxBatteryPowerKw + TrolleyPowerKw

# Battery discharges normally (no preservation)
NetBatteryPowerKw = BatteryContribution  # Positive = discharging
BatterySOC → Decreases
```

#### Energy Flow - Off Electric Path
```
MaxBatteryPowerKw = BatteryMaxPowerKw × PowerDegradationFactor  // Battery only, limited by degradation
TrolleyPowerKw = 0
TotalAvailablePowerKw = MaxBatteryPowerKw
```

#### Tractive Force Calculation (Power-Limited Method)
```
# Step 1: Get baseline force from existing curves (unchanged)
BaseRimpullForceN = lookup_rimpull_curve(CurrentSpeedKmh, CurrentGrade, LoadState)
BaseRetardForceN = lookup_retard_curve(CurrentSpeedKmh, CurrentGrade, LoadState)

# Step 2: Calculate power degradation factor
PowerDegradationFactor = calculate_degradation(BatteryHealth, prop_PowerDegradationActive)

# Step 3: Determine total available power
MaxBatteryPowerKw = BatteryMaxPowerKw × PowerDegradationFactor

if OnElectricPath AND prop_ElectricAssistMode == "IncreaseSpeed":
    TotalAvailablePowerKw = MaxBatteryPowerKw + TrolleyMaxPowerKw
else:
    TotalAvailablePowerKw = MaxBatteryPowerKw

# Step 4: Apply power limit to curve-based force
if CurrentSpeedKmh < TargetSpeedKmh:
    # Accelerating - use minimum of curve limit (with degradation) and power limit
    SpeedMs = CurrentSpeedKmh / 3.6
    CurveRimpullForceN = BaseRimpullForceN × PowerDegradationFactor
    
    if SpeedMs > 0:
        PowerLimitedForceN = (TotalAvailablePowerKw × 1000) / SpeedMs
        TractiveForceN = min(CurveRimpullForceN, PowerLimitedForceN)
    else:
        TractiveForceN = CurveRimpullForceN  // At standstill, use curve value
else:
    # Braking - retard affected by degradation
    TractiveForceN = -BaseRetardForceN × PowerDegradationFactor

# Step 5: Split actual power consumption between sources
ActualMotorPowerKw = (TractiveForceN × SpeedMs) / 1000

if OnElectricPath AND prop_ElectricAssistMode == "IncreaseSpeed":
    # Trolley-first strategy: Use trolley up to its max, battery supplements
    TrolleyContributionKw = min(TrolleyMaxPowerKw, ActualMotorPowerKw)
    BatteryContributionKw = ActualMotorPowerKw - TrolleyContributionKw
else:
    # Battery-only
    BatteryContributionKw = ActualMotorPowerKw
    TrolleyContributionKw = 0

# Step 6: Calculate net battery power for SOC update
NetBatteryPowerKw = BatteryContributionKw / MotorEfficiency + AuxiliaryPowerKw

# Track trolley contribution separately
var_TotalTrolleyEnergyKwh += TrolleyContributionKw × TimeStep / 3600
```

#### Example: Degraded Battery (80% Health) + Trolley Assist

**Without Trolley (Battery-only):**
- Max battery power: 4000 kW × 0.8 = 3200 kW
- At 20 km/h: Power limit = 3200 kW / 5.56 m/s = 575 kN
- Curve rimpull: 400 kN × 0.8 degradation = 320 kN
- **Result: Curve-limited** (320 kN used)

**With Trolley (IncreaseSpeed mode):**
- Total power: 3200 kW + 4000 kW = 7200 kW
- At 20 km/h: Power limit = 7200 kW / 5.56 m/s = 1295 kN
- Curve rimpull: 400 kN × 0.8 degradation = 320 kN
- **Result: Still curve-limited** (320 kN used), but can sustain higher speeds on grades

**Performance Benefit:**
- Trolley compensates for battery degradation
- Enables maintaining target speeds that degraded battery alone cannot achieve
- Battery contribution tracked separately for accurate SOC calculations

**Key Insight:** Power-limited scaling factor works seamlessly with battery degradation. Trolley adds power capability while respecting both mechanical limits (curves) and battery health constraints.

---

## Unified proc_SpeedBatteryUpdates Logic

### Design Principles

1. **Single Process:** All modes use one `proc_SpeedBatteryUpdates` process
2. **Mode Dispatch:** Early decision tree routes to mode-specific calculations
3. **Reusable Components:** Physics calculations shared across modes
4. **Energy Source Abstraction:** Generic "PowerSourceKw" calculated differently per mode
5. **Event-Driven Control:** Existing event system (SpeedUpdates_True/False, BatteryUpdates_True/False) remains unchanged

### High-Level Process Flow

```
proc_SpeedBatteryUpdates (Every 1 second):
    
    # ========== SECTION 1: DETECT MODE & PATH STATUS ==========
    TruckMode = prop_TruckMode  // "BatterySwap" | "DieselElectric" | "BatteryElectric"
    ElectricAssistMode = prop_ElectricAssistMode  // "PreserveEnergy" | "IncreaseSpeed"
    
    OnElectricPath = (Location.Parent.Is.obj_ElectricPath AND 
                      Location.Parent.obj_ElectricPath.prop_TrolleyAssistEnabled)
    
    if OnElectricPath:
        CurrentPath = Location.Parent.obj_ElectricPath
        
        # POWER SHARING CALCULATION (Model B - Recommended for 1km sections)
        ActiveTrucksOnSection = CurrentPath.NumberTravelers  // Simio built-in property
        
        if ActiveTrucksOnSection > 0:
            # Calculate shared power per truck
            TrolleySectionTotalPowerKw = CurrentPath.prop_TrolleySectionTotalPowerKw
            TrolleyMaxPowerPerTruckKw = CurrentPath.prop_TrolleyMaxPowerPerTruckKw
            
            SharedPowerPerTruckKw = TrolleySectionTotalPowerKw / ActiveTrucksOnSection
            
            # Limit by truck's pantograph rating
            AvailablePowerPerTruckKw = min(SharedPowerPerTruckKw, TrolleyMaxPowerPerTruckKw)
            
            # Apply system efficiency
            TrolleyEfficiency = CurrentPath.prop_TrolleyEfficiencyPct / 100
            TrolleyPowerKw = AvailablePowerPerTruckKw × TrolleyEfficiency
        else:
            TrolleyPowerKw = 0
        
        # ALTERNATIVE: FIXED POWER (Model A - Simple, not recommended for 1km)
        # TrolleyPowerKw = CurrentPath.prop_TrolleyMaxPowerKw × (CurrentPath.prop_TrolleyEfficiencyPct / 100)
    else:
        TrolleyPowerKw = 0
    
    
    # ========== SECTION 2: CALCULATE DRIVING REQUIREMENTS (COMMON) ==========
    # Shared physics - all modes need this
    CurrentSpeedKmh = Movement.Rate
    CurrentGrade = Movement.Pitch
    CurrentWeightKg = Payload if Loaded else EmptyWeight
    
    # Resistance forces (common to all modes)
    GradeResistanceN = CurrentWeightKg × 9.81 × CurrentGrade / 100
    RollingResistanceN = CurrentWeightKg × 9.81 × RollingResistanceCoeff
    TotalResistanceN = GradeResistanceN + RollingResistanceN
    
    # Target speed (common to all modes)
    MaxSpeedKmh = MaxSpeedKmh_Loaded if Loaded else MaxSpeedKmh_Empty
    TargetSpeedKmh = min(PathSpeedLimit, MaxSpeedKmh)
    
    
    # ========== SECTION 3: MODE-SPECIFIC POWER & FORCE CALCULATION ==========
    
    if TruckMode == "BatterySwap":
        # ===== BatterySwap Mode (Existing Logic) =====
        # Ignores electric paths, battery-only operation
        
        PowerDegradationFactor = calculate_degradation(BatteryHealth, prop_PowerDegradationActive)
        
        if CurrentSpeedKmh < TargetSpeedKmh:
            TractiveForceN = BaseRimpullForceN × PowerDegradationFactor
        else:
            TractiveForceN = -BaseRetardForceN × PowerDegradationFactor
        
        NetForceN = TractiveForceN - TotalResistanceN
        AccelerationMs2 = NetForceN / CurrentWeightKg
        NewSpeedKmh = clamp(CurrentSpeedKmh + Acceleration × TimeStep × 3600, 0, MaxSpeedKmh)
        Movement.Rate = NewSpeedKmh
        
        # Energy accounting
        SpeedMs = NewSpeedKmh / 3.6
        MotorMechanicalPowerKw = TractiveForceN × SpeedMs / 1000
        
        if MotorMechanicalPowerKw > 0:
            BatteryPowerKw = MotorMechanicalPowerKw / MotorEfficiency + AuxiliaryPowerKw
        else:
            BatteryPowerKw = MotorMechanicalPowerKw × RegenEfficiency
        
        # Update battery (existing logic)
        BatteryEnergyDeltaKwh = BatteryPowerKw × TimeStep / 3600
        NewSOC = CurrentSOC - (BatteryEnergyDeltaKwh / EffectiveCapacity) × 100
        Battery.BatterySOCPct = clamp(NewSOC, 0, 100)
        
        # Check swap threshold
        if NewSOC < prop_SwapBatterySOCPct:
            var_SwapBattery_Refuel_ChargeBattery_Flag = True
        
        # Degradation update (existing logic)
        update_battery_degradation(abs(BatteryEnergyDeltaKwh))
    
    
    elif TruckMode == "DieselElectric":
        # ===== DieselElectric Mode =====
        
        # Calculate baseline required power
        if CurrentSpeedKmh < TargetSpeedKmh:
            BaseTractiveForceN = BaseRimpullForceN
        else:
            BaseTractiveForceN = -BaseRetardForceN
        
        SpeedMs = CurrentSpeedKmh / 3.6
        BaseMotorPowerKw = BaseTractiveForceN × SpeedMs / 1000
        BaseDrivingDemandKw = BaseMotorPowerKw / MotorEfficiency + AuxiliaryPowerKw
        
        # Determine power sources based on assist mode
        if OnElectricPath:
            if ElectricAssistMode == "PreserveEnergy":
                # Trolley takes over motor + auxiliary, diesel backs off
                # Handle both driving (positive demand) and retarding (negative motor power)
                
                if BaseDrivingDemandKw > 0:
                    # Driving: Trolley serves total demand (motor + auxiliary)
                    TrolleyPowerKw = min(TrolleyPowerKw, BaseDrivingDemandKw)  # Dynamic value
                    DieselPowerKw = max(0, BaseDrivingDemandKw - TrolleyPowerKw)
                else:
                    # Retarding: Motor negative, but auxiliary still needed
                    TrolleyPowerKw = min(TrolleyPowerKw, AuxiliaryPowerKw)  # Serve auxiliary only
                    DieselPowerKw = max(0, AuxiliaryPowerKw - TrolleyPowerKw)
                
                # Force/speed unchanged from baseline
                TractiveForceN = BaseTractiveForceN
                
                var_DieselEnergyPreservedKwh += TrolleyPowerKw × TimeStep / 3600
            
            elif ElectricAssistMode == "IncreaseSpeed":
                # Combine diesel + trolley for max power, respect motor limit
                CombinedSourcePowerKw = DieselGeneratorMaxPowerKw + TrolleyPowerKw  # Dynamic
                AvailableMotorPowerKw = Min(CombinedSourcePowerKw, MaxMotorPowerKw)  # Motor constraint
                
                if SpeedMs > 0:
                    PowerLimitForceN = (AvailableMotorPowerKw × 1000) / SpeedMs
                else:
                    PowerLimitForceN = BaseRimpullForceN  # At standstill, use curve
                
                if CurrentSpeedKmh < TargetSpeedKmh:
                    TractiveForceN = min(BaseRimpullForceN, PowerLimitForceN)
                else:
                    TractiveForceN = -BaseRetardForceN
                
                # Actual power consumed by motors (limited by motor capacity)
                ActualMotorPowerKw = (TractiveForceN × SpeedMs) / 1000
                ActualDrivingDemandKw = ActualMotorPowerKw / MotorEfficiency + AuxiliaryPowerKw
                
                # Split: Trolley-first, diesel supplements
                TrolleyContributionKw = min(TrolleyPowerKw, ActualDrivingDemandKw)
                DieselContributionKw = ActualDrivingDemandKw - TrolleyContributionKw
                
                DieselPowerKw = DieselContributionKw
                var_TotalTrolleyEnergyKwh += TrolleyContributionKw × TimeStep / 3600
        else:
            # Off electric path - diesel only
            TractiveForceN = BaseTractiveForceN
            DieselPowerKw = BaseDrivingDemandKw
            TrolleyPowerKw = 0
        
        # Physics update (common)
        NetForceN = TractiveForceN - TotalResistanceN
        AccelerationMs2 = NetForceN / CurrentWeightKg
        NewSpeedKmh = clamp(CurrentSpeedKmh + Acceleration × TimeStep × 3600, 0, MaxSpeedKmh)
        Movement.Rate = NewSpeedKmh
        
        # Energy accounting
        var_TotalDieselEnergyKwh += DieselPowerKw × TimeStep / 3600
        var_TotalTrolleyEnergyKwh += TrolleyPowerKw × TimeStep / 3600
    
    
    elif TruckMode == "BatteryElectric":
        # ===== BatteryElectric Mode =====
        
        PowerDegradationFactor = calculate_degradation(BatteryHealth, prop_PowerDegradationActive)
        
        # Calculate baseline required power
        if CurrentSpeedKmh < TargetSpeedKmh:
            BaseTractiveForceN = BaseRimpullForceN × PowerDegradationFactor
        else:
            BaseTractiveForceN = -BaseRetardForceN × PowerDegradationFactor
        
        SpeedMs = CurrentSpeedKmh / 3.6
        BaseMotorPowerKw = BaseTractiveForceN × SpeedMs / 1000
        BaseDrivingDemandKw = BaseMotorPowerKw / MotorEfficiency + AuxiliaryPowerKw
        
        # Determine power sources based on assist mode
        if OnElectricPath:
            if ElectricAssistMode == "PreserveEnergy":
                # Trolley takes over motor + auxiliary, excess charges battery
                # Handle both driving (positive) and retarding (negative motor power)
                
                if BaseDrivingDemandKw > 0:
                    # Driving: Trolley serves total demand, surplus charges battery
                    TrolleyDrivingPowerKw = min(TrolleyPowerKw, BaseDrivingDemandKw)  # Dynamic
                else:
                    # Retarding: Regen power + trolley can charge battery
                    # Motor returns energy, auxiliary still needed
                    TrolleyDrivingPowerKw = min(TrolleyPowerKw, AuxiliaryPowerKw)  # Serve auxiliary
                    # Regen energy flows to battery automatically (negative motor power)
                
                if BaseDrivingDemandKw > 0 and TrolleyPowerKw > BaseDrivingDemandKw:
                    # Surplus - charge battery
                    SurplusPowerKw = TrolleyPowerKw - BaseDrivingDemandKw
                    PowerToFullChargeKw = (100 - CurrentSOC) / 100 × EffectiveCapacity / (TimeStep / 3600)
                    
                    TrolleyChargingPowerKw = min(
                        SurplusPowerKw,
                        prop_BatteryMaxChargePowerKw,
                        PowerToFullChargeKw
                    )
                    
                    NetBatteryPowerKw = -TrolleyChargingPowerKw  # Negative = charging
                    var_TrolleyChargingEnergyKwh += TrolleyChargingPowerKw × TimeStep / 3600
                
                elif TrolleyPowerKw < BaseDrivingDemandKw:
                    # Deficit - battery supplements
                    NetBatteryPowerKw = BaseDrivingDemandKw - TrolleyDrivingPowerKw
                else:
                    # Perfect match
                    NetBatteryPowerKw = 0
                
                # Force/speed unchanged from baseline
                TractiveForceN = BaseTractiveForceN
                
                var_BatteryEnergyPreservedKwh += TrolleyDrivingPowerKw × TimeStep / 3600
                var_TotalTrolleyEnergyKwh += TrolleyPowerKw × TimeStep / 3600  # Track actual available
            
            elif ElectricAssistMode == "IncreaseSpeed":
                # Combine battery + trolley for max power, respect motor limit
                MaxBatteryPowerKw = calculate_max_battery_power(CurrentSOC, BatteryHealth, PowerDegradationFactor)
                CombinedSourcePowerKw = MaxBatteryPowerKw + TrolleyPowerKw  # Dynamic
                AvailableMotorPowerKw = Min(CombinedSourcePowerKw, MaxMotorPowerKw)  # Motor constraint
                
                if SpeedMs > 0:
                    PowerLimitForceN = (AvailableMotorPowerKw × 1000) / SpeedMs
                else:
                    PowerLimitForceN = BaseRimpullForceN × PowerDegradationFactor
                
                if CurrentSpeedKmh < TargetSpeedKmh:
                    TractiveForceN = min(BaseRimpullForceN × PowerDegradationFactor, PowerLimitForceN)
                else:
                    TractiveForceN = -BaseRetardForceN × PowerDegradationFactor
                
                # Actual power used (limited by motor capacity)
                ActualMotorPowerKw = (TractiveForceN × SpeedMs) / 1000
                ActualDrivingDemandKw = ActualMotorPowerKw / MotorEfficiency + AuxiliaryPowerKw
                
                # Split: Trolley-first, battery supplements
                TrolleyContributionKw = min(TrolleyPowerKw, ActualDrivingDemandKw)
                BatteryContributionKw = ActualDrivingDemandKw - TrolleyContributionKw
                
                NetBatteryPowerKw = BatteryContributionKw  # Positive = discharging
                var_TotalTrolleyEnergyKwh += TrolleyContributionKw × TimeStep / 3600
        else:
            # Off electric path - battery only
            TractiveForceN = BaseTractiveForceN
            NetBatteryPowerKw = BaseDrivingDemandKw
        
        # Physics update (common)
        NetForceN = TractiveForceN - TotalResistanceN
        AccelerationMs2 = NetForceN / CurrentWeightKg
        NewSpeedKmh = clamp(CurrentSpeedKmh + Acceleration × TimeStep × 3600, 0, MaxSpeedKmh)
        Movement.Rate = NewSpeedKmh
        
        # Battery SOC update
        BatteryEnergyDeltaKwh = NetBatteryPowerKw × TimeStep / 3600
        NewSOC = CurrentSOC - (BatteryEnergyDeltaKwh / EffectiveCapacity) × 100
        Battery.BatterySOCPct = clamp(NewSOC, 0, 100)
        
        # Degradation update (only battery discharge/charge counts)
        update_battery_degradation(abs(BatteryEnergyDeltaKwh))
    
    # End of mode dispatch
```

**Key Design Features:**
1. **Early mode detection** - Single decision point at start
2. **Shared physics** - Resistance, acceleration, speed update common to all
3. **Energy source abstraction** - Each mode calculates its own power sources
4. **Minimal code duplication** - Reuse common calculations
5. **Clear energy accounting** - Each mode tracks its specific energy variables

---

## Property and State Variable Summary

### Required Properties (obj_BatteryElectricTruck)

| Property                            | Type        | Values                                             | Used By Modes                   |
| ----------------------------------- | ----------- | -------------------------------------------------- | ------------------------------- |
| `prop_TruckMode`                    | String/List | "BatterySwap", "DieselElectric", "BatteryElectric" | All                             |
| `prop_ElectricAssistMode`           | String/List | "PreserveEnergy", "IncreaseSpeed"                  | DieselElectric, BatteryElectric |
| `prop_SwapBatterySOCPct`            | Real        | 0-100%                                             | BatterySwap                     |
| `prop_DieselTankCapacityL`          | Real        | Liters (e.g., 3000)                                | DieselElectric                  |
| `prop_InitialDieselLevelL`          | Real        | Liters (e.g., 3000)                                | DieselElectric                  |
| `prop_RefuelDieselLevelL`           | Real        | Liters (e.g., 300)                                 | DieselElectric                  |
| `prop_DieselGeneratorMaxPowerKw`    | Real        | kW (e.g., 2539)                                    | DieselElectric                  |
| `prop_DieselGeneratorEfficiencyPct` | Real        | % (e.g., 35)                                       | DieselElectric                  |
| `prop_BatteryMaxChargePowerKw`      | Real        | kW                                                 | BatteryElectric                 |
| `prop_PowerDegradationActive`       | Boolean     | True/False                                         | BatterySwap, BatteryElectric    |

**Note:** Existing properties remain unchanged - new properties add capabilities without breaking existing logic.

---

### Required Properties (tbl_TruckTypes)

**New columns to be added for power management:**

| Property                    | Type | TONLY_DTE145_BatterySwap | CAT_794AC_DieselElectric | CAT_793XE_BatteryElectric | Description                                                         |
| --------------------------- | ---- | ------------------------ | ------------------------ | ------------------------- | ------------------------------------------------------------------- |
| `MaxMotorPowerKw`           | Real | 1,800                    | 1,800                    | 1,800                     | Electric motor peak power (kW) - Physical constraint for all trucks |
| `MaxBatteryPowerKw`         | Real | 0                        | 0                        | 1,800                     | Battery discharge power (kW) - BatteryElectric only                 |
| `DieselGeneratorMaxPowerKw` | Real | 0                        | 2,539                    | 0                         | Diesel generator electrical output (kW) - DieselElectric only       |

**Key Architecture Principles:**

1. **MaxMotorPowerKw is the physical limit** - All trucks use Dual LegoEM620-900 motors (2 × 900 kW peak = 1,800 kW)
2. **Power Source vs Motor Constraint:**
   - DieselElectric: Generator produces 2,539 kW, but **motors limit to 1,800 kW** (excess for losses/auxiliaries)
   - BatteryElectric: Battery must deliver 1,800 kW to match motor rating
   - BatterySwap: No trolley interaction, motor-limited only
3. **IncreaseSpeed Mode Logic:**
   ```
   CombinedSourcePowerKw = OnboardPowerKw + TrolleyPowerKw
   AvailableMotorPowerKw = Min(CombinedSourcePowerKw, MaxMotorPowerKw)
   PowerLimitForceN = (AvailableMotorPowerKw × 1000) / SpeedMs
   TractiveForceN = Min(CurveLimitForceN, PowerLimitForceN)
   ```
4. **PreserveEnergy Mode Logic:** No motor limit needed (trolley substitutes, doesn't add)

---

### Required Properties (obj_ElectricPath)

**For Power Sharing Implementation (Model B - Recommended):**

| Property                          | Type    | Default                        | Description                                                   |
| --------------------------------- | ------- | ------------------------------ | ------------------------------------------------------------- |
| `prop_RoadFrictionCoefficient`    | Real    | 0.7                            | Surface friction coefficient μ for traction limits            |
| `prop_TrolleyAssistEnabled`       | Boolean | `tbl_Paths.ElectricAssistPath` | Enable/disable trolley for this path                          |
| `prop_TrolleySectionTotalPowerKw` | Real    | 10000                          | Total substation/section capacity (kW) - Aitik verified       |
| `prop_TrolleyMaxPowerPerTruckKw`  | Real    | 5000                           | Individual truck pantograph limit (kW) - CAT 795F AC verified |
| `prop_TrolleyMaxConcurrentTrucks` | Integer | 6                              | Physical capacity (path length / min spacing)                 |
| `prop_TrolleyVoltageV`            | Real    | 1200                           | System voltage (V) - historical verified                      |
| `prop_TrolleyEfficiencyPct`       | Real    | 93                             | Power delivery efficiency (%)                                 |

**For Fixed Power Implementation (Model A - Simple):**

| Property                          | Type    | Default                        | Description                                        |
| --------------------------------- | ------- | ------------------------------ | -------------------------------------------------- |
| `prop_RoadFrictionCoefficient`    | Real    | 0.7                            | Surface friction coefficient μ for traction limits |
| `prop_TrolleyAssistEnabled`       | Boolean | `tbl_Paths.ElectricAssistPath` | Enable/disable trolley for this path               |
| `prop_TrolleyMaxPowerKw`          | Real    | 4000                           | Fixed power per truck (kW)                         |
| `prop_TrolleyMaxConcurrentTrucks` | Integer | 3                              | Capacity limit (fixed)                             |
| `prop_TrolleyVoltageV`            | Real    | 1200                           | System voltage (V)                                 |
| `prop_TrolleyEfficiencyPct`       | Real    | 93                             | Power delivery efficiency (%)                      |

**Recommendation:** Use **Model B (Power Sharing)** for realistic 1 km trolley section behavior.

**Typical Values for 1 km Section (CAT 794/795 class, 360-400 ton):**
- Section total power: 10-12 MW (10 MW recommended - verified Aitik mine)
- Per truck max: 4.5-5 MW (5 MW recommended - verified CAT 795F AC)
- Max concurrent: 6 trucks (based on 150-200m spacing)
- Voltage: 1200V DC (verified at some mines, modern systems may vary)
- Efficiency: 90-95% (93% typical)
- Real-world verified: Aitik mine (10 MW, CAT 795F AC fleet, 4.5+ MW per truck)

---

### Required State Variables (obj_BatteryElectricTruck)

#### Existing Variables (Keep)
- `var_Loaded` - Boolean, true when loaded
- `var_Payload` - Real, current payload weight
- `var_SpeedUpdates` - Boolean, enable/disable speed calculations
- `var_BatteryUpdates` - Boolean, enable/disable battery calculations
- `var_SwapBattery_Refuel_ChargeBattery_Flag` - Boolean, trigger service operation (unified for all modes)
- `var_AssignBatterySwapChargeStationNode` - Node reference (BatterySwap mode only)

#### New Variables Required

**For DieselElectric Mode:**
- `var_DieselLevelL` - Real, current diesel fuel level in tank (liters)
- `var_DieselLevelPct` - Real, current fuel level as percentage (0-100%)
- `var_TotalDieselConsumedL` - Real, cumulative diesel fuel consumed (liters)
- `var_TotalDieselEnergyKwh` - Real, cumulative energy produced by diesel generator (kWh)
- `var_DieselEnergyPreservedKwh` - Real, diesel energy saved by trolley assist (kWh)
- `var_DieselFuelSavedL` - Real, diesel fuel saved by trolley assist (liters)
- `var_AssignRefuelStationNode` - Node reference, assigned refuel station

**For BatteryElectric Mode:**
- `var_BatteryEnergyPreservedKwh` - Real, battery energy saved by trolley assist
- `var_TrolleyChargingEnergyKwh` - Real, energy charged to battery from trolley

**Common to DieselElectric and BatteryElectric:**
- `var_TotalTrolleyEnergyKwh` - Real, cumulative trolley energy received
- `var_TrolleyAssistActive` - Boolean, currently on electric path with assist active
- `var_TrolleyPowerKw` - Real, current trolley power being supplied

---

### Token Variables (tkn_proc_SpeedBatteryUpdates)

**Existing token variables** (keep all 35):
- CurrentSpeedKmh, CurrentGrade, CurrentWeightKg, etc.

**New token variables** (add ~26):
- `TruckMode` - String, current truck mode
- `ElectricAssistMode` - String, current assist mode
- `OnElectricPath` - Boolean, path detection
- `ActiveTrucksOnSection` - Integer, count of trucks on current electric path
- `TrolleySectionTotalPowerKw` - Real, total section capacity
- `TrolleyMaxPowerPerTruckKw` - Real, individual truck limit
- `SharedPowerPerTruckKw` - Real, section power divided by active trucks
- `AvailablePowerPerTruckKw` - Real, min(shared power, truck limit)
- `TrolleyPowerKw` - Real, available trolley power after efficiency
- `BaseDrivingDemandKw` - Real, baseline power requirement
- `TrolleyDrivingPowerKw` - Real, trolley power for driving
- `TrolleyChargingPowerKw` - Real, trolley power for charging (BatteryElectric)
- `DieselPowerKw` - Real, diesel generator output (DieselElectric)
- `DieselLevelL` - Real, current diesel level (liters)
- `DieselLevelPct` - Real, current diesel level (percentage)
- `DieselFuelInputPowerKw` - Real, diesel fuel energy input rate (kW)
- `DieselConsumptionRateLPerSecond` - Real, fuel consumption rate (L/s)
- `DieselConsumedL` - Real, fuel consumed this timestep (L)
- `DieselEnergySavedKwh` - Real, diesel energy saved by trolley (kWh)
- `DieselFuelSavedL` - Real, diesel fuel saved by trolley (L)
- `NetBatteryPowerKw` - Real, net battery power (positive=discharge, negative=charge)
- `BatteryContributionKw` - Real, battery's share of power
- `TrolleyContributionKw` - Real, trolley's share of power
- `TotalAvailablePowerKw` - Real, combined power (IncreaseSpeed modes)
- `MaxTractiveForceN` - Real, force limit from available power
- `PowerToFullChargeKw` - Real, power needed to reach 100% SOC
- `SurplusPowerKw` - Real, excess trolley power available for charging

**Token variable strategy:** Use token variables for intermediate calculations within the process, state variables for values that need to persist between timesteps.

---

## Event System Integration

### Existing Events (Keep Unchanged)
- `event_SpeedUpdates_True` - Enable speed calculations
- `event_SpeedUpdates_False` - Disable speed calculations (collision handling)
- `event_BatteryUpdates_True` - Enable battery calculations
- `event_BatteryUpdates_False` - Disable battery calculations
- `event_Loaded_True` - Set loaded state
- `event_Loaded_False` - Set empty state
- `event_OnRunInitialised` - Initialize truck at simulation start
- `event_OnRunEnding` - Cleanup at simulation end

### New Events (Optional)

**For path interaction:**
- `event_ElectricPathEntered` - Fired when entering obj_ElectricPath
- `event_ElectricPathExited` - Fired when exiting obj_ElectricPath

**For mode transitions (future flexibility):**
- `event_TruckModeChanged` - Mode switch notification
- `event_AssistModeChanged` - Assist mode switch notification

**Note:** Path detection can be handled within `proc_SpeedBatteryUpdates` without new events, keeping it simpler. Events are optional for logging/statistics.

---

## Unified Service Flag System

### var_SwapBattery_Refuel_ChargeBattery_Flag

**Purpose:** Single unified flag variable that triggers service operations for all three truck modes, reducing code complexity and maintaining consistent behavior.

**Flag Behavior by Mode:**

| Truck Mode          | Trigger Condition                              | Service Destination                      | Service Action                                 |
| ------------------- | ---------------------------------------------- | ---------------------------------------- | ---------------------------------------------- |
| **BatterySwap**     | `var_BatterySOCPct < prop_SwapBatterySOCPct`   | `var_AssignBatterySwapChargeStationNode` | Battery swap at `obj_BatterySwapChargeStation` |
| **DieselElectric**  | `var_DieselLevelL < prop_RefuelDieselLevelL`   | `var_AssignRefuelStationNode`            | Diesel refuel at `obj_DieselRefuelStation`     |
| **BatteryElectric** | `var_BatterySOCPct < prop_ChargeBatterySOCPct` | `var_AssignDepotChargeStationNode`       | Battery charge at depot charging station       |

**Implementation Logic:**

```pseudocode
# In proc_SpeedBatteryUpdates, after energy calculations:

if prop_TruckMode == "BatterySwap":
    if var_BatterySOCPct < prop_SwapBatterySOCPct:
        var_SwapBattery_Refuel_ChargeBattery_Flag = True
        # Truck navigation logic uses var_AssignBatterySwapChargeStationNode
        
elif prop_TruckMode == "DieselElectric":
    if var_DieselLevelL < prop_RefuelDieselLevelL:
        var_SwapBattery_Refuel_ChargeBattery_Flag = True
        # Truck navigation logic uses var_AssignRefuelStationNode
        
elif prop_TruckMode == "BatteryElectric":
    if var_BatterySOCPct < prop_ChargeBatterySOCPct:
        var_SwapBattery_Refuel_ChargeBattery_Flag = True
        # Truck navigation logic uses var_AssignDepotChargeStationNode
```

**Service Station Reset:**
Each service station (swap/refuel/charge) is responsible for resetting the flag to `False` after service completion:

```pseudocode
# At end of service process (swap/refuel/charge):
ParentObject.obj_BatteryElectricTruck.var_SwapBattery_Refuel_ChargeBattery_Flag = False
# Release truck to resume normal operations
```

**Benefits:**
- ✅ **Single flag variable** - Reduces state variable count and complexity
- ✅ **Consistent pattern** - Same flag semantics across all three modes
- ✅ **Mode-specific destinations** - Each mode navigates to its appropriate service location
- ✅ **Backward compatible** - BatterySwap mode behavior unchanged
- ✅ **Clear responsibility** - Service stations own flag reset logic

---

## Trolley Power Sharing for 1 km Sections

### Real-World Trolley System Behavior

Mining trolley systems typically span 0.5-2 km sections with **shared power infrastructure**. As multiple trucks connect to the same section, available power per truck decreases due to:
- Transformer/substation capacity limits
- Voltage drop along the catenary
- Current capacity of overhead lines

**For a 1 km trolley section**, typical characteristics:

| Parameter                   | Typical Value | Notes                                                     |
| --------------------------- | ------------- | --------------------------------------------------------- |
| Section Length              | 1,000 m       | Single continuous electrical section                      |
| Section Total Power         | 10-12 MW      | Substation/transformer capacity (ABB highest: 12 MW)      |
| Trucks on Section (typical) | 1-2           | At 30 km/h avg speed, ~2 min transit time                 |
| Trucks on Section (peak)    | 3-4           | Busy periods                                              |
| Truck Spacing (minimum)     | 150-200 m     | Safe following distance                                   |
| Max Concurrent Trucks       | 6             | Physical capacity (1000m / 167m spacing)                  |
| Power Per Truck (1 truck)   | 10-12 MW      | Limited by truck pantograph rating (5 MW for CAT 795F AC) |
| Power Per Truck (2 trucks)  | 5-6 MW        | Typical operating scenario                                |
| Power Per Truck (3 trucks)  | 3.3-4 MW      | Section capacity divided                                  |
| Power Per Truck (4 trucks)  | 2.5-3 MW      | Peak traffic                                              |
| Power Per Truck (6 trucks)  | 1.7-2 MW      | Maximum capacity, degraded performance                    |

### Power Distribution Models

#### Model A: Fixed Power (Simple, Conservative)

**Design:** First N trucks get full power, additional trucks queue

```
prop_TrolleyMaxPowerKw = 4000  // Fixed power per truck
prop_TrolleyMaxConcurrentTrucks = 3  // Capacity limit
InitialTravelerCapacity = 3  // Simio path capacity
```

**Behavior:**
- Truck 1, 2, 3: Each gets 4 MW
- Truck 4+: Waits at section entrance

**Pros:** Simple, predictable, already designed
**Cons:** Unrealistic queuing, doesn't utilize full section capacity

---

#### Model B: Power Sharing (Realistic, Recommended)

**Design:** Total section power divided among active trucks

**obj_ElectricPath Properties:**
```
prop_TrolleySectionTotalPowerKw = 10000  // Total substation capacity (10 MW - matches Aitik)
prop_TrolleyMaxPowerPerTruckKw = 5000    // Truck pantograph rating (5 MW - verified CAT 795F AC)
prop_TrolleyMaxConcurrentTrucks = 6      // Physical spacing limit (~167m spacing)
prop_TrolleyEfficiencyPct = 93           // System efficiency (90-95% typical)
InitialTravelerCapacity = 6              // Allow up to 6 trucks simultaneously
```

**Dynamic Calculation (in proc_SpeedBatteryUpdates):**
```python
if Location.Parent.Is.obj_ElectricPath:
    CurrentPath = Location.Parent.obj_ElectricPath
    
    if CurrentPath.prop_TrolleyAssistEnabled:
        # Count trucks currently on this section
        ActiveTrucksOnSection = CurrentPath.NumberTravelers  // Simio built-in
        
        # Calculate shared power per truck
        if ActiveTrucksOnSection > 0:
            SharedPowerPerTruckKw = CurrentPath.prop_TrolleySectionTotalPowerKw / ActiveTrucksOnSection
            
            # Limit by truck's pantograph rating
            AvailablePowerPerTruckKw = min(
                SharedPowerPerTruckKw,
                CurrentPath.prop_TrolleyMaxPowerPerTruckKw
            )
        else:
            AvailablePowerPerTruckKw = 0
        
        # Apply efficiency
        TrolleyPowerKw = AvailablePowerPerTruckKw × (CurrentPath.prop_TrolleyEfficiencyPct / 100)
```

**Example Scenarios (10 MW section, 5 MW truck limit - verified real-world config):**

| Trucks on 1km Section | Section Capacity | Shared Power | Truck Limit | **Actual Power per Truck**   | Real-World Scenario           |
| --------------------- | ---------------- | ------------ | ----------- | ---------------------------- | ----------------------------- |
| 1                     | 10 MW            | 10 MW        | 5 MW        | **5 MW** (truck-limited)     | Typical - optimal performance |
| 2                     | 10 MW            | 5 MW         | 5 MW        | **5 MW** (truck-limited)     | Typical - optimal performance |
| 3                     | 10 MW            | 3.3 MW       | 5 MW        | **3.3 MW** (section-limited) | Peak traffic                  |
| 4                     | 10 MW            | 2.5 MW       | 5 MW        | **2.5 MW** (section-limited) | Peak traffic                  |
| 5                     | 10 MW            | 2 MW         | 5 MW        | **2 MW** (section-limited)   | Heavy traffic                 |
| 6                     | 10 MW            | 1.7 MW       | 5 MW        | **1.7 MW** (section-limited) | Maximum capacity              |

**Pros:** 
- Realistic power sharing behavior (matches industry practice)
- No artificial queuing - all trucks can enter section
- Graceful performance degradation
- Simple implementation (one division operation)

**Cons:**
- Performance varies dynamically based on other trucks
- Need to track active truck count

---

#### Model C: Tiered Power Levels (Lookup-Based)

**Design:** Stepped power reduction based on truck count

```
prop_TrolleyMaxConcurrentTrucks = 6
prop_TrolleyPowerTable:
  1 truck  → 6000 kW per truck
  2 trucks → 6000 kW per truck
  3 trucks → 4000 kW per truck
  4 trucks → 3000 kW per truck
  5 trucks → 2400 kW per truck
  6 trucks → 2000 kW per truck
```

**Pros:** Can calibrate to field measurements, realistic stepped behavior
**Cons:** Less flexible than Model B, requires data table

---

### Recommended Configuration for 1 km Trolley Section

**For typical haul road uphill section (1 km, 6-8% grade) - CAT 794/795 class trucks:**

```
obj_ElectricPath: "TrolleyUphill_1km"
  # Power capacity (based on verified Aitik mine & CAT 795F AC specs)
  prop_TrolleySectionTotalPowerKw = 10000    // 10 MW substation (matches Aitik)
  prop_TrolleyMaxPowerPerTruckKw = 5000      // 5 MW pantograph limit (CAT 795F AC: 4.5+ MW)
  
  # Physical capacity (1000m / 167m spacing = 6 trucks max)
  prop_TrolleyMaxConcurrentTrucks = 6
  InitialTravelerCapacity = 6
  
  # System characteristics
  prop_TrolleyVoltageV = 1200                // 1.2 kV DC (historical verified, modern may vary)
  prop_TrolleyEfficiencyPct = 93             // 90-95% typical
  prop_RoadFrictionCoefficient = 0.7         // Dry gravel road surface
  
  # Path properties
  SpeedLimit = 30                            // km/h (grade-limited)
  Length = 1000                              // meters
```

### Transit Time and Truck Density Analysis

**Scenario: 30 km/h average speed on 1 km section**

| Metric                     | Value       | Calculation                |
| -------------------------- | ----------- | -------------------------- |
| Transit time               | 2 minutes   | 1 km / 30 km/h = 2 min     |
| Truck headway (typical)    | 3-5 minutes | Fleet cycle time dependent |
| Expected trucks on section | 1-2         | Most common                |
| Peak trucks on section     | 3-4         | During busy periods        |
| Maximum physical trucks    | 6           | 150m spacing minimum       |

**Typical Operating Scenarios:**

**Light Traffic (1-2 trucks) - TYPICAL:**
- Power per truck: 5 MW (truck-limited, full performance)
- No sharing effects - each truck gets maximum power
- Optimal trolley benefit (matches Aitik operations)
- Real-world: Most common scenario based on 2 min transit time

**Moderate Traffic (3-4 trucks) - PEAK:**
- Power per truck: 2.5-3.3 MW (section-limited)
- Noticeable but acceptable performance reduction
- Still significant trolley benefit vs battery/diesel-only
- Real-world: Busy period operations

**Heavy Traffic (5-6 trucks) - MAXIMUM:**
- Power per truck: 1.7-2 MW (section-limited)
- Reduced performance but still beneficial (better than no trolley)
- May need fleet management to optimize spacing
- Real-world: Rare, represents physical capacity limit

### Implementation Impact on Modes

**For PreserveEnergy mode:**
- Reduced trolley power → Battery/diesel supplements more
- Still preserves energy, just less preservation
- Example: 3 MW trolley (4 trucks) + 1 MW diesel vs 4 MW diesel-only = 25% fuel savings
- **Downgrade handling:** On descents, regen energy flows to battery, trolley serves auxiliary loads (HVAC, controls), no physics errors even with negative motor power

**For IncreaseSpeed modes:**
- Reduced total available power → Lower top speed
- Still beneficial compared to no trolley
- Example: 3 MW trolley + 4 MW battery = 7 MW total vs 4 MW battery-only

### Validation and Sensitivity Analysis

**Test different section capacities for 1 km (with 5 MW truck limit):**

| Section Capacity    | Optimal Truck Count | Degradation Point  | Performance     | Real-World Example    |
| ------------------- | ------------------- | ------------------ | --------------- | --------------------- |
| 8 MW (conservative) | 1 truck @ 5 MW      | 2+ trucks → 4 MW   | Earlier sharing | Standard systems      |
| 10 MW (recommended) | 1-2 trucks @ 5 MW   | 3+ trucks → 3.3 MW | Balanced        | Aitik mine (verified) |
| 12 MW (premium)     | 1-2 trucks @ 5 MW   | 3+ trucks → 4 MW   | Minimal sharing | ABB highest-end       |

**Recommendation:** Use **10 MW** as baseline for 1 km section - matches verified Aitik mine installation (10 MW DC capacity, CAT 795F AC fleet) and represents realistic industry standard. 12 MW represents ABB's highest-end systems and can be used for premium installations.

---

## Real-World Verification

### Specifications Aligned with Industry Data

Our trolley assist specifications have been verified against real-world mining operations:

**Primary Reference: Aitik Mine (Boliden, Sweden)**
- Fleet: Caterpillar 795F AC (14 trucks, entire fleet)
- Substation Capacity: **10 MW DC** ✓ (matches our 10 MW recommendation)
- Power per Truck: **4.5+ MW** ✓ (aligns with our 5 MW limit)
- Trolley Length: 3.7 km total (700m initial + 3km expansion)
- Trucks per Section: 2-4 trucks estimated
- Status: Operational since 2018

**Supporting Data:**
- **ABB Systems:** Up to 12 MW DC (highest available) - our premium option
- **Conventional Systems:** 8 MW DC typical
- **General Power Draw:** 3-5 MW per truck typical across industry
- **Los Pelambres Pilot (Chile):** 2 km section, 6 trucks, 2-3 substations

**CAT 794/795 Class Specifications:**
- Gross Vehicle Weight: ~360-400 tons
- Payload: ~290-400 tons
- Motor Power: ~2,610-3,000 kW (diesel generator)
- Trolley Power Draw: 4.5-5 MW (verified for CAT 795F AC)
- Speed Improvement: Up to 100% on grade (14→28 km/h)
- Fuel Reduction: 90%+ while on trolley (450 L/hr → 40 L/hr idle)

**Validation Summary:**
- ✅ Section power (10 MW) matches Aitik mine verified data
- ✅ Truck power (5 MW) aligns with CAT 795F AC verified 4.5+ MW
- ✅ Power sharing model reflects realistic operations (1-2 trucks typical, 3-4 peak)
- ✅ Voltage (1200V DC) verified at historical installations
- ✅ Efficiency (93%) within industry standard range (90-95%)

**Sources:**
- Aitik mine operational data (Boliden, 2018-present)
- ABB trolley assist technical specifications
- Caterpillar 795F AC trolley system documentation
- Los Pelambres pilot program specifications (2025)
- Industry publications and mining press releases (2018-2024)

---

## Implementation Strategy

### Phase 1: Add Mode Infrastructure
1. Add `prop_TruckMode` property with list `list_TruckModes = {"BatterySwap", "DieselElectric", "BatteryElectric"}`
2. Add `prop_ElectricAssistMode` property with list `list_ElectricAssistModes = {"PreserveEnergy", "IncreaseSpeed"}`
3. Add new state variables (9 total)
4. Add new token variables (~15 total)
5. Test with `prop_TruckMode = "BatterySwap"` - should behave identically to current implementation

### Phase 2: Implement DieselElectric Mode
1. Add `prop_DieselGeneratorMaxPowerKw` property
2. Modify `proc_SpeedBatteryUpdates` - add DieselElectric branch
3. Implement PreserveEnergy logic:
   - Trolley serves total demand (motor + auxiliary)
   - Handles downgrades: trolley serves auxiliary even during regen
   - Energy tracking for diesel preserved
4. Implement IncreaseSpeed logic (power-limited scaling factor)
5. Test with electrified and non-electrified paths
6. Validate downgrade scenarios (descents, negative motor power)

### Phase 3: Implement BatteryElectric Mode
1. Add `prop_BatteryMaxChargePowerKw` property
2. Modify `proc_SpeedBatteryUpdates` - add BatteryElectric branch
3. Implement PreserveEnergy logic:
   - Trolley serves total demand (motor + auxiliary)
   - Surplus power charges battery
   - Handles downgrades: regen + trolley auxiliary, both can charge battery
4. Implement IncreaseSpeed logic (power-limited scaling + battery tracking)
5. Test charging scenarios (surplus, deficit, perfect match)
6. Validate downgrade scenarios (regen + charging, auxiliary handling)

### Phase 4: Validation and Optimization
1. Validate all 7 operating scenarios (1 BatterySwap + 4 DieselElectric/BatteryElectric combinations)
2. Verify backward compatibility (BatterySwap mode unchanged)
3. Optimize proc_SpeedBatteryUpdates for readability/performance
4. Document energy accounting for each mode
5. Create test cases and validation scenarios

---

## Physics Implementation: Power-Limited Scaling Factor

### ⚠️ Critical Integration: Power Sharing + Power-Limited Physics

**IMPORTANT:** The power-limited scaling factor approach **must use dynamically calculated trolley power**, not static property values, when modeling hybrid-sectioned systems with power sharing.

**Problem Statement:**
- Power sharing dynamically calculates `TrolleyPowerKw` based on active trucks on section
- This value varies from `1.7 MW` (6 trucks) to `5 MW` (1-2 trucks) in real-world scenarios
- Using static `TrolleyMaxPowerKw` property (5 MW) in force calculations would **overestimate available power** when multiple trucks are present
- Results in **non-physical behavior**: Trucks appear to have more power than the section can supply

**Correct Implementation Pattern:**

```python
# Step 1: ALWAYS calculate dynamic trolley power FIRST (from power sharing section)
if OnElectricPath:
    ActiveTrucksOnSection = CurrentPath.NumberTravelers
    SharedPowerPerTruckKw = TrolleySectionTotalPowerKw / ActiveTrucksOnSection
    AvailablePowerPerTruckKw = min(SharedPowerPerTruckKw, TrolleyMaxPowerPerTruckKw)
    TrolleyPowerKw = AvailablePowerPerTruckKw × TrolleyEfficiency  # ← Dynamic value
else:
    TrolleyPowerKw = 0

# Step 2: Use TrolleyPowerKw (NOT TrolleyMaxPowerKw) in force calculations
if ElectricAssistMode == "IncreaseSpeed":
    TotalAvailablePowerKw = BasePowerKw + TrolleyPowerKw  # ✅ CORRECT
    # NOT: TotalAvailablePowerKw = BasePowerKw + TrolleyMaxPowerKw  # ❌ WRONG
```

**Physics Validation Example (10 MW section, 5 MW truck limit):**

| Scenario       | Active Trucks | Shared Power                 | TrolleyPowerKw (93% eff) | Total Power (w/ 4MW base) | Force @ 30 km/h | Valid?                                 |
| -------------- | ------------- | ---------------------------- | ------------------------ | ------------------------- | --------------- | -------------------------------------- |
| 1 truck        | 1             | 10 MW → 5 MW (truck-limited) | 4.65 MW                  | 8.65 MW                   | 1,038 kN        | ✅ Section has capacity                 |
| 3 trucks       | 3             | 3.3 MW                       | 3.07 MW                  | 7.07 MW                   | 848 kN          | ✅ Section provides 3×3.07=9.2 MW total |
| 6 trucks       | 6             | 1.7 MW                       | 1.58 MW                  | 5.58 MW                   | 669 kN          | ✅ Section provides 6×1.58=9.5 MW total |
| **Wrong calc** | 6             | -                            | **5 MW (static!)**       | **9 MW**                  | **1,080 kN**    | ❌ Section would need 54 MW!            |

**Robustness Check:** The power-limited scaling factor is robust **IF AND ONLY IF** it uses the dynamically calculated `TrolleyPowerKw` that respects power sharing constraints. Using static property values breaks the physics model.

---

### Design Decision Summary

**Selected Approach:** Power-Limited Scaling Factor

**Alternatives Considered:**

| Approach                         | Pros                                                                                                        | Cons                                                                                                              | Decision       |
| -------------------------------- | ----------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- | -------------- |
| **New Rimpull/Retard Curves**    | Most accurate for specific truck+trolley combinations                                                       | Requires extensive data collection/validation; separate curves for each configuration; maintenance burden         | ❌ Rejected     |
| **Direct Curve Scaling**         | Simple implementation; minimal code changes                                                                 | Assumes linear power-force relationship; not physically accurate at all speeds; over-predicts force at low speeds | ❌ Rejected     |
| **Power-Limited Scaling Factor** | Physics-accurate (P=F×V); reuses validated curves; respects mechanical limits; one calculation per timestep | Slightly more complex than direct scaling                                                                         | ✅ **SELECTED** |

### Mathematical Foundation

**Power-Force-Velocity Relationship:**
```
Power (kW) = Force (kN) × Velocity (m/s)
Force (kN) = Power (kW) / Velocity (m/s)
```

**Implementation:**
```
# Curve provides mechanical limit (tire adhesion, drivetrain)
CurveLimitForceN = lookup_rimpull_curve(speed, grade, load)

# Power provides energy limit (generator/battery capacity + trolley)
PowerLimitForceN = (TotalAvailablePowerKw × 1000) / SpeedMs

# Actual force is minimum of both constraints
TractiveForceN = min(CurveLimitForceN, PowerLimitForceN)
```

**Why This Works:**
- At **low speeds**: Power limit >> Curve limit → Curve-limited (mechanical constraints dominate)
- At **high speeds**: Power limit ≈ Curve limit → Power-limited (energy constraints dominate)
- Seamless transition between regimes without special case logic

### Implementation in proc_SpeedBatteryUpdates

**Common Force Calculation Pattern (All IncreaseSpeed Modes):**

```python
# Step 1: Get curve-based baseline force
BaseRimpullForceN = lookup_rimpull_curve(CurrentSpeedKmh, CurrentGrade, LoadState)
BaseRetardForceN = lookup_retard_curve(CurrentSpeedKmh, CurrentGrade, LoadState)

# Step 2: Apply degradation (battery modes only)
if TruckMode in ["BatterySwap", "BatteryElectric"]:
    PowerDegradationFactor = calculate_degradation(BatteryHealth, prop_PowerDegradationActive)
    CurveLimitForceN = BaseRimpullForceN × PowerDegradationFactor
else:
    CurveLimitForceN = BaseRimpullForceN

# Step 3: Calculate total available power
if OnElectricPath AND ElectricAssistMode == "IncreaseSpeed":
    if TruckMode == "DieselElectric":
        TotalAvailablePowerKw = DieselGeneratorMaxPowerKw + TrolleyPowerKw  # Dynamic
    elif TruckMode == "BatteryElectric":
        MaxBatteryPowerKw = BatteryMaxPowerKw × PowerDegradationFactor
        TotalAvailablePowerKw = MaxBatteryPowerKw + TrolleyPowerKw  # Dynamic
else:
    # Off path or non-IncreaseSpeed mode
    if TruckMode == "DieselElectric":
        TotalAvailablePowerKw = DieselGeneratorMaxPowerKw
    elif TruckMode == "BatteryElectric":
        TotalAvailablePowerKw = BatteryMaxPowerKw × PowerDegradationFactor

# Step 4: Apply power limit
if CurrentSpeedKmh < TargetSpeedKmh:
    SpeedMs = CurrentSpeedKmh / 3.6
    
    if SpeedMs > 0:
        PowerLimitForceN = (TotalAvailablePowerKw × 1000) / SpeedMs
        TractiveForceN = min(CurveLimitForceN, PowerLimitForceN)
    else:
        TractiveForceN = CurveLimitForceN  # At standstill
else:
    # Braking - not power-limited
    if TruckMode in ["BatterySwap", "BatteryElectric"]:
        TractiveForceN = -BaseRetardForceN × PowerDegradationFactor
    else:
        TractiveForceN = -BaseRetardForceN
```

### Validation Test Cases

**Test 1: Low Speed, High Force (Mechanical Limit Dominant)**
- Speed: 5 km/h, Grade: 12%, Loaded
- Curve rimpull: 850 kN
- Base power: 4000 kW → Power limit: 2,878 kN
- With trolley: 8000 kW → Power limit: 5,755 kN
- **Result:** Curve-limited at 850 kN (both cases)
- **Conclusion:** Trolley doesn't help at very low speeds (already mechanically limited)

**Test 2: Medium Speed, Steep Grade (Transition Zone)**
- Speed: 20 km/h, Grade: 8%, Loaded
- Curve rimpull: 400 kN
- Base power: 4000 kW → Power limit: 719 kN
- With trolley: 8000 kW → Power limit: 1,439 kN
- **Result:** Curve-limited at 400 kN (both cases)
- **Benefit:** With more power, truck can **sustain** 20 km/h; without trolley it would slow down

**Test 3: High Speed, Moderate Grade (Power Limit Emerges)**
- Speed: 35 km/h, Grade: 3%, Loaded
- Curve rimpull: 200 kN
- Base power: 4000 kW → Power limit: 412 kN
- With trolley: 8000 kW → Power limit: 823 kN
- **Result:** Curve-limited at 200 kN
- **Benefit:** Higher power enables reaching 35 km/h vs slowing to 25 km/h without trolley

### Key Advantages Over Alternatives

1. **vs New Curves:**
   - No data collection required for each truck+trolley combination
   - Existing validated curves remain authoritative for mechanical limits
   - Future trolley power changes don't require new curve derivation

2. **vs Direct Scaling:**
   - Physically accurate at all speed ranges
   - Doesn't over-predict force at low speeds (curve scaling would give 1700 kN at 5 km/h with 2× power - impossible due to tire adhesion)
   - Natural handling of standstill conditions (divide-by-zero avoided)

3. **Implementation Simplicity:**
   - One additional calculation: `min(CurveLimit, PowerLimit)`
   - Reuses all existing curve lookup infrastructure
   - Same logic works for DieselElectric and BatteryElectric modes

## Key Simplification Opportunities

### 1. Shared Calculation Functions
Extract common calculations to reusable token variable assignments:
```
# Once at top of process
BaseRimpullForceN = lookup_curve(CurrentSpeed, CurrentGrade, LoadState)
BaseDrivingDemandKw = calculate_driving_demand(BaseTractiveForceN, SpeedMs, MotorEfficiency, AuxiliaryPowerKw)

# Calculate power limit (IncreaseSpeed modes)
if ElectricAssistMode == "IncreaseSpeed":
    PowerLimitForceN = calculate_power_limit(TotalAvailablePowerKw, SpeedMs)
else:
    PowerLimitForceN = Infinity  # No power limiting

# Then each mode uses these baseline values
```

### 2. Power Source Resolver Pattern
```
# Generic pattern for all modes:
[TrolleyPowerKw, OnboardPowerKw, ChargingPowerKw] = resolve_power_sources(
    TruckMode,
    ElectricAssistMode,
    OnElectricPath,
    TrolleyMaxPowerKw,
    BaseDrivingDemandKw,
    CurrentSOC,
    BatteryMaxChargePowerKw
)

# Then apply to physics/energy accounting
```

### 3. Conditional Blocks Instead of Full Duplication
```
# Calculate common physics ONCE
[calculate resistance, calculate base force, apply power limit]

# Mode-specific energy source selection
if TruckMode == "BatterySwap":
    [simple battery-only logic]
elif TruckMode == "DieselElectric":
    [diesel + trolley logic]
elif TruckMode == "BatteryElectric":
    [battery + trolley logic]

# Apply physics update ONCE (common to all modes)
[calculate net force, acceleration, speed update]

# Mode-specific energy accounting
[update energy sources based on mode]
```

### 4. Flag-Based Assist Detection
```
# Single boolean flag simplifies many conditionals
AssistActive = OnElectricPath AND (TruckMode != "BatterySwap")

# Then use throughout:
if AssistActive AND ElectricAssistMode == "PreserveBattery":
    [preserve logic]
```

---

## Summary of Calculation Workflows

### BatterySwap Mode
```
Input: Speed, Grade, Weight, BatterySOC, BatteryHealth
Physics: Standard force-based acceleration → Speed update
Energy: Battery only (discharge during driving, regen during braking)
SOC: Decreases based on energy consumed
Swap: Triggered when SOC < threshold
Electric Path: Ignored (passes through as regular path)
Output: NewSpeed, NewSOC, SwapFlag
```

### DieselElectric + PreserveDiesel
```
Input: Speed, Grade, Weight, OnElectricPath, TrolleyMaxPowerKw
Physics: Standard force-based acceleration → Speed update (unchanged)
Energy: 
  - Off path: Diesel provides all power
  - On path: Trolley provides driving power, diesel backs off
  - Track diesel energy preserved
Electric Path: Energy substitution (trolley replaces diesel)
Output: NewSpeed, DieselEnergy, DieselPreserved
```

### DieselElectric + IncreaseSpeed
```
Input: Speed, Grade, Weight, OnElectricPath, TrolleyMaxPowerKw, DieselMaxPowerKw
Physics: Enhanced force from combined power → Higher speed capability
Energy:
  - Off path: Diesel only (limited power)
  - On path: Diesel + trolley (combined power for max force)
Electric Path: Power addition (trolley adds to diesel capability)
Output: NewSpeed (higher), DieselEnergy, TrolleyEnergy
```

### BatteryElectric + PreserveBattery
```
Input: Speed, Grade, Weight, OnElectricPath, TrolleyMaxPowerKw, BatterySOC, BatteryMaxChargePowerKw
Physics: Standard force-based acceleration → Speed update (unchanged)
Energy:
  - Off path: Battery provides all power (discharge)
  - On path: 
    - Trolley >= Demand: Trolley drives + excess charges battery (SOC increases)
    - Trolley < Demand: Trolley drives + battery supplements (SOC decreases slowly)
    - Track battery preserved + charging energy
Electric Path: Energy substitution + charging (trolley replaces battery + charges)
Output: NewSpeed, NewSOC (may increase!), BatteryPreserved, ChargingEnergy
```

### BatteryElectric + IncreaseSpeed
```
Input: Speed, Grade, Weight, OnElectricPath, TrolleyMaxPowerKw, BatterySOC, BatteryHealth
Physics: Enhanced force from combined power → Higher speed capability
Energy:
  - Off path: Battery only (limited power, degradation factor applies)
  - On path: Battery + trolley (combined power for max force)
  - Split actual power consumption between sources
Electric Path: Power addition (trolley adds to battery capability)
Output: NewSpeed (higher), NewSOC (decreases from battery usage), BatteryEnergy, TrolleyEnergy
```

---

## Validation Scenarios

### Scenario 1: BatterySwap Backward Compatibility
- **Setup:** `prop_TruckMode = "BatterySwap"`, existing model configuration
- **Expected:** Identical behavior to current implementation, electric paths ignored
- **Verify:** Speed profiles, SOC curves, swap triggers match baseline

### Scenario 2: DieselElectric PreserveDiesel
- **Setup:** Diesel truck on 8% grade uphill path, trolley 4000 kW available
- **Expected:** Diesel generator off/reduced when on electric path, preserved energy tracked
- **Verify:** Speed unchanged (~20 km/h), diesel consumption near zero on path

### Scenario 3: DieselElectric IncreaseSpeed
- **Setup:** Same path, trolley + diesel combined
- **Expected:** Higher speed (~28 km/h) due to combined power
- **Verify:** Speed increase validated, both power sources tracked

### Scenario 4: BatteryElectric PreserveBattery - Surplus
- **Setup:** Battery truck, 2000 kW driving demand, 4000 kW trolley available
- **Expected:** Trolley powers driving (2000 kW) + charges battery (2000 kW or up to max charge rate)
- **Verify:** SOC increases while driving, preserved energy + charging energy tracked

### Scenario 5: BatteryElectric PreserveBattery - Deficit
- **Setup:** Battery truck, 2000 kW driving demand, 1000 kW trolley available
- **Expected:** Trolley provides 1000 kW, battery supplements 1000 kW
- **Verify:** SOC decreases (but slower than without trolley), preserved energy tracked

### Scenario 6: BatteryElectric IncreaseSpeed
- **Setup:** Battery truck with degraded battery (80% health), trolley adds power
- **Expected:** Higher speed than battery-only operation
- **Verify:** Speed increase, battery + trolley energy tracked separately

### Scenario 7: Mode Transitions
- **Setup:** Switch `prop_TruckMode` between modes during simulation (if supported)
- **Expected:** Clean transitions, no calculation errors
- **Verify:** State variables reset appropriately, no orphaned values

---

## Supporting Infrastructure: obj_DieselRefuelStation

### Overview

**Object Type:** Fixed Resource (extends Simio TransferNode)  
**Purpose:** Diesel refueling operations for DieselElectric trucks  
**Design Pattern:** Mirrors `obj_BatterySwapChargeStation` architecture for consistency

**Core Functions:**
- **Refuel service** - Fills truck diesel tank to target level (typically 100%)
- **Flow rate simulation** - Realistic refueling duration based on configurable flow rates
- **Connection delays** - Models hose connection/disconnection time
- **Performance tracking** - Cumulative fuel dispensed and truck count statistics
- **Optional inventory** - Station fuel storage capacity tracking (if needed)

### Properties

| Property                     | Type    | Default | Description                                                        |
| ---------------------------- | ------- | ------- | ------------------------------------------------------------------ |
| `prop_RefuelRateLPerSecond`  | Real    | 150     | Refueling flow rate (L/s) - typical high-flow systems: 100-200 L/s |
| `prop_RefuelDelaySeconds`    | Real    | 5       | Connection/disconnection delays (hose attach/detach)               |
| `prop_TargetFuelLevelPct`    | Real    | 100     | Target fuel level percentage for refueling (typically 100%)        |
| `prop_FuelTankCapacityL`     | Real    | 50000   | Station fuel storage capacity in liters (optional tracking)        |
| `prop_TrackStationInventory` | Boolean | False   | Enable/disable station fuel inventory depletion tracking           |

### State Variables

| Variable                    | Type    | Description                                                    |
| --------------------------- | ------- | -------------------------------------------------------------- |
| `var_TotalFuelDispensedL`   | Real    | Cumulative fuel dispensed to all trucks (liters)               |
| `var_TotalTrucksRefueled`   | Integer | Count of refuel operations completed                           |
| `var_CurrentFuelInventoryL` | Real    | Current fuel in station storage (liters) - if tracking enabled |
| `var_Debug`                 | Boolean | Debug flag for development/troubleshooting                     |

### Process: proc_RefuelTruck

**Trigger:** Truck enters refuel station (Transfer or Seize)  
**Token:** `tkn_proc_RefuelTruck`

**Purpose:** Simulates complete diesel refueling operation including connection delays, fuel transfer duration based on flow rate, and station statistics updates.

**Process Flow:**

```pseudocode
# Step 1: Connection delay (hose attachment)
Delay(prop_RefuelDelaySeconds)

# Step 2: Calculate fuel needed
TruckTankCapacityL = ParentObject.obj_BatteryElectricTruck.prop_DieselTankCapacityL
CurrentFuelLevelL = ParentObject.obj_BatteryElectricTruck.var_DieselLevelL
TargetFuelLevelL = TruckTankCapacityL × (prop_TargetFuelLevelPct / 100)
FuelNeededL = TargetFuelLevelL - CurrentFuelLevelL

# Step 3: Calculate refuel duration based on flow rate
RefuelDurationSeconds = FuelNeededL / prop_RefuelRateLPerSecond
Delay(RefuelDurationSeconds)

# Step 4: Update truck fuel level
ParentObject.obj_BatteryElectricTruck.var_DieselLevelL = TargetFuelLevelL
ParentObject.obj_BatteryElectricTruck.var_DieselLevelPct = prop_TargetFuelLevelPct

# Step 5: Update station statistics
var_TotalFuelDispensedL += FuelNeededL
var_TotalTrucksRefueled += 1

# Step 6: Update station inventory (if tracking enabled)
if prop_TrackStationInventory == True:
    var_CurrentFuelInventoryL -= FuelNeededL
    # Optional: Check for low inventory warning/alarm

# Step 7: Disconnection delay (hose detachment)
Delay(prop_RefuelDelaySeconds)

# Step 8: Reset service flag and release truck
ParentObject.obj_BatteryElectricTruck.var_SwapBattery_Refuel_ChargeBattery_Flag = False
# Truck released to resume normal operations
```

### Performance Specifications

**Typical Refuel Operation (CAT 795F AC example):**

| Parameter             | Value          | Calculation                        |
| --------------------- | -------------- | ---------------------------------- |
| Tank capacity         | 3,000 L        | Truck specification                |
| Fuel needed           | ~2,700 L       | 90% tank refill (from 10% to 100%) |
| Refuel flow rate      | 150 L/s        | High-flow diesel system            |
| Connection delay      | 5 s            | Hose attachment time               |
| Transfer duration     | 18 s           | 2,700 L ÷ 150 L/s                  |
| Disconnection delay   | 5 s            | Hose detachment time               |
| **Total refuel time** | **28 seconds** | 5 + 18 + 5                         |

**For full tank refill (3,000 L):** ~25 seconds transfer + 10 seconds connection = **35 seconds total**

**Real-World Comparison:**
- Industry typical: 15-20 minutes for large trucks (manual operations, safety checks)
- High-flow automated systems: 1-5 minutes
- Simulation uses high-flow rates for optimal throughput modeling

### Station Capacity Planning

**Station Configuration Examples:**

| Scenario         | Refuel Stations | Flow Rate (L/s) | Trucks Served/Hour | Notes                            |
| ---------------- | --------------- | --------------- | ------------------ | -------------------------------- |
| Small operation  | 1 station       | 150             | ~100 trucks        | Single point of failure          |
| Medium operation | 2 stations      | 150 each        | ~200 trucks        | Redundancy, peak handling        |
| Large operation  | 3-4 stations    | 200 each        | ~400 trucks        | High throughput, multiple fleets |

**Utilization Formula:**
```
Trucks per Hour = (3600 seconds/hour) / (AvgRefuelTime seconds/truck) × NumberOfStations
AvgRefuelTime = ConnectionDelay + (AvgFuelNeeded / FlowRate) + DisconnectionDelay
```

### Integration with Truck Navigation

**Truck Decision Logic (in main model processes):**

```pseudocode
# When var_SwapBattery_Refuel_ChargeBattery_Flag is set to True:

if prop_TruckMode == "DieselElectric":
    # Navigate to assigned refuel station
    DestinationNode = var_AssignRefuelStationNode
    
    # Routing logic
    if CurrentNode != DestinationNode:
        Navigate to DestinationNode
        Transfer to obj_DieselRefuelStation
        # proc_RefuelTruck executes
    
    # After refuel completion, flag is reset by station
    # Resume normal hauling operations
```

### Comparison with obj_BatterySwapChargeStation

**Architectural Similarities:**
- ✅ Both extend TransferNode for truck service operations
- ✅ Both use connection/service delays for realism
- ✅ Both track cumulative statistics (energy/fuel dispensed, trucks served)
- ✅ Both reset unified service flag after completion
- ✅ Both support optional inventory tracking

**Key Differences:**

| Feature               | obj_BatterySwapChargeStation              | obj_DieselRefuelStation         |
| --------------------- | ----------------------------------------- | ------------------------------- |
| Service type          | Battery swap (10-step sequence)           | Diesel refuel (simple transfer) |
| Service duration      | ~5-10 minutes (swap sequence)             | ~30 seconds (high-flow refuel)  |
| Concurrent operations | Battery charging (multiple ports)         | Fuel transfer (single truck)    |
| Inventory complexity  | Multiple battery entities with SOC/health | Bulk fuel volume (simpler)      |
| Background processes  | Battery charging updates (1s timestep)    | None (passive storage)          |
| Capacity metric       | Available charged batteries               | Fuel volume in tank             |

---

**End of Document**
