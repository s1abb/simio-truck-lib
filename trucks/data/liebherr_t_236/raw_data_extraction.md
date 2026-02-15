# Liebherr T 236 - Raw Data Extraction

**Source**: Liebherr T236 Tech Specs - Performance Curves Page

---

## Chart Identification

### Source Document Layout

The source document shows **two charts side-by-side** on one page titled "Performance curves". Each chart has a parameter table below that identifies which data it shows.

### LEFT CHART - Rimpull/Propulsion (Red Curves)

**Identified by table below chart:**
- Gross power: 895 kW / 1,200 HP
- Net power: 835 kW / 1,120 HP
- Tire size: 27.00 R49
- Gear ratio: 40:1

**Visual identification:**
- **RED solid curve**: Rimpull force (kN/Lbf)
- **RED dashed curve**: Wheel power (kW/HP)

### RIGHT CHART - Retarding (Blue Curves)

**Identified by table below chart:**
- Retard power (continuous): 1,045 kW / 1,400 HP
- Tire size: 27.00 R49
- Gear ratio: 40:1

**Visual identification:**
- **BLUE solid curve**: Retarding force (kN/Lbf)
- **BLUE dashed curve**: Wheel power (kW/HP)

---

## Chart Reading Instructions

### Common Chart Elements

**Axes:**
- **X-axis (bottom)**: Speed in km/h (0-60)
- **Y-axis (left)**: Force in kN (0-1000)
- **Y-axis (right)**: Percent effective grade (2%, 6%, 10%, 14%)
- **Top X-axis**: Gross Vehicle Weight (GVW) in kg × 1000

**Weight Markers (Vertical Orange Lines):**
- **EVW** (Empty Vehicle Weight): ~80,000 kg
- **GVW** (Gross Vehicle Weight): ~180,000 kg

**Grade Lines (Diagonal Black Lines):**
- Multiple lines showing effective grades: 2%, 6%, 10%, 14%

### Reading Process

1. Choose a vehicle weight (between EVW and GVW)
2. Find where a grade line intersects your weight position
3. Read horizontally to the force curve
4. Read down to get speed (km/h) and left to get force (kN)

---

## Specifications

### Weights
- **Empty Vehicle Weight (EVW)**: 80,000 kg
- **Gross Vehicle Weight (GVW)**: 180,000 kg
- **Payload Capacity**: 100 tonnes

### Engine & Drivetrain
- **Engine Model**: Cummins QST30-C Quantum
- **Gross Power**: 895 kW / 1,200 HP
- **Net Power**: 835 kW / 1,120 HP
- **Drive Type**: Liebherr Litronic Plus Generation 2 AC drive system
- **Tire Size**: 27.00 R49
- **Gear Ratio**: 40:1
- **Retarding Power**: 1,045 kW / 1,400 HP continuous

### Speed on Grade
- **Diesel mode at 10% grade**: 15 km/h / 9.3 mph
- **Trolley mode at 10% grade**: 21 km/h / 13 mph
- **Maximum speed**: ~60 km/h

---

## Extracted Data

### RIMPULL DATA - From Red Curve Chart

#### LOADED TRUCK (GVW ~ 180,000 kg)

| Effective Grade (%) | Speed (km/h) | Rimpull (kN) | Notes                  |
| ------------------- | ------------ | ------------ | ---------------------- |
| 2%                  | 60           | 40           | Low grade, high speed  |
| 6%                  | 30           | 80           | Medium grade           |
| 10%                 | 13           | 160          | Matches spec: 15 km/h  |
| 14%                 | 12           | 200          | Steep grade, low speed |
| 15%                 | 10           | 240          | Steep grade, low speed |

#### EMPTY TRUCK (EVW ~ 80,000 kg)

| Effective Grade (%) | Speed (km/h) | Rimpull (kN) | Notes                    |
| ------------------- | ------------ | ------------ | ------------------------ |
| 2%                  | 60           | 40           | Near maximum speed       |
| 6%                  | 45           | 40           | Medium grade             |
| 10%                 | 30           | 80           | Higher speed than loaded |
| 14%                 | 25           | 100          | Steep grade              |
| 15%                 | 22           | 110          | Steep grade              |

---

### RETARDING DATA - From Blue Curve Chart

#### LOADED TRUCK (GVW ~ 180,000 kg)

| Effective Grade (%) | Speed (km/h) | Retarding Force (kN) | Notes              |
| ------------------- | ------------ | -------------------- | ------------------ |
| 2%                  | 60           | 60                   | Gentle descent     |
| 6%                  | 37           | 100                  | Medium descent     |
| 10%                 | 24           | 150                  | Steep descent      |
| 14%                 | 15           | 220                  | Very steep descent |
| 15%                 | 10           | 240                  | Very steep descent |

#### EMPTY TRUCK (EVW ~ 80,000 kg)

| Effective Grade (%) | Speed (km/h) | Retarding Force (kN) | Notes              |
| ------------------- | ------------ | -------------------- | ------------------ |
| 2%                  | 60           | 60                   | Gentle descent     |
| 6%                  | 60           | 60                   | Medium descent     |
| 10%                 | 45           | 70                   | Steep descent      |
| 14%                 | 30           | 120                  | Very steep descent |
| 15%                 | 28           | 135                  | Very steep descent |

---

## Notes

### Chart Legend Issue

Both charts have legends that say "Rimpull (kN/Lbf)" even though one shows retarding force. The correct identification comes from:
1. Parameter tables below each chart (Propulsion vs Retard)
2. Curve colors (red = propulsion, blue = retarding)
3. Power specifications (895 kW propulsion, 1,045 kW retarding)

### Data Extraction

- **For rimpull data**: Use left chart (red curves)
- **For retarding data**: Use right chart (blue curves)

---

## Summary

### Key Specifications
- **Payload**: 100 tonnes
- **Empty Weight**: 80,000 kg
- **Gross Weight**: 180,000 kg
- **Engine**: Cummins QST30-C, 895 kW / 1,200 HP gross
- **Retarding**: 1,045 kW / 1,400 HP continuous
- **Drive**: Liebherr Litronic Plus Gen 2 AC
- **Tires**: 27.00 R49
- **Gear Ratio**: 40:1


---

**Data extraction complete** - Ready for curve fitting and configuration file creation.