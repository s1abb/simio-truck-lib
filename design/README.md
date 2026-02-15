# Mining Truck Electrification Simulation - Design Documentation

**Version**: 3.0  
**Last Updated**: November 27, 2025  
**Repository**: simio-electric-truck-lib

---

## Overview

Complete design documentation for mining truck electrification simulation supporting:
- **6 truck models** with **12 operating configurations**
- **3 truck modes**: BatterySwap, DieselElectric, BatteryElectric
- **4 assist modes**: StandAlone, PreserveEnergy, PreserveBattery, SustainSpeed
- **Universal physics**: Speed dynamics, power flow, battery degradation, fuel consumption

---

## Documentation Structure

### 📚 [research/](research/) - Industry Research & Market Analysis

External research, vendor specifications, white papers, economic analysis.

**Files:**
- [Battery Electric Haul Trucks Decoding Trade-offs and Maximising Value.md](research/Battery%20Electric%20Haul%20Trucks%20Decoding%20Trade-offs%20and%20Maximising%20Value.md)
- [MINExpo 2024 and International Mining Update.md](research/MINExpo%202024%20and%20International%20Mining%20Update.md)

**Key topics**: Operating model tradeoffs (plug-in, swappable, trolley-assist), battery lifecycle economics, DoD impact on cycle life, vendor technologies (Liebherr Power Rail, CAT DET, ABB eMine, Stäubli charging)

---

### 🎯 [concept/](concept/) - Conceptual Design

Mode-agnostic physics models, algorithms, architecture, operating philosophy.

**Files:**
- [01-fleet-and-modes.md](concept/01-fleet-and-modes.md) - 6 trucks × 12 configurations matrix
- [02-physics-speed-force.md](concept/02-physics-speed-force.md) - Universal speed dynamics, power-limited scaling
- [03-power-flow.md](concept/03-power-flow.md) - Mode-specific energy management
- [04-battery-management.md](concept/04-battery-management.md) - SOC tracking and calculations
- [05-fuel-systems.md](concept/05-fuel-systems.md) - Diesel consumption and refueling
- [06-infrastructure.md](concept/06-infrastructure.md) - Paths, stations, service flag system
- [07-trolley-power-sharing.md](concept/07-trolley-power-sharing.md) - Dynamic power allocation
- [08-degradation-models.md](concept/08-degradation-models.md) - Throughput vs cycle-life models

---

### ⚙️ [simio/](simio/) - Simio Implementation

Simio-specific processes, properties, tables, expressions.

**Files:**
- [proc_PhysicsUpdates_BatterySwap.md](simio/proc_PhysicsUpdates_BatterySwap.md)
- [proc_PhysicsUpdates_BatteryElectric_PreserveEnergy.md](simio/proc_PhysicsUpdates_BatteryElectric_PreserveEnergy.md)
- [proc_PhysicsUpdates_BatteryElectric_SustainSpeed.md](simio/proc_PhysicsUpdates_BatteryElectric_SustainSpeed.md)
- [proc_PhysicsUpdates_BatteryElectric_RechargeBattery.md](simio/proc_PhysicsUpdates_BatteryElectric_RechargeBattery.md)
- [proc_PhysicsUpdates_DieselElectric_PreserveEnergy.md](simio/proc_PhysicsUpdates_DieselElectric_PreserveEnergy.md)
- [proc_PhysicsUpdates_DieselElectric_SustainSpeed.md](simio/proc_PhysicsUpdates_DieselElectric_SustainSpeed.md)
- [proc_PhysicsUpdates_DieselElectric_RefuelDiesel.md](simio/proc_PhysicsUpdates_DieselElectric_RefuelDiesel.md)
- [properties_variables_tables.md](simio/properties_variables_tables.md)

---




