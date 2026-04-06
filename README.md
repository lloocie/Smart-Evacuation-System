# 🚨 FLOCK — Smart Evacuation Navigation System

French University in Armenia · Faculty of Computer Science and Applied Mathematics

> A B2B safety platform that computes real-time personalised evacuation routes
> for large multi-story buildings using BLE beacon positioning and graph-based
> BFS pathfinding — all backed by a fully normalised SQL Server database.

---

## 📖 Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [System Architecture](#system-architecture)
- [Algorithm Demo](#algorithm-demo)
- [Database](#database)
- [How to Run](#how-to-run)
- [Authors](#authors)

---

## Overview

During an emergency, occupants of large buildings — malls, hospitals, airports,
universities — may not know the nearest available exit, especially when routes
are blocked by fire or hazards. Existing static signage cannot adapt in real time.

**FLOCK** solves this by combining:

- **BLE beacon indoor positioning** — detects which floor and zone a user is in
- **Graph-based building model** — every room, hallway, and exit is a node
- **BFS pathfinding** — computes the shortest safe route to the nearest open exit
- **SQL Server database** — stores buildings, incidents, routes, and audit logs
- **Python desktop simulator** — visualises the algorithm on a live floor map

---

## Project Structure

```
FLOCK/
│
├── 📁 database/                    ← SQL Server T-SQL scripts (run in order)
│   ├── DB_CREATE.sql
│   ├── DB_DDL.sql
│   ├── DB_DML.sql
│   ├── DB_DQL.sql
│   ├── DB_Views.sql
│   ├── DB_Indexes.sql
│   ├── DB_Triggers.sql
│   ├── DB_Stored_Procedures.sql
│   ├── DB_DCL.sql
│   └── DB_Deploy.sql
│
├── 📁 algorithm/                   ← Python BFS/DFS visualiser
│   ├── main.py                     ← Tkinter GUI application
│   ├── algorithms.py               ← BFS + DFS implementations
│   └── .py                 ← Floor graph (nodes, edges, exits)
│
├── 📁 mvp/                         ← Hardware prototype
│   ├── 📁 tinkercad/               ← Circuit design (BLE beacon simulation)
│   └── 📁 photos/                  ← Prototype photos
│
├── 📁 presentation/                      ← Full academic report (PDF)
│   └── report_final.pdf
│   └── FLOCK.pdf
│
└── README.md
```

---

## System Architecture

The system is built around four layers that work together during an emergency:

```
User smartphone
      │
      │  detects nearest BLE beacon UUID
      ▼
BLE Beacon Hardware
      │
      │  UUID → floor_id + zone_id lookup
      ▼
SQL Server Database
      │
      │  fetch active incident + available exits
      ▼
BFS Routing Engine
      │
      │  shortest safe path → ordered RouteStep records
      ▼
Step-by-step guidance displayed to user
```

**Core database tables:** `BUILDING` → `FLOOR` → `ZONE` → `BEACON` → `EXIT_POINT`
→ `INCIDENT` → `EVACUATION_ROUTE` → `ROUTE_STEP` → `USER_LOCATION` + graph (`NODE`, `EDGE`)

All 15 tables are fully normalised to **3NF** with enforced foreign keys,
check constraints, triggers, and role-based access control.

---

## Algorithm Demo

The `algorithm/` folder contains a standalone Python desktop application that
visually demonstrates the BFS pathfinding engine on a sample office floor.

### What it does

| Action | Result |
|--------|--------|
| Click any room | Places your position pin |
| **Run BFS** | Highlights the shortest safe path to the nearest exit in orange |
| **Add Incident** | Marks a room as blocked (red) and forces BFS to reroute |
| **Reset** | Clears all state |

### Algorithms implemented

**BFS — Breadth-First Search** (`algorithms.py`)
- Finds the **shortest path** (fewest hops) from the user's position to the nearest available exit
- Time complexity: **O(N + E)**  ·  Space complexity: **O(N + E)**
- Used for primary evacuation routing

**DFS — Depth-First Search** (`algorithms.py`)
- Finds **all possible paths** from the user's position to any exit
- Time complexity: **O(N + E)**  ·  Space complexity: **O(N)**
- Used for route analysis and fallback discovery

### Requirements

```
Python 3.8+
tkinter (included in standard Python on Windows/macOS)
```

### Run the visualiser

```bash
cd algorithm
python main.py
```

---

## Database

### What is implemented

| Chapter | Content |
|---------|---------|
| DDL | 15 tables with PKs, FKs, CHECK constraints |
| DML | 40+ rows inserted per table |
| DQL | 33 queries — σ Selection, π Projection, ⋈ Join, ∪ Union, ∩ Intersection, − Difference |
| Views | 7 views for dashboards and reporting |
| Indexes | 17 indexes for query optimisation |
| Triggers | 9 triggers enforcing business rules |
| Stored Procedures | 12 reusable procedures |
| DCL | 3-tier access control |

### Access levels

| User | Role | Permissions |
|------|------|-------------|
| `evac_admin`    | Building manager / safety officer | Full SELECT, INSERT, UPDATE, DELETE + EXECUTE |
| `evac_occupant` | Building occupant (mobile app)    | Read layout data, insert own location events |
| `evac_readonly` | External auditor / reporting      | SELECT only on all tables and views |

### Key business rules enforced

- Beacon UUIDs are globally unique across all buildings
- A `USER_LOCATION` record can only reference a beacon that belongs to the correct floor
- Non-emergency exits are automatically blocked when an active incident is registered
- Deletion of `INCIDENT`, `EVACUATION_ROUTE`, and `USER_LOCATION` records is permanently blocked — they are immutable audit logs
- Incident `end_time` is automatically set when status changes to `resolved`

---

## How to Run

### Database (SQL Server)

1. Open **SQL Server Management Studio (SSMS)**
2. Run the scripts inside `database/` **in order**,
3. Each file starts with `USE SmartEvacuationDB; GO` — no manual setup needed

### Algorithm visualiser (Python)

```bash
# Clone the repository
git clone https://github.com/lloocie/FLOCK.git
cd FLOCK/algorithm

# Run (no extra packages needed)
python main.py
```

---

## Authors

| Name | Role |
|------|------|
| Lusine Stepanyan    | Database design, physical implementation, algorithm |
| Elen Yeghiazaryan   | Conceptual & logical design, normalisation |
| Melanya Martirosyan | Physical implementation, MVP hardware design, UML diagrams |

**Supervisor:** Varazdat Avetisyan, PhD
**French University in Armenia** · April 2026
