from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class Parcel:
    """Represents a single courier parcel to be prioritized and packed."""

    parcel_id: str
    destination: str
    weight: int
    value: int
    deadline: int  # Delivery deadline in hours (smaller = more urgent)
    priority: int  # Priority level (1 = low, 5 = highest)


class DeliveryGraph:
    """Weighted undirected graph representing delivery hubs and road distances."""

    def __init__(self) -> None:
        self.adj: Dict[str, List[Tuple[str, int]]] = {}

    def add_node(self, node: str) -> None:
        if node not in self.adj:
            self.adj[node] = []

    def add_edge(self, u: str, v: str, distance: int) -> None:
        self.add_node(u)
        self.add_node(v)
        self.adj[u].append((v, distance))
        self.adj[v].append((u, distance))

    def nodes(self) -> List[str]:
        return list(self.adj.keys())

