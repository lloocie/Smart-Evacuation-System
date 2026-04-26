import heapq

# ─── Graph Construction ───────────────────────────────────────────────────────

def build_weighted_graph(edges_weighted):
    adj = {}
    weights = {}

    for u, v, w in edges_weighted:
        if u not in adj:
            adj[u] = set()
        if v not in adj:
            adj[v] = set()

        adj[u].add(v)
        adj[v].add(u)

        key = (min(u, v), max(u, v))
        weights[key] = w

    return adj, weights

# ─── Pathfinding ──────────────────────────────────────────────────────────────

def dijkstra_shortest_path(start, graph, edge_weights, exits, blocked):

    if start in blocked:
        return None

    pq = [(0.0, start)]
    dist = {start: 0.0}
    parent = {start: None}
    visited = set()

    while pq:
        d, u = heapq.heappop(pq)
        if u in visited:
            continue
        visited.add(u)

        if u in exits:
            path = []
            node = u
            while node is not None:
                path.append(node)
                node = parent[node]
            return list(reversed(path))

        for v in graph.get(u, set()):
            if v in blocked or v in visited:
                continue
            key = (min(u, v), max(u, v))
            w = edge_weights.get(key, 1.0)
            nd = d + w
            if v not in dist or nd < dist[v]:
                dist[v] = nd
                parent[v] = u
                heapq.heappush(pq, (nd, v))

    return None