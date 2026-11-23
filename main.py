import json
import os
import sys
import time
from typing import Tuple

from src.knapsack import knapsack_pack
from src.models import DeliveryGraph, Parcel
from src.routing import dijkstra, nearest_neighbor_tsp, reconstruct_path
from src.sorting import merge_sort_parcels


def load_dataset(path: str) -> Tuple[str, int, DeliveryGraph, list]:
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    graph = DeliveryGraph()
    for u, v, dist in raw["edges"]:
        graph.add_edge(u, v, dist)

    parcels = [Parcel(**item) for item in raw["parcels"]]
    return raw["depot"], raw["vehicle_capacity"], graph, parcels


def run_planner(dataset_path: str) -> str:
    depot, capacity, graph, parcels = load_dataset(dataset_path)
    lines = []

    lines.append("=" * 64)
    lines.append("MINI-COURIER PLANNER — EXECUTION REPORT")
    lines.append(f"Dataset: {dataset_path} | Depot: {depot} | Capacity: {capacity} kg")
    lines.append("=" * 64)

    # Phase 2A: Merge Sort Prioritization
    t0 = time.perf_counter()
    sorted_parcels = merge_sort_parcels(parcels)
    t_sort = (time.perf_counter() - t0) * 1000

    lines.append(f"\n[Phase 2A] Prioritized Parcels via Merge Sort ({t_sort:.4f} ms):")
    lines.append(f"{'ID':<8}{'Dest':<12}{'Wt':>5}{'Val':>6}{'Deadline':>10}{'Priority':>10}")
    for p in sorted_parcels:
        lines.append(f"{p.parcel_id:<8}{p.destination:<12}{p.weight:>5}{p.value:>6}{p.deadline:>10}{p.priority:>10}")

    # Phase 2B: 0/1 Knapsack DP Packing
    t0 = time.perf_counter()
    max_val, total_wt, selected, dp_table = knapsack_pack(sorted_parcels, capacity)
    t_dp = (time.perf_counter() - t0) * 1000

    lines.append(f"\n[Phase 2B] 0/1 Knapsack Packing Plan ({t_dp:.4f} ms):")
    lines.append(f"Selected {len(selected)}/{len(sorted_parcels)} parcels | Total Weight: {total_wt}/{capacity} kg | Max Value: {max_val}")
    for p in selected:
        lines.append(f"  - {p.parcel_id} -> {p.destination} (wt={p.weight}, val={p.value}, deadline={p.deadline}h)")

    if len(sorted_parcels) <= 10 and capacity <= 20:
        lines.append("\nDP Table (rows = items 0..n, cols = capacity 0..W):")
        for idx, row in enumerate(dp_table):
            lines.append(f"  i={idx}: " + " ".join(f"{val:>3}" for val in row))

    # Phase 3A: Dijkstra Shortest Paths from Depot
    t0 = time.perf_counter()
    dists, parents = dijkstra(graph, depot)
    t_dijk = (time.perf_counter() - t0) * 1000

    lines.append(f"\n[Phase 3A] Dijkstra Shortest Paths from {depot} ({t_dijk:.4f} ms):")
    for node in sorted(dists.keys()):
        if node == depot:
            continue
        path = " -> ".join(reconstruct_path(parents, node))
        lines.append(f"  {depot} -> {node:<10} dist={dists[node]:>4}  path: {path}")

    # Phase 3B: Nearest-Neighbor TSP Delivery Route
    stops = [p.destination for p in selected]
    t0 = time.perf_counter()
    route, total_dist, legs = nearest_neighbor_tsp(graph, depot, stops)
    t_tsp = (time.perf_counter() - t0) * 1000

    lines.append(f"\n[Phase 3B] Nearest-Neighbor TSP Delivery Route ({t_tsp:.4f} ms):")
    lines.append("  Tour: " + " -> ".join(route))
    lines.append(f"  Total Route Distance: {total_dist:.0f} km")
    for src, dst, leg_dist, leg_path in legs:
        lines.append(f"    Leg {src} -> {dst} ({leg_dist:.0f} km): {' -> '.join(leg_path)}")

    return "\n".join(lines)


if __name__ == "__main__":
    default_data = os.path.join(os.path.dirname(__file__), "data", "small_dataset.json")
    dataset = sys.argv[1] if len(sys.argv) > 1 else default_data
    report = run_planner(dataset)
    print(report)

    out_dir = os.path.join(os.path.dirname(__file__), "outputs")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "sample_run_output.txt")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(report + "\n")

