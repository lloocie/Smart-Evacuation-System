
from collections import deque

def build_graph(edges):
    graph = {}
    for a, b in edges:
        graph.setdefault(a, set()).add(b)
        graph.setdefault(b, set()).add(a)
    return graph


# BFS — shortest path to nearest exit
# Time O(N+E)  Memory O(N+E)
def bfs(start, graph, exits):
    visited = set()
    parent  = {start: None}
    q       = deque([start])

    while q:
        curr = q.popleft()
        if curr in visited:
            continue
        visited.add(curr)

        if curr in exits:
            path, node = [], curr
            while node is not None:
                path.append(node)
                node = parent[node]
            return list(reversed(path))

        for nb in graph.get(curr, set()):
            if nb not in visited:
                parent.setdefault(nb, curr)
                q.append(nb)

    return None


# DFS — find all paths to any exit
# Time O(N+E)  Memory O(N)
def _dfs(node, graph, exits, visited, parent, paths):
    if node in visited:
        return
    visited.add(node)

    if node in exits:
        path, cur = [], node
        while cur is not None:
            path.append(cur)
            cur = parent[cur]
        paths.append(list(reversed(path)))
        return

    for nb in graph.get(node, set()):
        if nb not in visited:
            parent[nb] = node
            _dfs(nb, graph, exits, visited, parent, paths)


def dfs(start, graph, exits):
    paths = []
    _dfs(start, graph, exits, set(), {start: None}, paths)
    return paths