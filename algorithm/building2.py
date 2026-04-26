import math
from collections import namedtuple

# ─── Data Structures ──────────────────────────────────────────────────────────

Room = namedtuple('Room', ['name', 'x', 'y', 'is_exit'])

# ─── Building Data ────────────────────────────────────────────────────────────

BUILDING_NAME = "City Medical Center - Floor 2"

NODES = {
    0:  Room("Main Atrium",        500, 150, False),
    1:  Room("East Hall",          780, 150, False),
    2:  Room("West Hall",          220, 150, False),
    3:  Room("Pharmacy",           650, 250, False),
    4:  Room("Lab A",              350, 250, False),
    5:  Room("X-Ray",              780, 350, False),
    6:  Room("MRI",                220, 350, False),
    7:  Room("Nurses Station",     500, 350, False),
    8:  Room("Central Corridor",   500, 520, False),
    9:  Room("Ward 202",           780, 520, False),
    10: Room("Ward 201",           220, 520, False),
    11: Room("Stairs West",        120, 620, False),
    12: Room("Stairs East",        880, 620, False),
    13: Room("EXIT North",         500,  50, True),
    14: Room("EXIT West",           80, 730, True),
    15: Room("EXIT East",          920, 730, True),
    16: Room("EXIT South",         500, 730, True),
    17: Room("Doctor's Office",    650, 420, False),
    18: Room("Consultation",       350, 420, False),
}

EDGES_RAW = [
    # Main Atrium connections
    (0, 1),   # Main Atrium – East Hall
    (0, 2),   # Main Atrium – West Hall
    (0, 7),   # Main Atrium – Nurses Station
    
    # East side
    (1, 3),   # East Hall – Pharmacy
    (1, 5),   # East Hall – X-Ray
    (3, 5),   # Pharmacy – X-Ray
    (5, 9),   # X-Ray – Ward 202
    (9, 12),  # Ward 202 – Stairs East
    
    # West side
    (2, 4),   # West Hall – Lab A
    (2, 6),   # West Hall – MRI
    (4, 6),   # Lab A – MRI
    (6, 10),  # MRI – Ward 201
    (10, 11), # Ward 201 – Stairs West
    
    # Middle vertical spine
    (7, 8),   # Nurses Station – Central Corridor
    (8, 16),  # Central Corridor – EXIT South
    
    # Additional offices off central spine
    (8, 17),  # Central Corridor – Doctor's Office
    (8, 18),  # Central Corridor – Consultation
    
    # Cross connections between east/west via spine
    (8, 9),   # Central Corridor – Ward 202
    (8, 10),  # Central Corridor – Ward 201
    
    # Stairs to exits
    (11, 14), # Stairs West – EXIT West
    (12, 15), # Stairs East – EXIT East
    
    # Direct north exit
    (0, 13),  # Main Atrium – EXIT North
]

# ─── Auto-computed from coordinates ───────────────────────────────────────────

def euclidean(n1, n2):
    x1, y1 = NODES[n1].x, NODES[n1].y
    x2, y2 = NODES[n2].x, NODES[n2].y
    return round(math.dist((x1, y1), (x2, y2)) / 10, 1)  # pixels → meters

EDGES_WEIGHTED = [(u, v, euclidean(u, v)) for u, v in EDGES_RAW]
EDGES          = [(u, v) for u, v in EDGES_RAW]
EXITS          = {nid for nid, room in NODES.items() if room.is_exit}