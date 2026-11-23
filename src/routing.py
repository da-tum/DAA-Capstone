import heapq
from typing import Dict, List, Optional, Tuple
from src.models import DeliveryGraph


def dijkstra(
    graph: DeliveryGraph, source: str
) -> Tuple[Dict[str, float], Dict[str, Optional[str]]]:
    """
    Computes shortest paths from `source` to all reachable nodes using Dijkstra's Algorithm.
    Time Complexity:  O((V + E) log V)
    Space Complexity: O(V)
    """
    distances: Dict[str, float] = {node: float("inf") for node in graph.nodes()}
    parents: Dict[str, Optional[str]] = {node: None for node in graph.nodes()}

    if source not in distances:
        return distances, parents

    distances[source] = 0
    min_heap: List[Tuple[float, str]] = [(0, source)]

    while min_heap:
        curr_dist, u = heapq.heappop(min_heap)
        if curr_dist > distances[u]:
            continue

        for neighbor, weight in graph.adj[u]:
            new_dist = curr_dist + weight
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                parents[neighbor] = u
                heapq.heappush(min_heap, (new_dist, neighbor))

    return distances, parents


def reconstruct_path(parents: Dict[str, Optional[str]], target: str) -> List[str]:
    """Reconstructs the shortest path from source to `target` using the parent map."""
    path: List[str] = []
    curr: Optional[str] = target
    while curr is not None:
        path.append(curr)
        curr = parents.get(curr)
    path.reverse()
    return path


def nearest_neighbor_tsp(
    graph: DeliveryGraph, depot: str, stops: List[str]
) -> Tuple[List[str], float, List[Tuple[str, str, float, List[str]]]]:
    """
    Approximates the shortest delivery tour starting and ending at `depot`
    and visiting all `stops` using the Nearest-Neighbor TSP heuristic
    backed by Dijkstra shortest-path distances.

    Time Complexity:  O(k * (V + E) log V + k^2) where k = len(stops)
    Space Complexity: O(k * V)
    """
    unique_stops = list(dict.fromkeys(s for s in stops if s != depot))
    if not unique_stops:
        return [depot], 0, []

    # Precompute shortest paths from depot and every stop
    all_points = [depot] + unique_stops
    dist_cache: Dict[str, Dict[str, float]] = {}
    parent_cache: Dict[str, Dict[str, Optional[str]]] = {}

    for point in all_points:
        dists, parents = dijkstra(graph, point)
        dist_cache[point] = dists
        parent_cache[point] = parents

    unvisited = set(unique_stops)
    current = depot
    route = [depot]
    total_distance = 0.0
    legs: List[Tuple[str, str, float, List[str]]] = []

    while unvisited:
        next_stop = min(unvisited, key=lambda s: dist_cache[current][s])
        leg_dist = dist_cache[current][next_stop]
        if leg_dist == float("inf"):
            raise ValueError(f"Stop '{next_stop}' is unreachable from '{current}'")

        leg_path = reconstruct_path(parent_cache[current], next_stop)
        legs.append((current, next_stop, leg_dist, leg_path))
        total_distance += leg_dist
        route.append(next_stop)
        unvisited.remove(next_stop)
        current = next_stop

    # Return to depot
    return_dist = dist_cache[current][depot]
    if return_dist == float("inf"):
        raise ValueError(f"Depot '{depot}' is unreachable from '{current}'")

    return_path = reconstruct_path(parent_cache[current], depot)
    legs.append((current, depot, return_dist, return_path))
    total_distance += return_dist
    route.append(depot)

    return route, total_distance, legs

