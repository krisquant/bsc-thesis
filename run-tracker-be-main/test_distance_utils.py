"""
Tests for distance calculation utilities
"""

from app.utils.distance_utils import (
    calculate_distance_meters,
    extract_route_endpoints,
    points_within_radius,
)


def test_haversine_known_distance():
    """Test Haversine formula with known coordinates"""
    # New York City coordinates (Times Square to Central Park, approximately 1.4km)
    lat1, lon1 = 40.758896, -73.985130  # Times Square
    lat2, lon2 = 40.785091, -73.968285  # Central Park

    distance = calculate_distance_meters(lat1, lon1, lat2, lon2)
    print(f"NYC Test: {distance:.2f} meters (expected ~3000-3500m)")
    assert 2500 < distance < 4000, f"Expected ~3000-3500m, got {distance:.2f}m"


def test_points_within_radius_close():
    """Test points within 100m radius"""
    # Two points very close together (approx 50m apart)
    point1 = {"latitude": 40.758896, "longitude": -73.985130}
    point2 = {"latitude": 40.759350, "longitude": -73.985130}  # ~50m north

    assert points_within_radius(point1, point2, radius_meters=100) is True
    print("✓ Close points correctly identified as within 100m")


def test_points_outside_radius():
    """Test points outside 100m radius"""
    # Two points far apart
    point1 = {"latitude": 40.758896, "longitude": -73.985130}  # Times Square
    point2 = {"latitude": 40.785091, "longitude": -73.968285}  # Central Park

    assert points_within_radius(point1, point2, radius_meters=100) is False
    print("✓ Distant points correctly identified as outside 100m")


def test_extract_route_endpoints():
    """Test route endpoint extraction"""
    route = [
        {"latitude": 40.758896, "longitude": -73.985130},
        {"latitude": 40.759000, "longitude": -73.985000},
        {"latitude": 40.785091, "longitude": -73.968285},
    ]

    start, end = extract_route_endpoints(route)
    assert start == route[0]
    assert end == route[-1]
    print("✓ Route endpoints extracted correctly")


def test_extract_empty_route():
    """Test empty route handling"""
    start, end = extract_route_endpoints([])
    assert start is None
    assert end is None
    print("✓ Empty route handled correctly")


def test_points_with_missing_data():
    """Test handling of invalid coordinate data"""
    point1 = {"latitude": 40.758896, "longitude": -73.985130}
    point2 = {"latitude": None, "longitude": -73.985130}

    assert points_within_radius(point1, point2, radius_meters=100) is False
    print("✓ Invalid coordinates handled correctly")


if __name__ == "__main__":
    print("Testing distance calculation utilities...\n")

    test_haversine_known_distance()
    test_points_within_radius_close()
    test_points_outside_radius()
    test_extract_route_endpoints()
    test_extract_empty_route()
    test_points_with_missing_data()

    print("\n✅ All tests passed!")
