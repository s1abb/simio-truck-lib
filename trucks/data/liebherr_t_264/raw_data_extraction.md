# Liebherr T 264 - Raw Data Extraction

**Source**: Liebherr T264 Tech Specs - Performance Curves Page

---

## Chart Identification

### Source Document Layout

The source document shows a **single combined chart** displaying both rimpull (red curve) and retarding (blue curve) performance on one graph.

### Combined Chart - Rimpull and Retarding

**Visual identification:**
- **RED solid curve**: Rimpull force (kN)
- **BLUE solid curve**: Retarding force (kN)

---

## Chart Reading Instructions

### Chart Elements

**Axes:**
- **X-axis (bottom)**: Speed in km/h (0-80)
- **Y-axis (left)**: Force in kN (0-1200)
- **Y-axis (right)**: Percent effective grade (2%, 6%, 10%, 14%, 16%)
- **Top X-axis**: Gross Vehicle Weight (GVW) in kg × 1000

**Weight Markers (Vertical Orange Lines):**
- **EVW** (Empty Vehicle Weight): ~176,000 kg
- **GVW** (Gross Vehicle Weight): ~416,000 kg

**Grade Lines (Diagonal Black Lines):**
- Multiple lines showing effective grades: 2%, 6%, 10%, 14%, 16%

### Reading Process

1. Choose a vehicle weight (between EVW and GVW)
2. Find where a grade line intersects your weight position
3. Read horizontally to the force curve (red for rimpull, blue for retarding)
4. Read down to get speed (km/h) and left to get force (kN)

---

## Specifications

### Weights
- **Empty Vehicle Weight (EVW)**: 176,000 kg
- **Gross Vehicle Weight (GVW)**: 416,000 kg
- **Payload Capacity**: 240 tonnes

### Engine & Drivetrain
- **Engine Model**: Liebherr D9812
- **Gross Power**: 2,013 kW / 2,700 HP at 1,800 RPM
- **Drive Type**: Liebherr Litronic Plus AC drive system
- **Displacement**: 62 L (12-cylinder V-engine)
- **Tire Size**: 40.00 R57
- **Retarding Power**: ~3,500 kW continuous (from chart)

### Speed on Grade
- **Diesel mode at 10% grade**: 15.2 km/h
- **Trolley mode at 10% grade**: 24.2 km/h
- **Maximum speed**: ~70-80 km/h

---

## Extracted Data

### RIMPULL DATA - From Red Curve

#### LOADED TRUCK (GVW ~ 416,000 kg)

| Effective Grade (%) | Speed (km/h) | Rimpull (kN) | Notes |
| ------------------- | ------------ | ------------ | ----- |
| 2%                  | 55           | 100          |
| 4%                  | 40           | 160          |
| 6%                  | 30           | 200          |
| 8%                  | 20           | 300          |
| 10%                 | 15           | 400          |
| 12%                 | 13           | 440          |
| 14%                 | 11           | 520          |
| 16%                 | 10           | 620          |

#### EMPTY TRUCK (EVW ~ 176,000 kg)

| Effective Grade (%) | Speed (km/h) | Rimpull (kN) | Notes |
| ------------------- | ------------ | ------------ | ----- |
| 2%                  | 55           | 100          |
| 4%                  | 55           | 100          |
| 6%                  | 55           | 100          |
| 8%                  | 45           | 120          |
| 10%                 | 34           | 190          |
| 12%                 | 28           | 200          |
| 14%                 | 25           | 220          |
| 16%                 | 22           | 260          |

---

### RETARDING DATA - From Blue Curve

#### LOADED TRUCK (GVW ~ 416,000 kg)

| Effective Grade (%) | Speed (km/h) | Retarding Force (kN) | Notes |
| ------------------- | ------------ | -------------------- | ----- |
| 2%                  | 55           | 140                  |
| 4%                  | 55           | 140                  |
| 6%                  | 45           | 220                  |
| 8%                  | 40           | 300                  |
| 10%                 | 32           | 360                  |
| 12%                 | 25           | 480                  |
| 14%                 | 23           | 540                  |
| 16%                 | 20           | 630                  |

#### EMPTY TRUCK (EVW ~ 176,000 kg)

| Effective Grade (%) | Speed (km/h) | Retarding Force (kN) | Notes |
| ------------------- | ------------ | -------------------- | ----- |
| 2%                  | 55           | 140                  |
| 4%                  | 55           | 140                  |
| 6%                  | 55           | 140                  |
| 8%                  | 55           | 140                  |
| 10%                 | 50           | 200                  |
| 12%                 | 47           | 210                  |
| 14%                 | 40           | 260                  |
| 16%                 | 38           | 280                  |

---

## Notes

### Chart Layout

This truck's performance data is shown on a single combined chart with both rimpull (red) and retarding (blue) curves visible together.

### Data Extraction

- **For rimpull data**: Use red curve
- **For retarding data**: Use blue curve

---

## Summary

### Key Specifications
- **Payload**: 240 tonnes
- **Empty Weight**: 176,000 kg
- **Gross Weight**: 416,000 kg
- **Engine**: Liebherr D9812, 2,013 kW / 2,700 HP
- **Retarding**: ~3,500 kW continuous
- **Drive**: Liebherr Litronic Plus AC
- **Tires**: 40.00 R57

### Performance at 10% Grade
- **Loaded (diesel)**: 15.2 km/h (15 km/h from chart)
- **Loaded (trolley)**: 24.2 km/h

---

**Data extraction complete** - Ready for curve fitting and configuration file creation.