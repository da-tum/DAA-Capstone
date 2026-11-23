import json
import os
import random
import time
from typing import Dict, List

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.knapsack import knapsack_pack
from src.models import DeliveryGraph, Parcel
from src.routing import dijkstra, nearest_neighbor_tsp
from src.sorting import merge_sort_parcels


def generate_synthetic_case(num_parcels: int, num_nodes: int, seed: int = 42):
    rng = random.Random(seed + num_parcels)
    graph = DeliveryGraph()
    nodes = ["Depot"] + [f"Hub{i}" for i in range(1, num_nodes)]

    # Build a connected graph with extra random cross-edges
    for i in range(1, num_nodes):
        graph.add_edge(nodes[i - 1], nodes[i], rng.randint(2, 15))
    for _ in range(num_nodes * 2):
        u, v = rng.sample(nodes, 2)
        graph.add_edge(u, v, rng.randint(2, 20))

    parcels: List[Parcel] = []
    for i in range(num_parcels):
        parcels.append(
            Parcel(
                parcel_id=f"P{i:04d}",
                destination=rng.choice(nodes[1:]),
                weight=rng.randint(1, 10),
                value=rng.randint(10, 100),
                deadline=rng.randint(1, 12),
                priority=rng.randint(1, 5),
            )
        )
    capacity = max(20, num_parcels * 2)
    return "Depot", capacity, graph, parcels


def run_benchmarks() -> List[Dict]:
    sizes = [
        (10, 8),
        (50, 15),
        (100, 25),
        (250, 40),
        (500, 60),
    ]
    results: List[Dict] = []

    for num_parcels, num_nodes in sizes:
        depot, capacity, graph, parcels = generate_synthetic_case(num_parcels, num_nodes)

        t0 = time.perf_counter()
        sorted_parcels = merge_sort_parcels(parcels)
        sort_ms = (time.perf_counter() - t0) * 1000

        t0 = time.perf_counter()
        _, _, selected, _ = knapsack_pack(sorted_parcels, capacity)
        dp_ms = (time.perf_counter() - t0) * 1000

        t0 = time.perf_counter()
        dijkstra(graph, depot)
        dijkstra_ms = (time.perf_counter() - t0) * 1000

        stops = [p.destination for p in selected[: min(15, len(selected))]]
        t0 = time.perf_counter()
        nearest_neighbor_tsp(graph, depot, stops)
        tsp_ms = (time.perf_counter() - t0) * 1000

        results.append(
            {
                "num_parcels": num_parcels,
                "num_nodes": num_nodes,
                "capacity": capacity,
                "merge_sort_ms": round(sort_ms, 4),
                "knapsack_dp_ms": round(dp_ms, 4),
                "dijkstra_ms": round(dijkstra_ms, 4),
                "tsp_nn_ms": round(tsp_ms, 4),
            }
        )

    return results


def save_chart(results: List[Dict], out_path: str) -> None:
    x = [r["num_parcels"] for r in results]
    plt.figure(figsize=(8, 4.8))
    plt.plot(x, [r["merge_sort_ms"] for r in results], marker="o", label="Merge Sort O(n log n)")
    plt.plot(x, [r["knapsack_dp_ms"] for r in results], marker="s", label="0/1 Knapsack DP O(n * W)")
    plt.plot(x, [r["dijkstra_ms"] for r in results], marker="^", label="Dijkstra O((V + E) log V)")
    plt.plot(x, [r["tsp_nn_ms"] for r in results], marker="d", label="Nearest-Neighbor TSP")
    plt.title("Mini-Courier Planner — Runtime Scaling Across Dataset Sizes")
    plt.xlabel("Number of Parcels (n)")
    plt.ylabel("Execution Time (ms)")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs")
    os.makedirs(out_dir, exist_ok=True)

    results = run_benchmarks()
    json_path = os.path.join(out_dir, "benchmark_results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    chart_path = os.path.join(out_dir, "runtime_chart.png")
    save_chart(results, chart_path)

    print("Benchmark Summary:")
    for row in results:
        print(row)
    print(f"Saved chart to: {chart_path}")

