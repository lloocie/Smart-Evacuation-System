import math
from collections import namedtuple

# ─── Data Structures ──────────────────────────────────────────────────────────

Room = namedtuple('Room', ['name', 'x', 'y', 'is_exit'])

# ─── Building Data ────────────────────────────────────────────────────────────

BUILDING_NAME = "Corporate Office Tower - Floor 3"

NODES = {
    0:  Room("Main Lobby",      450, 130, False),
    1:  Room("East Corridor",   700, 130, False),
    2:  Room("West Corridor",   300, 130, False),
    3:  Room("Office 102",      600, 230, False),
    4:  Room("Office 101",      400, 230, False),
    5:  Room("Conf Room B",     700, 330, False),
    6:  Room("Conf Room A",     300, 330, False),
    7:  Room("Kitchen",         500, 330, False),
    8:  Room("Spine Hall",      500, 530, False),
    9:  Room("Office 202",      700, 530, False),
    10: Room("Office 201",      300, 530, False),
    11: Room("Stairs West",     200, 630, False),
    12: Room("Stairs East",     800, 630, False),
    13: Room("EXIT North",      500,  70, True),
    14: Room("EXIT West",       140, 730, True),
    15: Room("EXIT East",       860, 730, True),
    16: Room("EXIT South",      500, 730, True),
}

EDGES_RAW = [
    (0, 1),   # Main Lobby    – East Corridor
    (0, 2),   # Main Lobby    – West Corridor
    (0, 7),   # Main Lobby    – Kitchen
    (1, 3),   # East Corridor – Office 102
    (1, 5),   # East Corridor – Conf Room B
    (2, 4),   # West Corridor – Office 101
    (2, 6),   # West Corridor – Conf Room A
    (3, 5),   # Office 102    – Conf Room B
    (4, 6),   # Office 101    – Conf Room A
    (5, 8),   # Conf Room B   – Spine Hall
    (6, 8),   # Conf Room A   – Spine Hall
    (7, 8),   # Kitchen       – Spine Hall
    (8, 9),   # Spine Hall    – Office 202
    (8, 10),  # Spine Hall    – Office 201
    (9, 12),  # Office 202    – Stairs East
    (10, 11), # Office 201    – Stairs West
    (11, 14), # Stairs West   – EXIT West
    (12, 15), # Stairs East   – EXIT East
    (8, 16),  # Spine Hall    – EXIT South
    (0, 13),  # Main Lobby    – EXIT North
]

# ─── Auto-computed from coordinates ───────────────────────────────────────────

def euclidean(n1, n2):
    x1, y1 = NODES[n1].x, NODES[n1].y
    x2, y2 = NODES[n2].x, NODES[n2].y
    return round(math.dist((x1, y1), (x2, y2)) / 10, 1)  # pixels → meters

EDGES_WEIGHTED = [(u, v, euclidean(u, v)) for u, v in EDGES_RAW]
EDGES          = [(u, v) for u, v in EDGES_RAW]
EXITS          = {nid for nid, room in NODES.items() if room.is_exit}