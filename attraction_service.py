
import requests
import math

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

HEADERS = {
    "User-Agent": "TravelTourismIntelligence/1.0"
}


def calculate_distance(lat1, lon1, lat2, lon2):

    radius = 6371

    lat1, lon1, lat2, lon2 = map(
        math.radians, [lat1, lon1, lat2, lon2]
    )

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    return 2 * radius * math.asin(math.sqrt(a))


def find_attractions(latitude, longitude, radius=3000):

    query = f"""
    [out:json][timeout:15];
    (
      node(around:{radius},{latitude},{longitude})["tourism"~"attraction|museum|gallery|viewpoint"];
      way(around:{radius},{latitude},{longitude})["tourism"~"attraction|museum|gallery|viewpoint"];
      relation(around:{radius},{latitude},{longitude})["tourism"~"attraction|museum|gallery|viewpoint"];
      nwr(around:{radius},{latitude},{longitude})["historic"];
      nwr(around:{radius},{latitude},{longitude})["leisure"="park"];
    );
    out center tags;
    """

    servers = [
        "https://overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter"
    ]

    for server in servers:
        try:
            response = requests.post(
                server,
                data={"data": query},
                headers=HEADERS,
                timeout=60
            )

            response.raise_for_status()
            elements = response.json().get("elements", [])

            attractions = []
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

                distance = calculate_distance(
                    latitude, longitude, lat, lon
                )

                attractions.append({
                    "name": name,
                    "category": tags.get(
                        "tourism",
                        tags.get("historic", tags.get("leisure", "Attraction"))
                    ),
                    "latitude": lat,
                    "longitude": lon,
                    "distance_km": round(distance, 2),
                    "website": tags.get("website", ""),
                    "description": tags.get("description", ""),
                    "address": tags.get("addr:full", "")
                })

            attractions.sort(key=lambda x: x["distance_km"])
            return attractions

        except requests.exceptions.RequestException:
            continue

    raise RuntimeError(
        "All OpenStreetMap attraction servers are unavailable. Please try again later."
    )