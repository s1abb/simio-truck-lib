# proc_SpeedUpdates - Force-Based Delay Physics

**Process Type:** Event-driven physics with incremental speed changes  
**Trigger:** Monitor fires when `Movement.Pitch` changes and `Movement.Rate > 0`  
**Token:** `tkn_SpeedCalculations`  
**Implementation Status:** ✅ DELAY-BASED APPROACH IMPLEMENTED

---

## Overview

The `proc_SpeedUpdates` process implements **force-based delay physics** similar to the example model. When the truck's grade changes, the process calculates target speed based on truck capabilities and road conditions, then incrementally adjusts speed (±1 km/h per iteration) with delays calculated from physics forces.

**Key Characteristics:**
- **Event-driven**: Fires on pitch change (not fixed timestep)
- **Conditional execution**: Only runs if `var_SpeedUpdates == True`
- **Incremental speed changes**: ±1 km/h per iteration
- **Physics-based delays**: Delay duration calculated from forces and acceleration
- **Loop structure**: Decide → Assign → Delay → Loop until target reached

**Current Trigger:**
```
Monitor: Movement.Pitch
Condition: Movement.Rate > 0
Process: proc_SpeedUpdates
```

---

## Current Implementation Status

### ✅ Fully Implemented & VALIDATED
- **Grade-change monitoring** - Event-driven trigger on pitch change ✅
- **Force calculations** - Grade resistance, rolling resistance, total resistance ✅
- **Exact trigonometry** - `Sin(Atan(grade/100))` for gravity force ✅ **VALIDATED**
- **Target speed logic** - Loaded vs empty, path speed limits ✅
- **Acceleration/deceleration detection** - Boolean flag for force direction ✅
- **Incremental speed changes** - ±1 km/h per iteration ✅
- **Loop structure** - Correctly compares `CurrentSpeed < TargetSpeed` ✅ **FIXED**
- **Net force calculation** - `TractiveForce - TotalResistance` ✅ **VALIDATED**
- **Acceleration calculation** - `NetForce / Mass` ✅ **VALIDATED**

### 🔴 Critical Bug (Confirmed from Trace - WORSE THAN INITIALLY THOUGHT)
1. **Delay calculation CATASTROPHICALLY WRONG** - Divides by 3600 twice instead of once
   - **Current formula:** `(0.2778 / AccelerationMs2) / 3600 / 3600` 
   - **Should be:** `(0.2778 / AccelerationMs2) / 3600`
   - **Impact:** Truck accelerates **3600x too fast** (instant acceleration!)
   - **Validation:** Trace shows delay = 0.0000553 seconds, should be 0.1991 seconds

### ⚠️ Still Missing from Full Model
- Iteration limit (prevent infinite loops)
- Curve-limited force (power-speed relationship)
- Power-limited force (motor power constraints)
- Motor thermal management
- Battery/fuel energy tracking
- Trolley power calculations
- Effective grade for table lookups

---

## Process Flow

### Structure Overview
```
Step 3: Decide (var_SpeedUpdates)
  ├─ True → Step 2
  └─ False → End

Step 2: Assign "TargetSpeed" (17 assignments)
  └─ → Step 6

Step 6: Assign "Speed+1/-1" (2 assignments)
  └─ → Step 7

Step 7: Decide "Current<Target"
  ├─ True → Step 4
  └─ False → End

Step 4: Assign "SpeedUpdates" (4 assignments)
  └─ → Step 5

Step 5: Delay (PhysicsDelaySeconds)
  └─ → Step 6 (loop back)
```

### Step-by-Step Details

---

### **Step 3: Decide "SpeedUpdates"**
**Purpose:** Only execute physics if speed updates are enabled.

**Type:** Conditional Decide

**Condition:** `var_SpeedUpdates`

**Paths:**
- **True** → Continue to Step 2 (calculate target speed)
- **False** → End process (skip all physics)

---

### **Step 2: Assign "TargetSpeed"** (17 assignments)
**Purpose:** Read current state, lookup truck properties, calculate target speed and resistance forces, determine acceleration/deceleration.

**Assignment Order:**

1. **Read Current State**
   ```
   CurrentGrade = Movement.Pitch
   CurrentSpeedKmh = Movement.Rate
   ```

2. **Lookup Truck Properties**
   ```
   RowIndex = tbl_TruckTypes.TruckType.RowForKey(String.FromList(list_TruckTypes, prop_TruckType))
   EmptyWeightKg = tbl_TruckTypes[RowIndex].EmptyOperatingWeightKg
   CurrentWeightKg = Math.If(var_Loaded, var_Payload, EmptyWeightKg)
   BaseRimpullForceN = tbl_TruckTypes[RowIndex].RimpullForceN
   BaseRetardForceN = tbl_TruckTypes[RowIndex].RetardForceN
   MaxSpeedKmh_Loaded = tbl_TruckTypes[RowIndex].MaxSpeedKmh_Loaded
   MaxSpeedKmh_Empty = tbl_TruckTypes[RowIndex].MaxSpeedKmh_Empty
   RollingResistance = tbl_TruckTypes[RowIndex].RollingResistance
   ```

3. **Calculate Target Speed**
   ```
   MaxSpeedKmh = Math.If(var_Loaded, MaxSpeedKmh_Loaded, MaxSpeedKmh_Empty)
   PathSpeedLimitKmh = Math.If(
       Location.Parent.Is.obj_ElectricPath,
       Location.Parent.obj_ElectricPath.SpeedLimit,
       DesiredSpeed
   )
   TargetSpeedKmh = Math.Min(PathSpeedLimitKmh, MaxSpeedKmh)
   ```

4. **Calculate Resistance Forces**
   ```
   GradeResistanceForceN = CurrentWeightKg × 9.81 × Math.Sin(Math.Atan(CurrentGrade / 100))
   RollingResistanceForceN = CurrentWeightKg × 9.81 × RollingResistance
   TotalResistanceN = GradeResistanceForceN + RollingResistanceForceN
   ```

5. **Determine Acceleration/Deceleration Direction**
   ```
   TrueAccelerate_FalseDecelerate = TargetSpeedKmh > CurrentSpeedKmh
   ```

**Exit:** → Step 6

---

### **Step 6: Assign "Speed+1/-1"** (2 assignments)
**Purpose:** Increment or decrement speed by 1 km/h based on direction flag.

**Assignments:**
```
CurrentSpeedKmh = Math.If(
    TrueAccelerate_FalseDecelerate,
    CurrentSpeedKmh + 1,
    CurrentSpeedKmh - 1
)

Movement.Rate = CurrentSpeedKmh (units: km/h)
```

**Exit:** → Step 7

---

### **Step 7: Decide "Current<Target"**
**Purpose:** Check if speed has reached target to exit loop.

**Type:** Conditional Decide

**Condition:** 
```
Math.If(
    TrueAccelerate_FalseDecelerate,
    CurrentSpeedKmh < TargetSpeedKmh,   ✅ Correct!
    CurrentSpeedKmh > TargetSpeedKmh    ✅ Correct!
)
```

**✅ VALIDATION:** Trace confirms correct condition is used. Loop works properly.

**Paths:**
- **True** → Step 4 (calculate forces and delay)
- **False** → End process

---

### **Step 4: Assign "SpeedUpdates"** (4 assignments)
**Purpose:** Calculate tractive force, net force, acceleration, and delay duration.

**Assignments:**

1. **Select Tractive Force (Accelerate or Decelerate)**
   ```
   TractiveForceN = Math.If(
       TrueAccelerate_FalseDecelerate,
       BaseRimpullForceN,
       -BaseRetardForceN
   )
   ```

2. **Calculate Net Force**
   ```
   NetTractiveForceN = TractiveForceN - TotalResistanceN
   ```

3. **Calculate Acceleration**
   ```
   AccelerationMs2 = NetTractiveForceN / CurrentWeightKg
   ```

4. **Calculate Delay Duration** 🔴 **CATASTROPHICALLY WRONG**
   ```
   PhysicsDelaySeconds = (0.2778 / AccelerationMs2) / 3600 / 3600
   ```
   
   **🔴 CRITICAL BUG:** Divides by 3600 TWICE - converts to hours then divides by 3600 again!
   
   **SHOULD BE:**
   ```
   PhysicsDelaySeconds = (0.2778 / AccelerationMs2) / 3600
   ```
   - `0.2778` converts 1 km/h to m/s
   - Division by acceleration gives time in seconds
   - **Single** division by 3600 converts to hours (Simio time units)

**Exit:** → Step 5

---

### **Step 5: Delay**
**Purpose:** Wait for the calculated physics delay before next speed increment.

**Delay Duration:** `tkn_SpeedCalculations.PhysicsDelaySeconds` (seconds)

**Exit:** → Step 6 (loop back to increment/decrement speed again)

---

## Critical Issues & Validation

### ✅ Issue 1: Loop Condition **FIXED & VALIDATED**
**Status:** Trace validation confirms loop condition is correct.

**Trace Shows:**
```
Math.If(tkn_SpeedCalculations.TrueAccelerate_FalseDecelerate,
    tkn_SpeedCalculations.CurrentSpeedKmh<tkn_SpeedCalculations.TargetSpeedKmh,
    tkn_SpeedCalculations.CurrentSpeedKmh>tkn_SpeedCalculations.TargetSpeedKmh)
```

**Validation:** Loop correctly compares `CurrentSpeedKmh` to `TargetSpeedKmh`. ✅

**Result:** Loop iterates properly, truck reaches target speed. ✅

---

### 🔴 Issue 2: Delay Calculation Incorrect (CATASTROPHIC - RE-VALIDATED)
**Problem:** Physics delay formula divides by 3600 TWICE, making delays nearly instantaneous.

**Current Code:**
```
PhysicsDelaySeconds = (0.2778 / AccelerationMs2) / 3600 / 3600
```

**Latest Trace Validation (Time: 0.1516798085996971 Hours):**
```
Acceleration: 1.3950369 m/s²
Trace delay:  1.536409e-08 hours = 0.0000553 seconds
Expected:     5.531514e-05 hours = 0.1991 seconds
Error factor: 3600x too SHORT (essentially instant!)
```

**Formula Breakdown:**
```
Step 1: Time for 1 km/h = 0.2778 / 1.3950 = 0.1991 seconds ✅
Step 2: Convert to hours = 0.1991 / 3600 = 5.531e-05 hours ✅
Step 3: EXTRA division = 5.531e-05 / 3600 = 1.536e-08 hours 🔴 BUG!
```

**Correct Formula:**
```
PhysicsDelaySeconds = (0.2778 / AccelerationMs2) / 3600
```
(Remove the second `/3600` division)

**Why This Is Correct:**
- `0.2778 m/s` = 1 km/h converted to m/s
- Time (seconds) = ΔVelocity / Acceleration = 0.2778 / AccelerationMs2
- Time (hours) = Time (seconds) / 3600 (convert once, not twice!)

**Impact:** 🔴 Truck accelerates **3600x faster** than physics predicts - essentially instantaneous!
```

**Dimensional Analysis:**
- `0.2778 m/s` = 1 km/h converted to m/s
- `(0.2778 m/s) / (AccelerationMs2 m/s²)` = time in seconds
- Division by 60 converts to minutes (Simio standard time units)

**Example:**
- If `AccelerationMs2 = 0.5 m/s²`
- Time to change 1 km/h = 0.2778 / 0.5 = 0.556 seconds = 0.00926 minutes
- This correctly represents time to accelerate by 1 km/h

**Impact:** Delays are completely wrong, truck speed changes don't match physics reality.

---

### ⚠️ Issue 3: No Iteration Limit
**Problem:** No maximum iteration counter to prevent infinite loops.

**Recommendation:** Add iteration limit like example model:
```
// In Step 2 (TargetSpeed), add:
MaxIterations = 100  // Or truck's max speed in km/h

// In Step 6 (Speed+1/-1), add:
MaxIterations = MaxIterations - 1

// In Step 7 (Current<Target), modify condition:
(iteration condition) AND MaxIterations > 0
```

**Impact:** If delay calculation fails or target is unreachable, process could loop forever.

---

### ⚠️ Issue 4: Speed Change Before Delay
**Problem:** Step 6 changes speed BEFORE delay, meaning first iteration happens instantly.

**Current Flow:**
```
Step 2: Calculate target → Step 6: Change speed → Step 7: Check → Step 4: Calculate delay → Step 5: Wait → Step 6: ...
```

**Impact:** First speed change happens with zero delay, subsequent changes have delays.

**Recommendation:** Reorder to delay BEFORE speed change:
```
Step 2: Calculate target → Step 4: Calculate delay → Step 5: Wait → Step 6: Change speed → Step 7: Check → ...
```

---

### ✅ Validation: Physics Calculations Verified from Trace

**Trace Sample:** Time 0.1516798085996971 Hours, Token 18

| Calculation | Trace Value | Calculated | Status |
|-------------|-------------|------------|--------|
| **Current Grade** | -0.095% | - | Input |
| **Current Weight** | 89,229.18 kg | - | Input |
| **Rolling Resistance** | 0.02 | - | Input |
| **Grade Resistance** | -829.38 N | -829.38 N | ✅ MATCH |
| **Rolling Resistance** | 17,506.77 N | 17,506.77 N | ✅ MATCH |
| **Total Resistance** | 16,677.39 N | 16,677.39 N | ✅ MATCH |
| **Tractive Force** | 130,449.49 N | 130,449.49 N | ✅ MATCH |
| **Net Tractive Force** | 113,772.10 N | 113,772.10 N | ✅ MATCH |
| **Acceleration** | 1.3950369 m/s² | 1.3950369 m/s² | ✅ MATCH |
| **Delay (current)** | 1.536e-08 hrs | (0.2778/accel)/3600/3600 | 🔴 WRONG |
| **Delay (correct)** | Should be 5.532e-05 hrs | (0.2778/accel)/3600 | 🔴 BUG |
| **Error Factor** | **3600x too fast!** | Divides by 3600 twice! | 🔴 CATASTROPHIC |

**Validation Summary:**
- ✅ All force calculations are mathematically correct
- ✅ Exact trigonometry properly implemented: `Sin(Atan(grade/100))`
- ✅ Net force and acceleration calculations verified
- 🔴 Delay formula has DOUBLE division error (3600x too fast!)

---

## Recommendations

### Priority 1: Fix Delay Calculation 🔴 **CATASTROPHIC BUG**
**Remove extra division by 3600 in Step 4 assignment 4:**

**Current (WRONG):**
```
PhysicsDelaySeconds = (0.2778 / AccelerationMs2) / 3600 / 3600
```

**Corrected:**
```
PhysicsDelaySeconds = (0.2778 / AccelerationMs2) / 3600
```

**Impact:** Will slow down acceleration by **3600x** to match real physics. Currently truck accelerates essentially instantly.

### Priority 2: Add Iteration Limit ⚠️
Add to Step 2 (last assignment):
```
MaxIterations = 100
```

Add to Step 6 (after speed change):
```
MaxIterations = MaxIterations - 1
```

Modify Step 7 condition:
```
Math.If(TrueAccelerate_FalseDecelerate,
    CurrentSpeedKmh < TargetSpeedKmh,
    CurrentSpeedKmh > TargetSpeedKmh) AND MaxIterations > 0
```

### Priority 3: Reorder Flow ⚠️
Change step connections to delay BEFORE speed change:
```
Step 2 (TargetSpeed) → Step 4 (SpeedUpdates) → Step 5 (Delay) → Step 6 (Speed+1/-1) → Step 7 (Decide) → Step 4 (loop)
```

---

## Comparison to Example Model (with Trace Validation)

| Aspect                 | Example Model         | Current obj_Truck          | Status                  |
| ---------------------- | --------------------- | -------------------------- | ----------------------- |
| **Trigger**            | Pitch change          | Pitch change               | ✅ Match                 |
| **Approach**           | Delay-based iteration | Delay-based iteration      | ✅ Match                 |
| **Speed increment**    | ±1 km/h               | ±1 km/h                    | ✅ Match                 |
| **Gravity force**      | `Sin(Atan(g/100))`    | `Sin(Atan(g/100))`         | ✅ Match (VALIDATED)     |
| **Rolling resistance** | `mass × 0.02 × 9.81`  | `mass × RR × 9.81`         | ✅ Match (VALIDATED)     |
| **Target speed**       | Complex logic         | Loaded/empty + path limits | ✅ Implemented           |
| **Delay formula**      | `(0.2778/accel)/60`   | `(0.2778/accel)/3600/3600` | 🔴 3600x too fast (VALIDATED) |
| **Loop condition**     | `speed < target`      | `speed < target`           | ✅ Fixed (VALIDATED)     |
| **Iteration limit**    | MaxIter = 60          | None                       | ⚠️ Missing               |
| **Flow order**         | Delay → Speed change  | Speed change → Delay       | ⚠️ Different             |

---

## Summary

**Approach:** ✅ Correctly implements delay-based physics similar to example model

**Force Calculations:** ✅ All physics equations validated from trace data

**Loop Condition:** ✅ Fixed - correctly compares CurrentSpeed vs TargetSpeed (validated)

**Critical Bug:** 🔴 **Delay formula catastrophically wrong** - Divides by 3600 twice instead of once
- **Current:** `(0.2778/accel)/3600/3600` 
- **Should be:** `(0.2778/accel)/3600`
- **Impact:** Truck accelerates **3600x too fast** (essentially instant)
- **Validated:** Trace shows 0.0000553 sec delay, should be 0.1991 sec (3600x error!)

**Recommended Actions:**
1. 🔴 Remove extra `/3600` from delay formula (CATASTROPHIC - 3600x acceleration error!)
2. ⚠️ Add iteration limit (prevent infinite loops)
3. ⚠️ Consider reordering to delay before speed change

**Trace Validation Results:**
- Grade resistance: ✅ EXACT match
- Rolling resistance: ✅ EXACT match  
- Net force: ✅ EXACT match
- Acceleration: ✅ EXACT match
- Delay calculation: 🔴 CATASTROPHICALLY WRONG (3600x too fast!)

---

**Document Version:** 2.2  
**Last Updated:** 2025-12-03  
**Status:** ✅ Latest trace re-validated - Delay bug worse than initially thought (3600x error!)