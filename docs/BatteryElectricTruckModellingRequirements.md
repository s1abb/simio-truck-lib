# Battery Electric Truck Modelling Requirements

**Version:** 1.0  
**Date:** October 20, 2025  
**Work Package:** 1 of 4  
**Delivery:** 24 October 2025

---

## Overview

Integrate battery electric truck functionality into the mine module with battery behavior, swap station operations, and degradation modeling.

---

## Development Steps

### Step 1: Requirements Specification & Model Architecture

**Collaborate with SMTP team** to finalize specifications for:
- Battery behavior
- Swap station operations
- Degradation modeling

**Design object architecture:**
- New Battery and Swapping Station objects
- Enhanced Truck objects
- Modular custom Simio elements for extensibility

---

### Step 2: Battery Object Development

Create **Battery entity** tracking:
- Current charge level (kWh)
- Degradation state (health %)
- Cycle count and age
- Current state (in use, charging, idle)

**Simulate battery degradation** based on:
- Usage cycles
- Depth of discharge

---

### Step 3: Truck Enhancements

Extend **Truck object** to:
- Reference installed Battery object
- Synchronize truck performance with battery health
- Enable battery swapping logic (charge thresholds or scheduling)

---

### Step 4: Swapping Station Modelling

Develop **Swapping Station object** with:

**Truck bays:**
- Queuing and processing logic

**Robot swapping sub-object:**
- Battery removal and replacement logic
- Failure and maintenance downtime modeling

**Charging infrastructure:**
- Charging slots per bay
- Queuing logic (FIFO) for empty batteries
- Time-dependent charging rates and efficiency losses

---

### Step 5: System Integration and Testing

**Incremental integration:**
- Validate compatibility with existing pathing and operational rules

**Scenario-based testing to ensure:**
- Truck performance adjusts realistically with battery state
- Charging and swapping stations interact efficiently with haulage demand
- System bottlenecks (charging queue lengths) are observable

---

## Dependencies

- Existing Truck objects
- Simio path and routing functionality
- Work Package 3 (Dynamic Charging Path)
