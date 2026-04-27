# 🚨 FLOCK — Smart Evacuation Navigation System

French University in Armenia · Faculty of Computer Science and Applied Mathematics

> A B2B safety platform that computes real-time personalised evacuation routes
> for large multi-story buildings using BLE beacon positioning and graph-based
> Dijkstra’s Algorithm pathfinding — all backed by a fully normalised SQL Server database.

---

## 📖 Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [System Architecture](#system-architecture)
- [Database Overview](#-database-overview)
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
- **Dijkstra’s Algorithm pathfinding** — computes the shortest safe route to the nearest open exit
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
│   ├── algorithms.py               ← Dijkstra’s Algorithm implementations
│   └── building.py                 ← Floor graph (nodes, edges, exits)
│   └── building2.py                ← Floor graph (nodes, edges, exits) (Other floor plan)
│   └── DataStructures_Report.pdf   ← Final Report with all requirements
│
├── 📁 presentation/                ← Full academic report (PDF)
│   └── Database_Project.pdf        ← Presentation (database)
│   └── Evacuation_Management_System_Report.pdf
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
Dijkstra’s Algorithm
      │
      │  shortest safe path → ordered RouteStep records
      ▼
Step-by-step guidance displayed to user
```

## 💾 Database Overview

The system includes a fully normalized relational database:

- **15 tables**
- Covers:
  - Buildings, floors, zones
  - Beacons and user locations
  - Incidents and evacuation routes

### Features
- Stored procedures for routing and logging
- Triggers for enforcing safety rules
- Indexes for performance optimization
- Role-based access control:
  - `evac_admin`
  - `evac_occupant`
  - `evac_readonly`
---

## Algorithm Demo

The `algorithm/` folder contains a standalone Python desktop application that
visually demonstrates the BFS pathfinding engine on a sample office floor.

### What it does

| Action | Result |
|--------|--------|
| Click any room | Places your position pin |
| **Find Route** | Highlights the shortest safe path to the nearest exit in orange |
| **Add Incident** | Marks a room as blocked (red) and forces BFS to reroute |
| **Reset** | Clears all state |


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
| Lusine Stepanyan    |Implementation of  algorithms.py (Details are in the report) //  Database design, physical implementation, algorithm |
| Elen Yeghiazaryan   |Implementation of building.py/building2.py (Details are in the report) // Conceptual & logical design, normalisation |
| Melanya Martirosyan |Implementation of main.py (Details are in the report) // Physical implementation, MVP design, UML diagrams |

**Supervisor:** Varazdat Avetisyan PhD, Ghevond Gevorgyan 

**French University in Armenia** · April 2026
