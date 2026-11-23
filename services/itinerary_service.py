import math


def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two geographic coordinates in km."""
    earth_radius = 6371

    lat1, lon1, lat2, lon2 = map(
        math.radians, [lat1, lon1, lat2, lon2]
    )

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )

    return 2 * earth_radius * math.asin(math.sqrt(a))


def plan_itinerary(attractions, days, max_places_per_day=3):
    """
    Create a day-by-day itinerary by grouping nearby attractions.
    Each attraction should contain name, lat and lon.
    """

    if days < 1:
        raise ValueError("Days must be at least 1.")

    if max_places_per_day < 1:
        raise ValueError("Maximum places per day must be at least 1.")

    valid_places = [
        place for place in attractions
        if place.get("name")
        and place.get("lat") is not None
        and place.get("lon") is not None
    ]

    if not valid_places:
        return []

    # Remove duplicate attraction names.
    unique_places = []
    seen = set()

    for place in valid_places:
        name = place["name"].strip().lower()

        if name not in seen:
            unique_places.append(place)
            seen.add(name)

    # Start with the first available attraction.
    remaining = unique_places.copy()
    itinerary = []

    for day in range(1, days + 1):
        if not remaining:
            break

        day_places = [remaining.pop(0)]

        while remaining and len(day_places) < max_places_per_day:
            last_place = day_places[-1]

            nearest_place = min(
                remaining,
                key=lambda place: calculate_distance(
                    float(last_place["lat"]),
                    float(last_place["lon"]),
                    float(place["lat"]),
                    float(place["lon"])
                )
            )

            day_places.append(nearest_place)
            remaining.remove(nearest_place)

        itinerary.append({
            "day": day,
            "places": day_places
        })

    return itinerary
