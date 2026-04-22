BUILDING_NAME = "Corporate Office Tower - Floor 3 (Simplified)"

# 15 nodes total: 11 interior rooms + 4 exits
NODES = {
    0:   ("Main Lobby",      450, 130),
    1:   ("East Corridor",   700, 130),
    2:   ("West Corridor",   300, 130),
    3:   ("Office 102",      600, 230),
    4:   ("Office 101",      400, 230),
    5:   ("Conf Room B",     700, 330),
    6:   ("Conf Room A",     300, 330),
    7:   ("Kitchen",         500, 330),
    8:   ("Spine Hall",      500, 530),
    9:   ("Office 202",      700, 530),
    10:  ("Office 201",      300, 530),
    11:  ("Stairs West",     200, 630),
    12:  ("Stairs East",     800, 630),
    13:  ("EXIT North",      500, 70),
    14:  ("EXIT West",       140, 730),
    15:  ("EXIT East",       860, 730),
    16:  ("EXIT South",      500, 730),
}

# Edges with correct Euclidean distances (10 pixels = 1 meter)
EDGES_WEIGHTED = [
    (0, 1, 25.0),   # Main Lobby – East Corridor
    (0, 2, 15.0),   # Main Lobby – West Corridor
    (0, 7, 20.6),   # Main Lobby – Kitchen
    (1, 3, 14.1),   # East Corridor – Office 102
    (1, 5, 20.0),   # East Corridor – Conf Room B
    (2, 4, 14.1),   # West Corridor – Office 101
    (2, 6, 20.0),   # West Corridor – Conf Room A
    (3, 5, 14.1),   # Office 102 – Conf Room B
    (4, 6, 14.1),   # Office 101 – Conf Room A
    (5, 8, 20.0),   # Conf Room B – Spine Hall
    (6, 8, 20.0),   # Conf Room A – Spine Hall
    (7, 8, 20.0),   # Kitchen – Spine Hall
    (8, 9, 20.0),   # Spine Hall – Office 202
    (8, 10, 20.0),  # Spine Hall – Office 201
    (9, 12, 14.1),  # Office 202 – Stairs East
    (10, 11, 14.1), # Office 201 – Stairs West
    (11, 14, 11.7), # Stairs West – EXIT West
    (12, 15, 11.7), # Stairs East – EXIT East
    (8, 16, 20.0),  # Spine Hall – EXIT South
    (0, 13, 7.8),   # Main Lobby – EXIT North
]

EDGES = [(u, v) for (u, v, _) in EDGES_WEIGHTED]
EXITS = {13, 14, 15, 16}