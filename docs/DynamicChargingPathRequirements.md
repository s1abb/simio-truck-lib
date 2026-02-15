# Dynamic Charging Path Requirements

**Version:** 1.0  
**Date:** October 20, 2025  
**Work Package:** 3 of 4  
**Delivery:** 28 November 2025

---

## Overview

Develop dynamic charging path object to simulate in-motion charging infrastructure, accurately modeling real-time charging for battery electric trucks traveling along designated routes.

---

## Development Steps

### Step 1: Requirements Analysis and Object Design

**Collaborate with SMTP team** to define operational parameters:
- Charging path locations
- Compatible vehicle types
- Operational constraints:
  - Maximum simultaneous users
  - Speed limitations

**Design Dynamic Charging Path object:**
- Build on Simio's path functionality
- Enhanced with custom logic for energy transfer and traffic management

---

### Step 2: Dynamic Charging Object Development

Develop **specialized charging path** with logic to:

**Detect when truck is on path**

**Calculate energy** based on:
- Speed
- Time on path
- Truck battery state

**Respect maximum truck limits:**
- Trigger queuing or rerouting if necessary

**Integrated parameters:**
- Charging rate (kW) per path
- Speed limit enforcement
- Partial charging logic (energy added dynamically based on time-on-path and efficiency)

---

### Step 3: Interaction with Truck and Battery Objects

**Extend obj_Truck logic** (from Work Package 1) to:
- Recognize entry/exit from dynamic charging zones
- Update battery object state during travel

---

### Step 4: Traffic and Capacity Constraints

Implement **traffic control logic:**
- Maximum number of trucks actively charging on a segment
- Trigger alternative logic if path at capacity

---

### Step 5: Integration with Mine Module

**Ensure charging object integrates** with:
- Existing routing logic
- No model-wide restructuring required

---

## Dependencies

- Work Package 1 (Battery Electric Truck) - Battery and Truck objects
- Existing Simio path infrastructure
- Mine module routing logic
