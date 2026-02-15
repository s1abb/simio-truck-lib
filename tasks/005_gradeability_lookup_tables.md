# Task 005: Generate Gradeability Lookup Tables

## Status: ✅ COMPLETE

## Objective
Convert exponential decay fitted gradeability data to simple grade-speed lookup tables for simulation use. The lookup tables will cover the full operating range from steep descents (-15%) to steep climbs (+20%) at 1% grade increments.

---

## Background

### Current State
- **Fitted gradeability curves** exist for all 4 trucks (exponential decay model)
- **Retarding curves** exist for all 4 trucks (power-limited)
- **Positive grades only**: Current data covers 2-30% climbing grades
- **No descent handling**: Negative grades not calculated

### Gap
Simulations need speed limits for **all grades** including:
- **Descents** (-15% to 0%): Limited by retarding/braking capacity
- **Flat** (0%): Maximum truck speed
- **Climbs** (0% to +20%): Limited by rimpull/gradeability

---

## Technical Approach

### Grade Ranges
| Range       | Description | Speed Determination                        |
| ----------- | ----------- | ------------------------------------------ |
| -15% to -1% | Descent     | Physics-based: Retarding force equilibrium |
| 0%          | Flat        | Maximum truck speed                        |
| +1% to +20% | Climb       | Interpolate from fitted gradeability data  |

### Key Equations

#### Descent Speed Calculation
Find equilibrium speed where retarding force = net downhill force:

```
GradeResistance (kN) = Mass (kg) × 9.81 × |Grade%| / 100 / 1000
RollingResistance (kN) = Mass (kg) × 9.81 × RR_Coef / 1000
NetDownhillForce (kN) = GradeResistance - RollingResistance

IF RetardingForce(MaxSpeed) >= NetDownhillForce:
    Speed = MaxSpeed  // Can maintain max speed
ELSE:
    Speed = SolveForEquilibrium(NetDownhillForce, RetardingCurve)
```

#### Climb Speed Calculation
Interpolate from fitted exponential decay curves:

```
Speed = FittedGradeabilityData.interpolate(Grade, Condition)
Speed = MIN(Speed, MaxSpeed)
```

---

## Implementation Plan

### Phase 1: Core Functions

#### 1.1 Add to `curve_fitting.py`
```python
def calculate_descent_speed(
    grade_pct: float,           # Negative value
    truck_mass_kg: float,
    max_speed_kmh: float,
    retarding_curve: dict,
    rolling_resistance: float = 0.02
) -> float:
    """Calculate max safe descent speed based on retarding capacity."""
    pass

def solve_equilibrium_speed(
    target_force_kn: float,
    retarding_curve: dict,
    max_speed_kmh: float,
    tolerance: float = 0.5
) -> float:
    """Binary search to find speed where retarding = target force."""
    pass

def interpolate_climb_speed(
    grade_pct: float,
    gradeability_curves: dict,
    condition: str,             # "empty" or "loaded"
    max_speed_kmh: float
) -> float:
    """Interpolate speed from fitted gradeability data."""
    pass

def generate_grade_speed_lookup(
    specifications: dict,
    gradeability_curves: dict,
    retarding_curve: dict,
    condition: str,
    min_grade: float = -15,
    max_grade: float = 20,
    grade_step: float = 1.0
) -> dict:
    """Generate complete grade-speed lookup table."""
    pass
```

### Phase 2: Integration

#### 2.1 Update `process_equipment.py`
Add Step 2.6 after gradeability curve fitting:
```python
# Step 2.6: Generate grade-speed lookup tables
print("Step 2.6: Generating grade-speed lookup tables...")
for condition in ['empty', 'loaded']:
    lookup = generate_grade_speed_lookup(
        specifications=specs,
        gradeability_curves=gradeability_curves,
        retarding_curve=retarding_data,
        condition=condition
    )
    # Store in performance_curves
```

#### 2.2 Update `export_utils.py`
Add CSV export for lookup tables:
```python
def export_grade_speed_lookup(model, lookup_tables, output_dir):
    """Export grade-speed lookup tables to CSV."""
    # {model}_grade_speed_loaded.csv
    # {model}_grade_speed_empty.csv
```

### Phase 3: Outputs

#### 3.1 JSON Structure
```json
{
  "grade_speed_lookup": {
    "description": "Maximum sustainable speed at each grade",
    "grade_range": {"min": -15, "max": 20, "step": 1},
    "rolling_resistance": 0.02,
    "loaded": {
      "data": [
        {"grade_pct": -15, "speed_kmh": 18.0, "limiting_factor": "retarding"},
        {"grade_pct": -14, "speed_kmh": 20.5, "limiting_factor": "retarding"},
        ...
        {"grade_pct": 0, "speed_kmh": 60.0, "limiting_factor": "max_speed"},
        {"grade_pct": 1, "speed_kmh": 58.5, "limiting_factor": "gradeability"},
        ...
      ]
    },
    "empty": { ... }
  }
}
```

#### 3.2 CSV Format
```csv
Grade (%),Speed (km/h),Limiting Factor
-15,18.0,retarding
-14,20.5,retarding
...
0,60.0,max_speed
1,58.5,gradeability
...
```

---

## Example Calculation

### CAT 794 AC Loaded on -8% Grade

**Given:**
- Truck mass: 521,631 kg
- Grade: -8%
- Max speed: 60 km/h
- Rolling resistance: 0.02

**Step 1: Calculate forces**
```
GradeResistance = 521,631 × 9.81 × 0.08 / 1000 = 409.6 kN
RollingResistance = 521,631 × 9.81 × 0.02 / 1000 = 102.4 kN
NetDownhillForce = 409.6 - 102.4 = 307.2 kN
```

**Step 2: Check max speed**
```
RetardingAt60kmh = 208.4 kN (from retarding curve)
208.4 kN < 307.2 kN → Cannot maintain max speed!
```

**Step 3: Binary search for equilibrium**
```
Try 30 km/h: Retarding = 416.8 kN > 307.2 kN → Can go faster
Try 45 km/h: Retarding = 277.8 kN < 307.2 kN → Too fast
Try 37.5 km/h: Retarding = 334.0 kN > 307.2 kN → Can go faster
Try 40 km/h: Retarding = 312.6 kN ≈ 307.2 kN → Equilibrium!
```

**Result:** -8% grade → 40 km/h (retarding-limited)

---

## Expected Output Example

| Grade (%) | Loaded (km/h) | Empty (km/h) | Notes                            |
| --------- | ------------- | ------------ | -------------------------------- |
| -15       | 18            | 35           | Steep descent, retarding-limited |
| -10       | 28            | 48           | Moderate descent                 |
| -5        | 52            | 60           | Gentle descent                   |
| 0         | 60            | 64           | Flat, max speed                  |
| 5         | 33            | 55           | Gentle climb                     |
| 10        | 16            | 34           | Moderate climb                   |
| 15        | 8             | 24           | Steep climb                      |
| 20        | 3             | 15           | Very steep climb                 |

---

## Validation

### Physical Checks
- [ ] Descent speeds limited by retarding capacity
- [ ] Heavier trucks have lower descent speeds (more downhill force)
- [ ] Empty trucks faster than loaded at same grade (both directions)
- [ ] No speeds exceed max truck speed
- [ ] Speed decreases monotonically with increasing grade

### Cross-Model Comparison
- [ ] Similar payload trucks have similar speed profiles
- [ ] Liebherr trucks may have different retarding characteristics
- [ ] All results physically plausible

---

## Files to Modify

| File                             | Changes                            |
| -------------------------------- | ---------------------------------- |
| `utilities/curve_fitting.py`     | Add descent speed functions        |
| `utilities/process_equipment.py` | Add Step 2.6 for lookup generation |
| `utilities/export_utils.py`      | Add CSV export for lookup tables   |
| `utilities/visualization.py`     | Add grade-speed chart (optional)   |

## Files to Create

| File                                             | Description         |
| ------------------------------------------------ | ------------------- |
| `outputs/{model}/{model}_grade_speed_loaded.csv` | Loaded lookup table |
| `outputs/{model}/{model}_grade_speed_empty.csv`  | Empty lookup table  |

---

## Success Criteria

- [x] Lookup tables generated for all 4 trucks
- [x] Both loaded and empty conditions
- [x] Grade range: -15% to +20% at 1% steps
- [x] Descent speeds physics-based (retarding equilibrium)
- [x] Climb speeds from fitted gradeability data
- [x] CSV exports created
- [x] All speeds physically valid

---

## Results Summary

### Loaded Truck Speed (km/h) at Key Grades

| Grade (%) | CAT 794 AC | CAT 793F AC | Liebherr T236 | Liebherr T264 |
| --------- | ---------- | ----------- | ------------- | ------------- |
| -15       | 18.5       | 22.0        | 14.0          | 20.0          |
| -10       | 30.5       | 35.5        | 22.5          | 33.0          |
| -5        | 60.0       | 64.0        | 60.0          | 55.0          |
| 0         | 60.0       | 64.0        | 60.0          | 55.0          |
| 5         | 40.0       | 38.5        | 34.0          | 33.5          |
| 10        | 17.5       | 15.5        | 15.5          | 16.5          |
| 15        | 7.5        | 6.0         | 10.0          | 10.0          |
| 20        | 3.5        | 2.5         | 10.0          | 9.5           |

### Empty Truck Speed (km/h) at Key Grades

| Grade (%) | CAT 794 AC | CAT 793F AC | Liebherr T236 | Liebherr T264 |
| --------- | ---------- | ----------- | ------------- | ------------- |
| -15       | 44.0       | 50.0        | 31.0          | 47.5          |
| -10       | 64.0       | 64.0        | 51.0          | 55.0          |
| -5        | 64.0       | 64.0        | 60.0          | 55.0          |
| 0         | 64.0       | 64.0        | 60.0          | 55.0          |
| 5         | 64.0       | 52.5        | 47.0          | 50.0          |
| 10        | 38.5       | 36.0        | 32.0          | 35.5          |
| 15        | 24.5       | 26.0        | 22.5          | 25.5          |
| 20        | 18.0       | 19.5        | 22.5          | 23.5          |

---

## Dependencies

- Task 003: Liebherr T 236 & T 264 data ✅ Complete
- Task 004: Gradeability curve fitting ✅ Complete
- Retarding curves for all 4 trucks ✅ Available

---

## References

- `/workspace/trucks/utilities/curve_fitting.py` - Existing curve fitting functions
- `/workspace/trucks/utilities/process_equipment.py` - Processing pipeline
- `/workspace/trucks/data/{model}/performance_curves.json` - Source data
- `/workspace/trucks/docs/curve_fitting_methodology.md` - Methodology docs

---

*Created: 2025-11-28*
*Status: PLANNED - Ready for implementation*
