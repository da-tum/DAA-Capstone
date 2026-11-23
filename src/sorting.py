from typing import List
from src.models import Parcel


def _parcel_key(parcel: Parcel) -> tuple:
    """
    Sort key for parcel prioritization:
    1. Earlier deadline first (ascending)
    2. Higher priority first (descending)
    3. Higher value first (descending)
    """
    return (parcel.deadline, -parcel.priority, -parcel.value)


def merge_sort_parcels(parcels: List[Parcel]) -> List[Parcel]:
    """
    Sorts parcels using Merge Sort.
    Time Complexity:  O(n log n)
    Space Complexity: O(n)
    """
    if len(parcels) <= 1:
        return list(parcels)

    mid = len(parcels) // 2
    left = merge_sort_parcels(parcels[:mid])
    right = merge_sort_parcels(parcels[mid:])
    return _merge(left, right)


def _merge(left: List[Parcel], right: List[Parcel]) -> List[Parcel]:
    merged: List[Parcel] = []
    i = 0
    j = 0

    while i < len(left) and j < len(right):
        if _parcel_key(left[i]) <= _parcel_key(right[j]):
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1

    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged

