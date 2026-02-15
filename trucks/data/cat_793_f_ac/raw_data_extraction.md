# CAT 793 F AC - Raw Data Extraction Template

**Source**: CAT 793 F AC Tech Specs

---

## Chart Reading Instructions

### Chart 1: Gradeability/Speed/Rimpull (Top Chart on Page 6)

**Chart Description:**
- **Top X-axis**: GROSS WEIGHT (lb x 1000, kg x 1000)
- **Bottom X-axis**: Speed in km/h / mph
- **Left Y-axis**: RIMPULL in kN / tf
- **Right Y-axis**: EFFECTIVE GRADE (Actual plus Rolling) in %
- **Diagonal lines**: Constant grade percentages (5%, 10%, 15%, 20%, 25%, 30%)
- **E and L curves**: Performance envelopes for Empty and Loaded trucks

**What to extract:**
The E and L curves represent the maximum performance envelope. To extract data:

1. Follow the **L-curve** (or E-curve for empty) from top to bottom
2. Find where it intersects each diagonal grade line (5%, 10%, 15%, 20%, 25%, 30%)
3. At each intersection point:
   - Read horizontally **LEFT** or **RIGHT** to intersect with the E/L curve
4. At the intersection point read the Y-axis for force and X-axis for speed

**IMPORTANT - Y-Axis Scale Check:**
- Check if the rimpull scale goes from 0-150 or 0-1500
- If it shows 0-150, this is a known mislabeling - actual scale is 0-1500 kN
- Note which scale you see: **0-150 (MISLABELED - multiply by 10 to get actual kN)**

---

## Data to Extract

### LOADED TRUCK (L) - 390,089 kg (GMW)
Follow the L-curve and read where it intersects each grade line:

| Effective Grade (%) | Speed (km/h) | Rimpull (kN) | Notes |
| ------------------- | ------------ | ------------ | ----- |
| 0-3%                | 60           | 0-130        |
| 5%                  | 30           | 195          |
| 10%                 | 16           | 370          |
| 15%                 | 12           | 560          |
| 20%                 | 5            | 760          |
| 25%                 | 3            | 920          |
| 30%                 | 13           | 420          |

### EMPTY TRUCK (E) - 169,802 kg
Follow the E-curve and read where it intersects each grade line:

| Effective Grade (%) | Speed (km/h) | Rimpull (kN) | Notes |
| ------------------- | ------------ | ------------ | ----- |
| 0-3%                | 60           | 50           |
| 5%                  | 55           | 90           |
| 10%                 | 36           | 160          |
| 15%                 | 24           | 230          |
| 20%                 | 20           | 300          |
| 25%                 | 16           | 360          |
| 30%                 | 13           | 420          |

---

### Chart 2: Retarding Performance - Continuous Grade (Bottom Chart on Page 6)

**Chart Description:**
- Bottom X-axis: Speed in km/h / mph
- Left Y-axis: RETARDING FORCE in kN (same 0-150 scale, multiply by 10)
- Right Y-axis: EFFECTIVE GRADE (Actual minus Rolling) in %
- Diagonal lines: Constant grade percentages
- E and L curves: Retarding performance envelopes

### LOADED TRUCK (L) - 390,089 kg (GMW)
Follow the L-curve and read where it intersects each grade line:

| Effective Grade (%) | Speed (km/h) | Retarding Force (kN) | Notes |
| ------------------- | ------------ | -------------------- | ----- |
| 4%                  | 60           | 1100                 |
| 5%                  | 44           | 1500                 |
| 10%                 | 20           | 3000                 |
| 15%                 | 13           | 4500                 |
| 20%                 | 13           | 4500                 |
| 25%                 | 9            | 6000                 |

### EMPTY TRUCK (E) - 169,802 kg
Follow the E-curve and read where it intersects each grade line:

| Effective Grade (%) | Speed (km/h) | Retarding Force (kN) | Notes |
| ------------------- | ------------ | -------------------- | ----- |
| 5%                  | 60           | 600                  |
| 10%                 | 44           | 1200                 |
| 15%                 | 33           | 2000                 |
| 20%                 | 23           | 2500                 |
| 25%                 | 18           | 3000                 |
| 30%                 | 17           | 3600                 |

---

