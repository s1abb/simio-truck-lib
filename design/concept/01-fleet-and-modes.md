# Fleet Configuration & Operating Modes

**Purpose:** Define the 6 trucks with 12 operating configurations and their mode-specific behaviors  
**Related:** [02-physics-speed-force.md](02-physics-speed-force.md), [03-power-flow.md](03-power-flow.md)

---

## Fleet Composition

**6 Trucks, 12 Operating Configurations**

| Truck                  | Payload | TruckMode       | ElectricAssistMode | Trolley Capable | Battery Capacity | Generator Power |
| ---------------------- | ------- | --------------- | ------------------ | --------------- | ---------------- | --------------- |
| TONLY DTE145           | 85-91t  | BatterySwap     | N/A                | ❌ No            | 801 kWh          | 0               |
| Liebherr T236          | 100t    | DieselElectric  | PreserveEnergy     | ✅ Yes           | 0                | 895 kW          |
| Liebherr T236          | 100t    | DieselElectric  | SustainSpeed      | ✅ Yes           | 0                | 895 kW          |
| CAT 793F AC            | 218t    | DieselElectric  | PreserveEnergy     | ✅ Yes           | 0                | 1,950 kW        |
| CAT 793F AC            | 218t    | DieselElectric  | SustainSpeed      | ✅ Yes           | 0                | 1,950 kW        |
| Liebherr T 264 BE      | 240t    | BatteryElectric | StandAlone         | ✅ Yes           | 3,200 kWh        | 0               |
| Liebherr T 264 BE      | 240t    | BatteryElectric | PreserveBattery    | ✅ Yes           | 3,200 kWh        | 0               |
| Liebherr T 264 BE      | 240t    | BatteryElectric | SustainSpeed      | ✅ Yes           | 3,200 kWh        | 0               |
| Liebherr T264 (diesel) | 240t    | DieselElectric  | PreserveEnergy     | ✅ Yes           | 0                | 2,013 kW        |
| Liebherr T264 (diesel) | 240t    | DieselElectric  | SustainSpeed      | ✅ Yes           | 0                | 2,013 kW        |
| CAT 794 AC             | 297t    | DieselElectric  | PreserveEnergy     | ✅ Yes           | 0                | 2,539 kW        |
| CAT 794 AC             | 297t    | DieselElectric  | SustainSpeed      | ✅ Yes           | 0                | 2,539 kW        |

---

## Truck Modes

### 1. BatterySwap Mode

**Trucks:** TONLY DTE145 (85-91t)

**Characteristics:**
- Battery as primary energy source (swappable)
- Swaps battery when SOC < threshold (typically 80%)
- **Does NOT interact with obj_ElectricPath** (passes through as regular path)
- Uses `obj_BatterySwapChargeStation` for battery swap operations
- Simple throughput-based battery degradation model

**Energy Flow:**
```
Driving Power Demand → Battery Only
Battery SOC → Decreases during operation
When SOC < SwapBatterySOCPct → Navigate to swap station
```

**Use Case:**
- Proven technology for smaller trucks (60-100t)
- Fast turnaround, high utilization
- Battery inventory managed separately from truck

**Status:** ✅ Fully implemented and working

---

### 2. DieselElectric Mode

**Trucks:** Liebherr T236 (100t), CAT 793F AC (218t), Liebherr T264 diesel (240t), CAT 794 AC (297t)

**Characteristics:**
- Diesel generator as primary energy source (always available)
- Interacts with `obj_ElectricPath` for trolley assist
- No battery swapping or depot charging
- Two assist modes: **PreserveEnergy** or **SustainSpeed**
- No battery degradation (no battery)

**Energy Sources:**
- **Primary:** Diesel generator (constant power output)
- **Supplemental:** Trolley assist (when on electric path)

**Electric Assist Modes:**

#### 2A. DieselElectric + PreserveEnergy

**Objective:** Minimize diesel consumption by letting trolley provide all driving energy when on electric path

**Power Flow (On Electric Path):**
```
IF TrolleyAvailablePowerKw ≥ DrivingPowerDemand:
    TrolleyPowerKw = DrivingPowerDemand  // Trolley provides motor + auxiliary
    DieselPowerKw = 0                     // Diesel generator off/idle
    
ELSE:
    TrolleyPowerKw = TrolleyAvailablePowerKw  // Use max available
    DieselPowerKw = Shortfall                  // Diesel supplements
```

**Power Flow (Off Electric Path):**
```
DieselPowerKw = DrivingPowerDemand
TrolleyPowerKw = 0
```

**Key Behavior:**
- Speed/force unchanged from diesel-only operation
- Energy source changes but performance characteristics don't
- 95-98% fuel savings on trolley sections

**Use Case:**
- Fuel cost optimization
- Standard operating mode for cost reduction

#### 2B. DieselElectric + SustainSpeed

**Objective:** Maximize performance by combining diesel and trolley power

**Power Flow (On Electric Path):**
```
DieselPowerKw = DieselGeneratorMaxPowerKw           // Diesel at full output
TrolleyPowerKw = TrolleyAvailablePowerKw            // Dynamic based on active trucks
TotalAvailablePowerKw = DieselPowerKw + TrolleyPowerKw
```

**Power Flow (Off Electric Path):**
```
DieselPowerKw = DieselGeneratorMaxPowerKw
TrolleyPowerKw = 0
TotalAvailablePowerKw = DieselPowerKw
```

**Key Behavior:**
- Uses power-limited scaling factor (P = F × V)
- Higher power enables sustaining higher speeds on grades
- Speed increase: 1.3x-1.78x on 10% grade loaded
- Tractive force limited by min(curve limit, power limit)

**Use Case:**
- Production optimization
- Use when production value exceeds fuel cost

---

### 3. BatteryElectric Mode

**Trucks:** Liebherr T 264 BE (240t)

**Characteristics:**
- Battery as primary energy source (rechargeable, non-swappable)
- Charges at depot/pit charging stations or via trolley
- Interacts with `obj_ElectricPath` for trolley assist AND charging
- Three assist modes: **StandAlone**, **PreserveBattery**, or **SustainSpeed**
- Advanced cycle-life based battery degradation model

**Energy Sources:**
- **Primary:** Battery (capacity varies with SOC and health)
- **Supplemental:** Trolley assist (when on electric path)
- **Charging:** Trolley can charge battery with excess power

**Electric Assist Modes:**

#### 3A. BatteryElectric + StandAlone

**Objective:** Independent operation without trolley infrastructure

**Power Flow:**
```
BatteryPowerKw = DrivingPowerDemand  // Battery only
TrolleyPowerKw = 0
```

**Key Behavior:**
- No trolley interaction (passes through electric paths)
- High battery stress
- Frequent charging required
- DoD per cycle: 20-30% (high stress)
- Battery life: 1-2 years

**Use Case:**
- Routes without trolley infrastructure
- Emergency/backup operation
- **NOT RECOMMENDED for standard operations**

#### 3B. BatteryElectric + PreserveBattery

**Objective:** Preserve battery energy by using trolley for driving AND charge battery with excess trolley power

**Power Flow (On Electric Path - Surplus):**
```
IF TrolleyPowerKw > DrivingPowerDemand:
    TrolleyDrivingPowerKw = DrivingPowerDemand
    TrolleyChargingPowerKw = min(
        TrolleyPowerKw - DrivingPowerDemand,
        BatteryMaxChargePowerKw,
        PowerToReach100SOC
    )
    NetBatteryPowerKw = -TrolleyChargingPowerKw  // Negative = charging
    BatterySOC → Increases
```

**Power Flow (On Electric Path - Deficit):**
```
IF TrolleyPowerKw < DrivingPowerDemand:
    TrolleyDrivingPowerKw = TrolleyPowerKw
    BatteryPowerKw = DrivingPowerDemand - TrolleyPowerKw
    BatterySOC → Decreases (but less than without trolley)
```

**Power Flow (Off Electric Path):**
```
BatteryPowerKw = DrivingPowerDemand
TrolleyPowerKw = 0
BatterySOC → Decreases
```

**Key Behavior:**
- Battery SOC: 95% → 90% (shallow cycling)
- DoD per cycle: 2-5% (excellent - low stress)
- Battery life: 200,000+ cycles (truck lifetime)
- Think of as "continuously connected electric truck with battery bridging"

**Use Case:**
- Standard operations
- Maximize battery life
- Long-term sustainability
- **RECOMMENDED operating mode**

#### 3C. BatteryElectric + SustainSpeed

**Objective:** Maximize performance by combining battery and trolley power

**Power Flow (On Electric Path):**
```
MaxBatteryPowerKw = BatteryMaxPowerKw × PowerDegradationFactor
TrolleyPowerKw = TrolleyAvailablePowerKw
TotalAvailablePowerKw = MaxBatteryPowerKw + TrolleyPowerKw

Battery and trolley both discharge at maximum for peak performance
```

**Power Flow (Off Electric Path):**
```
MaxBatteryPowerKw = BatteryMaxPowerKw × PowerDegradationFactor
TrolleyPowerKw = 0
TotalAvailablePowerKw = MaxBatteryPowerKw
```

**Key Behavior:**
- Uses power-limited scaling factor with battery degradation
- Speed increase: 1.59x (15.2 → 24.2 km/h) on 10% grade loaded
- DoD per cycle: 10-15% (moderate stress)
- Battery life: 30,000-50,000 cycles (3-5 years)
- Motor peak rating used (60-second duration)

**Use Case:**
- Production optimization
- Accept battery replacement costs ($800k-$1.2M every 3-5 years)
- Use ONLY when production value justifies cost

---

## Physics Systems Matrix

| Truck                      | Mode                              | Speed Dynamics | Power Flow       | Motor Thermal | Battery SOC | Battery Degradation     | Fuel System |
| -------------------------- | --------------------------------- | -------------- | ---------------- | ------------- | ----------- | ----------------------- | ----------- |
| **TONLY DTE145**           | BatterySwap                       | ✅ Universal    | Battery-Only     | ✅ Universal   | ✅ Required  | ✅ Simple (Throughput)   | ❌           |
| **Liebherr T236**          | DieselElectric (PreserveEnergy)   | ✅ Universal    | Trolley-Replace  | ✅ Universal   | ❌           | ❌                       | ✅ Required  |
| **Liebherr T236**          | DieselElectric (SustainSpeed)    | ✅ Universal    | Trolley-Combine  | ✅ Universal   | ❌           | ❌                       | ✅ Required  |
| **CAT 793F AC**            | DieselElectric (PreserveEnergy)   | ✅ Universal    | Trolley-Replace  | ✅ Universal   | ❌           | ❌                       | ✅ Required  |
| **CAT 793F AC**            | DieselElectric (SustainSpeed)    | ✅ Universal    | Trolley-Combine  | ✅ Universal   | ❌           | ❌                       | ✅ Required  |
| **Liebherr T 264 BE**      | BatteryElectric (StandAlone)      | ✅ Universal    | Battery-Only     | ✅ Universal   | ✅ Required  | ✅ Advanced (Cycle-Life) | ❌           |
| **Liebherr T 264 BE**      | BatteryElectric (PreserveBattery) | ✅ Universal    | Trolley-Priority | ✅ Universal   | ✅ Required  | ✅ Advanced (Cycle-Life) | ❌           |
| **Liebherr T 264 BE**      | BatteryElectric (SustainSpeed)   | ✅ Universal    | Trolley-Combine  | ✅ Universal   | ✅ Required  | ✅ Advanced (Cycle-Life) | ❌           |
| **Liebherr T264 (diesel)** | DieselElectric (PreserveEnergy)   | ✅ Universal    | Trolley-Replace  | ✅ Universal   | ❌           | ❌                       | ✅ Required  |
| **Liebherr T264 (diesel)** | DieselElectric (SustainSpeed)    | ✅ Universal    | Trolley-Combine  | ✅ Universal   | ❌           | ❌                       | ✅ Required  |
| **CAT 794 AC**             | DieselElectric (PreserveEnergy)   | ✅ Universal    | Trolley-Replace  | ✅ Universal   | ❌           | ❌                       | ✅ Required  |
| **CAT 794 AC**             | DieselElectric (SustainSpeed)    | ✅ Universal    | Trolley-Combine  | ✅ Universal   | ❌           | ❌                       | ✅ Required  |

**Legend:**
- ✅ Universal: Applied to all trucks
- ✅ Required: Applied to this specific truck/mode
- ❌ Not applicable

---

## Operating Philosophy Summary

### BatterySwap
- Simple, proven technology for smaller trucks (60-100t)
- Fast turnaround, high utilization
- Battery inventory managed separately from truck

### DieselElectric + PreserveEnergy
- Fuel cost optimization
- Trolley replaces diesel when available
- 95-98% fuel savings on trolley sections
- Standard operating mode for cost reduction

### DieselElectric + SustainSpeed
- Production optimization
- Diesel + trolley combine for maximum power
- 1.3x-1.78x speed increase on grades
- Use when production value exceeds fuel cost

### BatteryElectric + StandAlone
- Independent operation (no trolley needed)
- High battery stress, short lifespan (1-2 years)
- NOT RECOMMENDED for standard operations

### BatteryElectric + PreserveBattery
- Battery life optimization
- Battery is for bridging, not primary power
- Low DoD (2-5%) = battery lasts truck lifetime
- **RECOMMENDED standard operating mode**

### BatteryElectric + SustainSpeed
- Production at cost of battery life
- Battery + trolley combine for maximum performance
- Moderate DoD (10-15%) = 3-5 year battery life
- Use only when production value justifies battery replacement costs

---

## Critical Insight

**For battery-electric trucks with trolley**, think of them as:
- **"Continuously connected electric trucks with a battery that enables them to travel between power sources"**

Rather than:
- ~~"Battery trucks that recharge via trolley"~~

This mindset shift is critical for understanding the PreserveBattery operating mode and why extended trolley coverage is essential for battery longevity.

---

## Related Documents

- [02-physics-speed-force.md](02-physics-speed-force.md) - Universal speed dynamics
- [03-power-flow.md](03-power-flow.md) - Mode-specific power combining logic
- [04-battery-management.md](04-battery-management.md) - SOC tracking
- [05-fuel-systems.md](05-fuel-systems.md) - Diesel consumption
- [06-infrastructure.md](06-infrastructure.md) - Electric paths and stations
- [07-trolley-power-sharing.md](07-trolley-power-sharing.md) - Dynamic power allocation
- [08-degradation-models.md](08-degradation-models.md) - Battery lifecycle modeling
