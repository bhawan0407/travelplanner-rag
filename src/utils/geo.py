"""Geospatial utility functions."""

from typing import Tuple
import math
from src.models import Coordinates


def haversine_distance(coord1: Coordinates, coord2: Coordinates) -> float:
    """Calculate distance between two coordinates using Haversine formula.
    
    Args:
        coord1: First coordinate.
        coord2: Second coordinate.
        
    Returns:
        Distance in kilometers.
    """
    R = 6371  # Earth's radius in kilometers

    lat1, lon1 = math.radians(coord1.latitude), math.radians(coord1.longitude)
    lat2, lon2 = math.radians(coord2.latitude), math.radians(coord2.longitude)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))

    return R * c


def is_within_radius(
    center: Coordinates,
    point: Coordinates,
    radius_km: float,
) -> bool:
    """Check if a point is within a certain radius from center.
    
    Args:
        center: Center coordinates.
        point: Point to check.
        radius_km: Radius in kilometers.
        
    Returns:
        True if point is within radius.
    """
    distance = haversine_distance(center, point)
    return distance <= radius_km


def calculate_walking_time(distance_km: float, speed_kmh: float = 4.0) -> int:
    """Calculate walking time in minutes.
    
    Args:
        distance_km: Distance in kilometers.
        speed_kmh: Walking speed in km/h (default: 4 km/h).
        
    Returns:
        Walking time in minutes.
    """
    hours = distance_km / speed_kmh
    return int(hours * 60)


def get_bounding_box(
    center: Coordinates,
    radius_km: float,
) -> Tuple[float, float, float, float]:
    """Get bounding box (min_lat, max_lat, min_lon, max_lon) around a center point.
    
    Args:
        center: Center coordinates.
        radius_km: Radius in kilometers.
        
    Returns:
        Tuple of (min_lat, max_lat, min_lon, max_lon).
    """
    # Approximate degrees per km (varies by latitude)
    lat_km = 111.32  # 1 degree latitude ≈ 111.32 km
    lon_km = 111.32 * math.cos(math.radians(center.latitude))  # varies by latitude

    lat_delta = radius_km / lat_km
    lon_delta = radius_km / lon_km

    return (
        center.latitude - lat_delta,   # min_lat
        center.latitude + lat_delta,   # max_lat
        center.longitude - lon_delta,  # min_lon
        center.longitude + lon_delta,  # max_lon
    )


def cluster_locations(
    coordinates: list[Coordinates],
    max_distance_km: float = 2.0,
) -> list[list[int]]:
    """Cluster coordinates by proximity using simple distance-based grouping.
    
    Args:
        coordinates: List of coordinates to cluster.
        max_distance_km: Maximum distance within a cluster.
        
    Returns:
        List of clusters, each cluster is a list of indices.
    """
    n = len(coordinates)
    if n == 0:
        return []
    
    visited = [False] * n
    clusters = []
    
    for i in range(n):
        if visited[i]:
            continue
            
        cluster = [i]
        visited[i] = True
        
        # Find all points within max_distance from this point
        for j in range(i + 1, n):
            if not visited[j]:
                if haversine_distance(coordinates[i], coordinates[j]) <= max_distance_km:
                    cluster.append(j)
                    visited[j] = True
        
        clusters.append(cluster)
    
    return clusters