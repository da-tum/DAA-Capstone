from typing import List, Tuple
from src.models import Parcel


def knapsack_pack(
    parcels: List[Parcel], capacity: int
) -> Tuple[int, int, List[Parcel], List[List[int]]]:
    """
    Solves the 0/1 Knapsack problem using bottom-up Dynamic Programming
    to select the highest-value subset of parcels within vehicle capacity.

    Time Complexity:  O(n * capacity)
    Space Complexity: O(n * capacity)

    Returns:
        (max_value, total_weight, selected_parcels, dp_table)
    """
    n = len(parcels)
    if n == 0 or capacity <= 0:
        return 0, 0, [], [[0]]

    # dp[i][w] = max value achievable using first i parcels with capacity w
    dp: List[List[int]] = [[0] * (capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        parcel = parcels[i - 1]
        for w in range(capacity + 1):
            # Option 1: Exclude current parcel
            dp[i][w] = dp[i - 1][w]
            # Option 2: Include current parcel if it fits
            if parcel.weight <= w:
                include_val = parcel.value + dp[i - 1][w - parcel.weight]
                if include_val > dp[i][w]:
                    dp[i][w] = include_val

    # Backtrack through the DP table to find which parcels were selected
    selected: List[Parcel] = []
    w = capacity
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            parcel = parcels[i - 1]
            selected.append(parcel)
            w -= parcel.weight

    selected.reverse()
    total_weight = sum(p.weight for p in selected)
    return dp[n][capacity], total_weight, selected, dp

