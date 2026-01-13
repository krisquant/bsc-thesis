"""
Utilities for calculating distances between GPS coordinates.
"""

import math
from typing import Any, Dict, Optional


def calculate_distance_meters(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """
    Calculate the distance between two GPS coordinates using the Haversine formula.

    Args:
        lat1: Latitude of first point in degrees
        lon1: Longitude of first point in degrees
        lat2: Latitude of second point in degrees
        lon2: Longitude of second point in degrees

    Returns:
        Distance in meters
    """
    # Earth's radius in meters
    R = 6371000

    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    # Haversine formula
    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance


def points_within_radius(
    point1: Dict[str, Any], point2: Dict[str, Any], radius_meters: float = 100
) -> bool:
    """
    Check if two GPS coordinate points are within a given radius.

    Args:
        point1: Dictionary containing 'latitude' and 'longitude' keys
        point2: Dictionary containing 'latitude' and 'longitude' keys
        radius_meters: Maximum distance in meters (default: 100)

    Returns:
        True if points are within the radius, False otherwise
    """
    try:
        lat1 = point1.get("latitude")
        lon1 = point1.get("longitude")
        lat2 = point2.get("latitude")
        lon2 = point2.get("longitude")

        if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
            return False

        distance = calculate_distance_meters(lat1, lon1, lat2, lon2)
        return distance <= radius_meters
    except (TypeError, ValueError):
        return False


def extract_route_endpoints(
    route: Optional[list],
) -> tuple[Optional[Dict], Optional[Dict]]:
    """
    Extract the first and last points from a route.

    Args:
        route: List of GPS coordinate dictionaries

    Returns:
        Tuple of (first_point, last_point), either can be None if route is invalid
    """
    if not route or len(route) == 0:
        return None, None

    return route[0], route[-1]
