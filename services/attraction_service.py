import requests
import time
from math import radians, sin, cos, sqrt, atan2


OVERPASS_SERVERS = [
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass-api.de/api/interpreter"
]


def calculate_distance(lat1, lon1, lat2, lon2):
    earth_radius = 6371

    lat1, lon1, lat2, lon2 = map(
        radians, [lat1, lon1, lat2, lon2]
    )

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    )

    return 2 * earth_radius * atan2(sqrt(a), sqrt(1 - a))


def find_attractions(latitude, longitude, radius=5000, max_results=150):

    query = f"""
    [out:json][timeout:25];
    (
      nwr(around:{radius},{latitude},{longitude})["tourism"~"attraction|museum|gallery|zoo|viewpoint|theme_park|artwork"];
      nwr(around:{radius},{latitude},{longitude})["historic"~"castle|monument|archaeological_site|ruins|fort|manor|city_gate"];
      nwr(around:{radius},{latitude},{longitude})["leisure"~"park|garden"];
    );
    out center tags;
    """

    headers = {
        "User-Agent": "TravelTourismIntelligence/1.0 (educational project)",
        "Accept": "application/json"
    }

    data = None
    last_error = None

    for server in OVERPASS_SERVERS:
        try:
            print(f"Trying attraction data server: {server}")

            response = requests.post(
                server,
                data={"data": query},
                headers=headers,
                timeout=35
            )

            response.raise_for_status()
            data = response.json()

            print("Attraction data server connected successfully.")
            break

        except (requests.RequestException, ValueError) as error:
            last_error = error
            print(f"Server unavailable: {error}")
            time.sleep(1)

    if data is None:
        raise RuntimeError(
            f"All attraction servers failed. Last error: {last_error}"
        )

    attractions = []
    seen = set()

    for element in data.get("elements", []):
        tags = element.get("tags", {})
        name = tags.get("name")

        if not name:
            continue

        if "lat" in element and "lon" in element:
            lat = element["lat"]
            lon = element["lon"]
        elif "center" in element:
            lat = element["center"].get("lat")
            lon = element["center"].get("lon")
        else:
            continue

        if lat is None or lon is None:
            continue

        tourism = tags.get("tourism")
        historic = tags.get("historic")
        leisure = tags.get("leisure")

        if tourism:
            category = tourism
            priority = 1 if tourism in ["attraction", "museum", "zoo", "theme_park"] else 2
        elif historic:
            category = historic
            priority = 3
        elif leisure:
            category = leisure
            priority = 4
        else:
            continue

        unique_key = (
            name.strip().lower(),
            round(float(lat), 5),
            round(float(lon), 5)
        )

        if unique_key in seen:
            continue

        seen.add(unique_key)

        address_parts = [
            tags.get("addr:housenumber"),
            tags.get("addr:street"),
            tags.get("addr:city")
        ]

        attractions.append({
            "name": name,
            "category": category,
            "lat": float(lat),
            "lon": float(lon),
            "distance_km": round(
                calculate_distance(latitude, longitude, lat, lon), 2
            ),
            "website": tags.get("website"),
            "description": tags.get("description"),
            "address": ", ".join(
                str(part) for part in address_parts if part
            ),
            "priority": priority
        })

    attractions.sort(
        key=lambda place: (place["priority"], place["distance_km"])
    )

    return attractions[:max_results]

