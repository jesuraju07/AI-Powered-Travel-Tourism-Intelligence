
import requests
import math

OVERPASS_URL = "https://overpass-api.de/api/interpreter"


def calculate_distance(lat1, lon1, lat2, lon2):
    radius = 6371

    lat1, lon1, lat2, lon2 = map(
        math.radians, [lat1, lon1, lat2, lon2]
    )

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    return 2 * radius * math.asin(math.sqrt(a))


def find_food_places(latitude, longitude, radius=5000):

    query = f"""
    [out:json][timeout:40];
    (
      nwr(around:{radius},{latitude},{longitude})["amenity"="restaurant"];
      nwr(around:{radius},{latitude},{longitude})["amenity"="cafe"];
      nwr(around:{radius},{latitude},{longitude})["amenity"="fast_food"];
      nwr(around:{radius},{latitude},{longitude})["amenity"="food_court"];
      nwr(around:{radius},{latitude},{longitude})["amenity"="ice_cream"];
      nwr(around:{radius},{latitude},{longitude})["amenity"="pub"];
    );
    out center tags;
    """

    try:
        response = requests.post(
            OVERPASS_URL,
            data={"data": query},
            timeout=60
        )

        response.raise_for_status()

        elements = response.json().get("elements", [])

        food_places = []
        seen = set()

        for place in elements:

            tags = place.get("tags", {})
            name = tags.get("name")

            if not name:
                continue

            location = place.get("center", place)

            lat = location.get("lat")
            lon = location.get("lon")

            if lat is None or lon is None:
                continue

            key = (name.lower(), round(lat, 5), round(lon, 5))

            if key in seen:
                continue

            seen.add(key)

            food_places.append({
                "name": name,
                "category": tags.get("amenity", "Food"),
                "cuisine": tags.get("cuisine", "Not specified"),
                "latitude": lat,
                "longitude": lon,
                "distance_km": round(
                    calculate_distance(
                        latitude, longitude, lat, lon
                    ), 2
                ),
                "address": tags.get("addr:full", ""),
                "website": tags.get("website", ""),
                "phone": tags.get("phone", ""),
                "opening_hours": tags.get("opening_hours", ""),
                "price_level": tags.get("price_level", "Not available")
            })

        return sorted(
            food_places,
            key=lambda x: x["distance_km"]
        )

    except requests.exceptions.RequestException as error:
        raise RuntimeError(f"Food search failed: {error}")
