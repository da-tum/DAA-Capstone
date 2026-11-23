import unittest

from src.knapsack import knapsack_pack
from src.models import DeliveryGraph, Parcel
from src.routing import dijkstra, nearest_neighbor_tsp, reconstruct_path
from src.sorting import merge_sort_parcels


class TestMiniCourierPlanner(unittest.TestCase):
    def setUp(self) -> None:
        self.parcels = [
            Parcel("P1", "A", weight=3, value=30, deadline=3, priority=2),
            Parcel("P2", "B", weight=4, value=50, deadline=1, priority=5),
            Parcel("P3", "C", weight=2, value=25, deadline=1, priority=3),
            Parcel("P4", "A", weight=5, value=60, deadline=2, priority=4),
        ]
        self.graph = DeliveryGraph()
        self.graph.add_edge("Depot", "A", 4)
        self.graph.add_edge("Depot", "B", 8)
        self.graph.add_edge("A", "B", 2)
        self.graph.add_edge("B", "C", 3)
        self.graph.add_edge("A", "C", 7)

    def test_merge_sort_orders_by_deadline_then_priority(self) -> None:
        sorted_p = merge_sort_parcels(self.parcels)
        self.assertEqual([p.parcel_id for p in sorted_p], ["P2", "P3", "P4", "P1"])

    def test_knapsack_selects_optimal_value(self) -> None:
        max_val, total_wt, selected, _ = knapsack_pack(self.parcels, capacity=7)
        self.assertEqual(max_val, 85)  # P2 (50, wt=4) + P3 (25, wt=2) = 75 OR P3(25,2)+P4(60,5)=85
        self.assertEqual(total_wt, 7)
        self.assertEqual({p.parcel_id for p in selected}, {"P3", "P4"})

    def test_knapsack_zero_capacity(self) -> None:
        max_val, total_wt, selected, _ = knapsack_pack(self.parcels, capacity=0)
        self.assertEqual((max_val, total_wt, selected), (0, 0, []))

    def test_dijkstra_shortest_path(self) -> None:
        dists, parents = dijkstra(self.graph, "Depot")
        self.assertEqual(dists["B"], 6)  # Depot -> A (4) -> B (2)
        self.assertEqual(reconstruct_path(parents, "B"), ["Depot", "A", "B"])

    def test_nearest_neighbor_tsp_returns_to_depot(self) -> None:
        route, total_dist, legs = nearest_neighbor_tsp(self.graph, "Depot", ["B", "C"])
        self.assertEqual(route[0], "Depot")
        self.assertEqual(route[-1], "Depot")
        self.assertEqual(set(route), {"Depot", "B", "C"})
        self.assertEqual(total_dist, 18)  # Depot->B(6) + B->C(3) + C->Depot(9)
        self.assertEqual(len(legs), 3)

    def test_unreachable_stop_raises(self) -> None:
        self.graph.add_node("Isolated")
        with self.assertRaises(ValueError):
            nearest_neighbor_tsp(self.graph, "Depot", ["Isolated"])


if __name__ == "__main__":
    unittest.main()

