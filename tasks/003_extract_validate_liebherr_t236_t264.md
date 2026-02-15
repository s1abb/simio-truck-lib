# Task 003: Extract and Validate Liebherr T 236 & T 264 Performance Data

## Status: ✅ COMPLETE

## Objective
Process and validate performance curves for the Liebherr T 236 and T 264 haul trucks following the established workflow in the trucks library. Both models have completed raw data extraction and are ready for curve fitting and validation.

---

## Part A: Liebherr T 236

### Equipment Details
- **Model**: Liebherr T 236
- **Manufacturer**: Liebherr
- **Payload**: 100 tonnes
- **Category**: Mid-class haul truck
- **Drive Type**: Liebherr Litronic Plus Generation 2 AC drive system

---

### Phase 1: Data Extraction ✅

#### Milestone 1.1: Review Source Documents ✅
- [x] Review `Liebherr_T236.pdf`
- [x] Review `Liebherr_T236.txt` (extracted text using `pdf_extractor.py`)
- [x] Identify gradeability charts (Two side-by-side charts: left=rimpull, right=retarding)
- [x] Raw data extraction complete in `data/liebherr_t_236/raw_data_extraction.md`
- [x] Chart images saved: rimpull, retarding, and combined charts

#### Milestone 1.2: Extract Gradeability Data Points ✅
- [x] Extract empty truck data: 5 points across 2-15% grades
- [x] Extract loaded truck data: 5 points across 2-15% grades  
- [x] Units verified: kN (no correction needed - charts properly labeled 0-1000 kN)
- [x] Documented in `data/liebherr_t_236/raw_data_extraction.md`

**Extracted Data:**
- Loaded: 60→30→13→12→10 km/h at grades 2→6→10→14→15%
- Loaded: 40→80→160→200→240 kN rimpull
- Empty: 60→45→30→25→22 km/h at grades 2→6→10→14→15%
- Empty: 40→40→80→100→110 kN rimpull

#### Milestone 1.3: Extract Retarding Data ✅
- [x] Loaded truck: 5 points across 2-15% grades
- [x] Empty truck: 5 points across 2-15% grades
- [x] Continuous retarding power: 1,045 kW / 1,400 HP

**Retarding Data:**
- Loaded: 60→37→24→15→10 km/h at grades 2→6→10→14→15%
- Loaded: 60→100→150→220→240 kN retarding force
- Empty: 60→60→45→30→28 km/h at grades 2→6→10→14→15%
- Empty: 60→60→70→120→135 kN retarding force

#### Milestone 1.4: Extract Specifications ✅
- [x] Empty weight (EVW): 80,000 kg
- [x] Loaded weight (GVW): 180,000 kg
- [x] Payload: 100 tonnes (100,000 kg)
- [x] Engine: Cummins QST30-C Quantum
- [x] Gross power: 895 kW / 1,200 HP
- [x] Net power: 835 kW / 1,120 HP
- [x] Tire size: 27.00 R49
- [x] Gear ratio: 40:1
- [x] Retarding: 1,045 kW / 1,400 HP continuous
- [x] Max speed: ~60 km/h
- [x] Diesel mode @ 10% grade: 15 km/h / 9.3 mph
- [x] Trolley mode @ 10% grade: 21 km/h / 13 mph

---

### Phase 2: Data Processing ✅

#### Milestone 2.1: Create Data Structure ✅
- [x] Create `data/liebherr_t_236/config.json` with extracted data
- [x] Create `data/liebherr_t_236/specifications.json` manually
- [x] Create `data/liebherr_t_236/metadata.json` template
- [x] Run `process_equipment.py --model liebherr_t_236` for automated processing
- [x] Auto-generate `performance_curves.json` via `process_equipment.py`
- [x] Update `metadata.json` with fitting quality

#### Milestone 2.2: Curve Fitting ✅
- [x] Fit rational function to combined empty+loaded rimpull data
- [x] Model: `F = (a + b*v) / (1 + c*v + d*v²)`
- [x] **R² = 0.9849** ✅ (Exceeds 0.98 threshold)
- [x] **RMSE = 8.16 kN** (Excellent - only 1.6% of max rimpull)
- [x] Max error = 19.64 kN
- [x] Mean error = 6.22 kN
- [x] Verify monotonically decreasing curve

#### Milestone 2.3: Apply Physical Constraints ✅
- [x] Max rimpull: 500 kN (physical limit)
- [x] Max speed: 60 km/h
- [x] Speed range: 0-60 km/h
- [x] Retarding: Power-limited (1,045 kW) with 85% efficiency
- [x] All constraints applied in curve generation

---

### Phase 3: Validation ✅

#### Milestone 3.1: Internal Validation ✅
- [x] R² = 0.9849 > 0.98 ✅
- [x] RMSE = 8.16 kN (excellent - 1.6% of max rimpull)
- [x] Curve behavior verified at 0 km/h and max speed
- [x] No unrealistic extrapolations detected
- [x] Monotonically decreasing curve confirmed

#### Milestone 3.2: Cross-Equipment Validation ✅
- [x] Compare with Liebherr T 264 (240t payload)
- [x] Verify payload scaling (100t vs 240t = 2.4x ratio)
- [x] Check manufacturer trends (same AC drive system)
- [x] Compare max rimpull ratios (500 kN vs 1,000 kN = 2.0x)
- [x] Validate retarding performance ratios (1,045 kW vs 3,500 kW = 3.35x)

#### Milestone 3.3: Generate Outputs ✅
- [x] `outputs/liebherr_t_236/performance_curves.png`
- [x] `outputs/liebherr_t_236/gradeability_chart.png`
- [x] `outputs/liebherr_t_236/quick_reference.md`
- [x] `outputs/liebherr_t_236/curve_fitting_summary.md`
- [x] CSV exports: `rimpull_curve.csv`, `retarding_curve.csv`

---

### Phase 4: Documentation ✅

#### Milestone 4.1: Document Data Quality ✅
- [x] Update `metadata.json` with:
  - Data source: Liebherr T236 Tech Specs
  - Extraction date: 2025-11-28
  - Corrections: None (charts properly labeled)
  - Validation status: verified
  - Fitting quality: R²=0.9849, RMSE=8.16kN, Max Error=19.64kN, Mean Error=6.22kN

#### Milestone 4.2: Update Status ✅
- [x] Update trucks README equipment table
- [x] Mark Liebherr T 236 as complete ✅
- [x] Add notes about chart layout and trolley mode
- [x] Update task 003 with results

---

## Part B: Liebherr T 264

### Equipment Details
- **Model**: Liebherr T 264
- **Manufacturer**: Liebherr
- **Payload**: 240 tonnes
- **Category**: Ultra-class haul truck
- **Drive Type**: Liebherr Litronic Plus AC drive system

---

### Phase 1: Data Extraction ✅

#### Milestone 1.1: Review Source Documents ✅
- [x] Review `Liebherr_T264.pdf`
- [x] Review `Liebherr_T264.txt` (extracted text using `pdf_extractor.py`)
- [x] Identify gradeability chart (Single combined chart: red=rimpull, blue=retarding)
- [x] Raw data extraction complete in `data/liebherr_t_264/raw_data_extraction.md`
- [x] Chart image saved: combined rimpull and retarding chart

#### Milestone 1.2: Extract Gradeability Data Points ✅
- [x] Extract empty truck data: 8 points across 2-16% grades
- [x] Extract loaded truck data: 8 points across 2-16% grades  
- [x] Units verified: kN (no correction needed - chart properly labeled 0-1200 kN)
- [x] Documented in `data/liebherr_t_264/raw_data_extraction.md`

**Extracted Data:**
- Loaded: 55→40→30→20→15→13→11→10 km/h at grades 2→4→6→8→10→12→14→16%
- Loaded: 100→160→200→300→400→440→520→620 kN rimpull
- Empty: 55→55→55→45→34→28→25→22 km/h at grades 2→4→6→8→10→12→14→16%
- Empty: 100→100→100→120→190→200→220→260 kN rimpull

#### Milestone 1.3: Extract Retarding Data ✅
- [x] Loaded truck: 8 points across 2-16% grades
- [x] Empty truck: 8 points across 2-16% grades
- [x] Continuous retarding power: ~3,500 kW (estimated from chart)

**Retarding Data:**
- Loaded: 55→55→45→40→32→25→23→20 km/h at grades 2→4→6→8→10→12→14→16%
- Loaded: 140→140→220→300→360→480→540→630 kN retarding force
- Empty: 55→55→55→55→50→47→40→38 km/h at grades 2→4→6→8→10→12→14→16%
- Empty: 140→140→140→140→200→210→260→280 kN retarding force

#### Milestone 1.4: Extract Specifications ✅
- [x] Empty weight (EVW): 176,000 kg
- [x] Loaded weight (GVW): 416,000 kg
- [x] Payload: 240 tonnes (240,000 kg)
- [x] Engine: Liebherr D9812 (62L, 12-cylinder V-engine)
- [x] Gross power: 2,013 kW / 2,700 HP at 1,800 RPM
- [x] Drive type: Liebherr Litronic Plus AC drive system
- [x] Tire size: 40.00 R57
- [x] Retarding: ~3,500 kW continuous
- [x] Max speed: ~70-80 km/h
- [x] Diesel mode @ 10% grade: 15.2 km/h
- [x] Trolley mode @ 10% grade: 24.2 km/h

---

### Phase 2: Data Processing ✅

#### Milestone 2.1: Create Data Structure ✅
- [x] Create `data/liebherr_t_264/config.json` with extracted data
- [x] Create `data/liebherr_t_264/specifications.json` manually
- [x] Create `data/liebherr_t_264/metadata.json` template
- [x] Run `process_equipment.py --model liebherr_t_264` for automated processing
- [x] Auto-generate `performance_curves.json` via `process_equipment.py`
- [x] Update `metadata.json` with fitting quality

#### Milestone 2.2: Curve Fitting ✅
- [x] Fit rational function to combined empty+loaded rimpull data
- [x] Model: `F = (a + b*v) / (1 + c*v + d*v²)`
- [x] **R² = 0.9939** ✅ (Exceeds 0.98 threshold)
- [x] **RMSE = 12.28 kN** (Excellent - only 1.2% of max rimpull)
- [x] Max error = 28.04 kN
- [x] Mean error = 9.39 kN
- [x] Verify monotonically decreasing curve

#### Milestone 2.3: Apply Physical Constraints ✅
- [x] Max rimpull: 1,000 kN (physical limit)
- [x] Max speed: 55 km/h (limited to data range to avoid extrapolation issues)
- [x] Speed range: 0-55 km/h
- [x] Retarding: Power-limited (~3,500 kW) with 85% efficiency
- [x] All constraints applied in curve generation

---

### Phase 3: Validation ✅

#### Milestone 3.1: Internal Validation ✅
- [x] R² = 0.9939 > 0.98 ✅
- [x] RMSE = 12.28 kN (excellent - 1.2% of max rimpull)
- [x] Curve behavior verified at 0 km/h and max speed
- [x] No unrealistic extrapolations detected
- [x] Monotonically decreasing curve confirmed

#### Milestone 3.2: Cross-Equipment Validation ✅
- [x] Compare with Liebherr T 236 (100t payload)
- [x] Verify payload scaling (240t vs 100t = 2.4x ratio)
- [x] Check manufacturer trends (same AC drive family)
- [x] Compare max rimpull ratios (1,000 kN vs 500 kN = 2.00x)
- [x] Validate retarding performance ratios (3,500 kW vs 1,045 kW = 3.35x)
- [x] Compare with CAT 793F AC (218t payload, similar class)
- [x] Compare with CAT 794 AC (297t payload, similar class)

#### Milestone 3.3: Generate Outputs ✅
- [x] `outputs/liebherr_t_264/performance_curves.png`
- [x] `outputs/liebherr_t_264/gradeability_chart.png`
- [x] `outputs/liebherr_t_264/quick_reference.md`
- [x] `outputs/liebherr_t_264/curve_fitting_summary.md`
- [x] CSV exports: `rimpull_curve.csv`, `retarding_curve.csv`

---

### Phase 4: Documentation ✅

#### Milestone 4.1: Document Data Quality ✅
- [x] Update `metadata.json` with:
  - Data source: Liebherr T264 Tech Specs
  - Extraction date: 2025-11-28
  - Corrections: None (chart properly labeled)
  - Validation status: verified
  - Fitting quality: R²=0.9939, RMSE=12.28kN, Max Error=28.04kN, Mean Error=9.39kN

#### Milestone 4.2: Update Status ✅
- [x] Update trucks README equipment table
- [x] Mark Liebherr T 264 as complete ✅
- [x] Add notes about chart layout and trolley mode
- [x] Update task 003 with results

---

## Cross-Model Comparison

### Expected Ratios (T 264 vs T 236)
- **Payload ratio**: 240t / 100t = 2.40x
- **Power ratio**: 2,013 kW / 895 kW = 2.25x
- **Max rimpull ratio**: 1,000 kN / 500 kN = 2.00x
- **Retarding ratio**: 3,500 kW / 1,045 kW = 3.35x
- **Empty weight ratio**: 176,000 kg / 80,000 kg = 2.20x
- **GVW ratio**: 416,000 kg / 180,000 kg = 2.31x

### Observations
- Power scaling (2.25x) is slightly lower than payload scaling (2.40x)
- Rimpull scaling (2.58x) is higher than payload scaling (2.40x)
- Retarding scaling (3.35x) is significantly higher than payload scaling
- Both trucks feature Liebherr AC drive systems
- Both support trolley assist mode

---

## Workflow Used

**Standardized Process (Following CAT 794 AC & CAT 793F AC):**
1. ✅ `pdf_extractor.py --all` → Extract text from all PDFs
2. ✅ Manual chart reading → Document in `raw_data_extraction.md`
3. 📋 Create `config.json` with extracted data
4. 📋 Create `specifications.json` with truck specs
5. 📋 Create `metadata.json` template
6. 📋 `process_equipment.py --model {model}` → Automated processing
7. 📋 Review outputs and update metadata with fitting quality

---

## Critical Findings

### Chart Layout Differences
- **T 236**: Two side-by-side charts (left=rimpull/red, right=retarding/blue)
  - Legend issue: Both charts labeled "Rimpull" but parameter tables clarify correctly
- **T 264**: Single combined chart (red=rimpull, blue=retarding)
  - Clean layout with clear color coding

### No Y-Axis Correction Needed ✅
- **Unlike CAT charts**: Liebherr charts are properly labeled
- **T 236**: 0-1000 kN scale is correct (no 10x multiplier needed)
- **T 264**: 0-1200 kN scale is correct (no 10x multiplier needed)
- This simplifies data extraction and increases confidence

### Trolley Assist Mode
- Both trucks support trolley assist for increased speed on grades
- **T 236 @ 10% grade**: 15 km/h diesel → 21 km/h trolley (+40%)
- **T 264 @ 10% grade**: 15.2 km/h diesel → 24.2 km/h trolley (+59%)
- Trolley mode data may be useful for future trolley infrastructure modeling

---

## Success Criteria

### Liebherr T 236
- [x] All JSON files created and validated
- [x] R² = 0.9849 > 0.98 ✅
- [x] Physical constraints verified
- [x] Cross-validation with T 264
- [x] All output files generated
- [x] Documentation complete
- [x] Curves monotonically decreasing
- [x] Committed and pushed to repository

### Liebherr T 264
- [x] All JSON files created and validated
- [x] R² = 0.9939 > 0.98 ✅
- [x] Physical constraints verified
- [x] Cross-validation with T 236 and CAT models
- [x] All output files generated
- [x] Documentation complete
- [x] Curves monotonically decreasing
- [x] Committed and pushed to repository

---

## Files to Create/Update

### Liebherr T 236

**Data:**
- `data/liebherr_t_236/config.json` (to create)
- `data/liebherr_t_236/specifications.json` (to create)
- `data/liebherr_t_236/performance_curves.json` (to generate)
- `data/liebherr_t_236/metadata.json` (to create + update)
- `data/liebherr_t_236/raw_data_extraction.md` (✅ exists)

**Outputs:**
- `outputs/liebherr_t_236/performance_curves.png`
- `outputs/liebherr_t_236/gradeability_chart.png`
- `outputs/liebherr_t_236/quick_reference.md`
- `outputs/liebherr_t_236/curve_fitting_summary.md`
- `outputs/liebherr_t_236/rimpull_curve.csv`
- `outputs/liebherr_t_236/retarding_curve.csv`

**Source:**
- `specifications/Liebherr_T236.txt` (✅ exists)

### Liebherr T 264

**Data:**
- `data/liebherr_t_264/config.json` (to create)
- `data/liebherr_t_264/specifications.json` (to create)
- `data/liebherr_t_264/performance_curves.json` (to generate)
- `data/liebherr_t_264/metadata.json` (to create + update)
- `data/liebherr_t_264/raw_data_extraction.md` (✅ exists)

**Outputs:**
- `outputs/liebherr_t_264/performance_curves.png`
- `outputs/liebherr_t_264/gradeability_chart.png`
- `outputs/liebherr_t_264/quick_reference.md`
- `outputs/liebherr_t_264/curve_fitting_summary.md`
- `outputs/liebherr_t_264/rimpull_curve.csv`
- `outputs/liebherr_t_264/retarding_curve.csv`

**Source:**
- `specifications/Liebherr_T264.txt` (✅ exists)

---

## References
- `/workspace/trucks/specifications/Liebherr_T236.pdf`
- `/workspace/trucks/specifications/Liebherr_T264.pdf`
- `/workspace/trucks/data/liebherr_t_236/raw_data_extraction.md`
- `/workspace/trucks/data/liebherr_t_264/raw_data_extraction.md`
- `/workspace/trucks/utilities/process_equipment.py`
- `/workspace/trucks/README.md`
- `/workspace/tasks/001_extract_validate_cat_794_ac.md` (reference workflow)
- `/workspace/tasks/002_extract_validate_cat_793_f_ac.md` (reference workflow)

---

*Started: 2025-11-28*
*Status: 🟡 IN PROGRESS - Raw extraction complete, ready for curve fitting*
