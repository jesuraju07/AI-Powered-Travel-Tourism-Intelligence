import requests

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

HEADERS = {
    "User-Agent": "TravelTourismIntelligence/1.0 (educational project)"
}


def search_destinations(query, limit=5):

    if not query or not query.strip():
        return []

    params = {
        "q": query.strip(),
        "format": "jsonv2",
        "addressdetails": 1,
        "limit": limit
    }

    try:
        response = requests.get(
            NOMINATIM_URL,
            params=params,
            headers=HEADERS,
            timeout=20
        )

        response.raise_for_status()

        results = response.json()
        destinations = []

        for place in results:

            address = place.get("address", {})

            city = (
                address.get("city")
                or address.get("town")
                or address.get("village")
                or address.get("municipality")
                or address.get("county")
                or ""
            )

            destinations.append({
                "name": place.get("name", ""),
                "city": city,
                "state": address.get("state", ""),
                "country": address.get("country", ""),
                "country_code": address.get("country_code", "").upper(),
                "latitude": float(place["lat"]),
                "longitude": float(place["lon"]),
                "display_name": place.get("display_name", ""),
                "category": place.get("category", ""),
                "type": place.get("type", ""),
                "osm_id": place.get("osm_id", "")
            })

        return destinations

    except requests.exceptions.RequestException as error:
        raise RuntimeError(f"Destination search failed: {error}")

    except (ValueError, KeyError) as error:
        raise RuntimeError(f"Invalid destination data: {error}")
