# Discrete-Event Simulation — Tire Manufacturing Factory

A SimPy-based discrete-event simulation of a tire R&D manufacturing facility, built as part of **1BK50: Algorithmic Programming for Operations Management** at **Eindhoven University of Technology (TU/e)**.

---

## Assignment Overview

This project models the end-to-end production workflow of a tire manufacturer's R&D department — from receiving custom orders to final shipping. The factory processes two types of tire prototype orders:

- **Type A (Standard Design):** Predefined designs, making up ~90% of orders
- **Type B (Sports Design):** Tailored prototypes for specific vehicle models, ~10% of orders

Orders flow through six sequential production stages:

| Stage | Description | Duration |
|---|---|---|
| 1. Tire Design | Engineering design phase | A: 2–5 days / B: 5–10 days |
| 2. Subcomponent Collection | Sourcing parts (in-stock or on-request) | 3–6 hrs (70%) or 2–5 days (30%) |
| 3. Tire Assembly | Physical assembly, with 5% failure risk | 1–3 days |
| 4. Tire Curing | High-temperature curing | Exactly 3 days |
| 5. Quality Inspection | Standard + optional rigorous check (1%) | 12 hrs (+24 hrs if flagged) |
| 6. Shipping | Pack and dispatch | 12 hrs |

The simulation runs over a **1-year horizon (8,760 hours)**, with orders arriving at an exponential rate of λ = 0.5/day (mean inter-arrival: 2 days).

---

## Exercises

### Exercise 1 — Base Simulation
Implements the core SimPy simulation with a single resource per stage. Tracks order counts at each production stage, broken down by tire type (A and B). Establishes the foundational event-driven architecture that all subsequent exercises build on.

### Exercise 2 — Performance Analytics
Extends Exercise 1 with data collection and analysis functions:
- **`compute_resource_utilization()`** — calculates the percentage of time each resource is occupied
- **`compute_average_cycle_time()`** — computes mean order-to-completion time per tire type
- **`plot_cycle_times()`** — visualizes how cycle times evolve throughout the simulation as orders queue and bottlenecks form

### Exercise 3 — Advanced Scheduling
Introduces three significant model enhancements:
- **Priority queueing** — Type B orders preempt queue position over Type A at every stage using `simpy.PriorityResource`
- **Shared resources** — The curing resource can assist at assembly; the shipping resource can assist at inspection, simulating flexible worker allocation
- **Predefined arrivals** — Replaces stochastic arrivals with a fixed schedule loaded from `order_arrival_information.json`, enabling reproducible scenario testing

### Exercise 4 — Investment Optimization
Frames the simulation as a decision-support tool for capacity planning:
- Enumerates all valid resource investment combinations within a given budget
- Runs **5 replications** per configuration to account for stochastic variability
- Identifies the optimal allocation that maximizes order completion rate
- Targets a **95% completion rate** across configurable budgets

---

## Skills Demonstrated

### Discrete-Event Simulation (SimPy)
Built multi-stage production pipelines using SimPy's process-based paradigm — modelling concurrent processes, resource contention, and event-driven state transitions from scratch across four progressively complex scenarios.

### Stochastic Modelling
Applied probability distributions (exponential inter-arrivals, uniform processing times, Bernoulli failure events) to represent real-world manufacturing variability. Carefully seeded random number generators to balance reproducibility with realistic variance.

### Resource & Queue Management
Implemented both standard (`simpy.Resource`) and priority-based (`simpy.PriorityResource`) queuing. Modelled shared resource pools where workers can dynamically assist across stages — a non-trivial scheduling pattern that reflects real shop-floor flexibility.

### Simulation Design Patterns
Structured the simulation using object-oriented design with clean separation between process logic, resource management, and statistics collection. Each exercise maintains backward compatibility with the base class interface, demonstrating disciplined incremental development.

### Performance Analysis & KPI Tracking
Tracked and computed meaningful operational KPIs including resource utilisation rates, per-type cycle times, and throughput ratios — translating raw simulation output into actionable factory performance insights.

### Scenario-Based Decision Support
Extended the simulation into an optimisation framework: systematically exploring a combinatorial investment space, running replications to smooth stochastic noise, and surfacing the optimal resource configuration for a given budget constraint.

### Data Visualisation
Used Matplotlib to plot cycle time development over the simulation horizon, enabling visual identification of queue build-up and throughput degradation over time.

---

## Getting Started

**Prerequisites:**
```bash
pip install simpy numpy matplotlib
```

**Run any exercise:**
```bash
python Simulation_Exercise1_final.py
python Simulation_Exercise2_final.py
python Simulation_exercise3_final.py
python Simulation_Exercise4_final.py
```

Note: Exercise 3 requires `order_arrival_information.json` to be in the same directory.

---

## Files

| File | Description |
|---|---|
| `Simulation_Exercise1_final.py` | Base simulation |
| `Simulation_Exercise2_final.py` | + Analytics & visualisation |
| `Simulation_exercise3_final.py` | + Priority queuing & shared resources |
| `Simulation_Exercise4_final.py` | + Investment optimisation |
| `order_arrival_information.json` | Predefined order arrival schedule (Exercise 3) |
