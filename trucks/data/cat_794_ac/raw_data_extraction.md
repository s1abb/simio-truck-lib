# CAT 794 AC - Raw Data Extraction Template

**Source**: CAT 794 AC Tech Specs (AEHQ7083-09)  
**Chart Location**: Page 5  

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

### LOADED TRUCK (L) - 521,631 kg
Follow the L-curve and read where it intersects each grade line:

| Effective Grade (%) | Speed (km/h) | Rimpull (kN) | Notes                            |
| ------------------- | ------------ | ------------ | -------------------------------- |
| 0-3%                | 60           | 0-130        | Max speed, minimal rimpull (×10) |
| 5%                  | 33           | 250          | Read 25 on chart × 10            |
| 10%                 | 16           | 520          | Read 52 on chart × 10            |
| 15%                 | 11           | 720          | Read 72 on chart × 10            |
| 20%                 | 8            | 1000         | Read 100 on chart × 10           |
| 25%                 | 6            | 1260         | Read 126 on chart × 10           |
| 30%                 | 0            | 1400         | Read 140 on chart × 10           |

### EMPTY TRUCK (E) - 217,419 kg
Follow the E-curve and read where it intersects each grade line:

| Effective Grade (%) | Speed (km/h) | Rimpull (kN) | Notes                 |
| ------------------- | ------------ | ------------ | --------------------- |
| 6%                  | 60           | 130          | Read 13 on chart × 10 |
| 10%                 | 37           | 220          | Read 22 on chart × 10 |
| 15%                 | 26           | 320          | Read 32 on chart × 10 |
| 20%                 | 18           | 420          | Read 42 on chart × 10 |
| 25%                 | 15           | 520          | Read 52 on chart × 10 |
| 30%                 | 13           | 620          | Read 62 on chart × 10 |


---

### Chart 2: Retarding Performance - Continuous Grade (Bottom Chart on Page 6)

**Chart Description:**
- Bottom X-axis: Speed in km/h / mph
- Left Y-axis: RETARDING FORCE in kN (same 0-150 scale, multiply by 10)
- Right Y-axis: EFFECTIVE GRADE (Actual minus Rolling) in %
- Diagonal lines: Constant grade percentages
- E and L curves: Retarding performance envelopes

### LOADED TRUCK (L) - 521,631 kg
Follow the L-curve and read where it intersects each grade line:

| Effective Grade (%) | Speed (km/h) | Retarding Force (kN) | Notes         |
| ------------------- | ------------ | -------------------- | ------------- |
| 4%                  | 60           | 2100                 | Read 210 × 10 |
| 5%                  | 57           | 2500                 | Read 250 × 10 |
| 10%                 | 28           | 5300                 | Read 530 × 10 |
| >=14%               | 0-20         | 7300                 | Read 730 × 10 |


### EMPTY TRUCK (E) - 217,419 kg
Follow the E-curve and read where it intersects each grade line:

| Effective Grade (%) | Speed (km/h) | Retarding Force (kN) | Notes         |
| ------------------- | ------------ | -------------------- | ------------- |
| 10%                 | 60           | 2200                 | Read 220 × 10 |
| 15%                 | 44           | 3400                 | Read 340 × 10 |
| 20%                 | 33           | 4200                 | Read 420 × 10 |
| 25%                 | 28           | 5500                 | Read 550 × 10 |
| 30%                 | 24           | 6200                 | Read 620 × 10 |

---

