from services.destination_service import search_destinations
from services.attraction_service import find_attractions
from services.itinerary_service import plan_itinerary


def get_value(data, *keys):
    for key in keys:
        value = data.get(key)
        if value is not None:
            return value
    return None


print("=" * 60)
print("       REAL DESTINATION TRAVEL ITINERARY")
print("=" * 60)

destination_name = input("\nEnter destination city: ").strip()

print("\nSearching for destination...")

destinations = search_destinations(destination_name, limit=5)

if not destinations:
    print("Destination not found. Try another city.")
    raise SystemExit

print("\nAvailable destinations:")

for i, destination in enumerate(destinations, start=1):
    name = get_value(destination, "name", "city", "display_name")
    country = get_value(destination, "country", "country_en")

    label = str(name or "Unknown destination")

    if country and str(country).lower() not in label.lower():
        label += ", " + str(country)

    print(f"{i}. {label}")

choice = int(input("\nSelect destination number: "))

if choice < 1 or choice > len(destinations):
    print("Invalid selection.")
    raise SystemExit

selected = destinations[choice - 1]

latitude = get_value(selected, "latitude", "lat")
longitude = get_value(selected, "longitude", "lon", "lng")

if latitude is None or longitude is None:
    print("Coordinates are missing for this destination.")
    raise SystemExit

print("\nSelected destination:",
      get_value(selected, "display_name", "name", "city"))

days = int(input("Enter number of trip days: "))
max_places = int(input("Maximum attractions per day: "))

print("\nSearching for real tourist attractions...")

try:
    attractions = find_attractions(
        float(latitude),
        float(longitude),
        radius=2500
    )
except RuntimeError as error:
    print("\nSorry, the attraction data service is temporarily unavailable.")
    print("Please try again later.")
    print("Details:", error)
    raise SystemExit

if not attractions:
    print("No attractions found for this location.")
    raise SystemExit

# Convert attraction results into the format required by the planner.
planner_places = []

for place in attractions:
    name = get_value(place, "name")
    lat = get_value(place, "lat", "latitude")
    lon = get_value(place, "lon", "longitude")

    if name and lat is not None and lon is not None:
        planner_places.append({
            "name": name,
            "lat": float(lat),
            "lon": float(lon),
            "category": get_value(place, "category") or "Attraction"
        })

if not planner_places:
    print("Attractions were found, but usable coordinates are missing.")
    raise SystemExit

itinerary = plan_itinerary(
    planner_places,
    days,
    max_places
)

print("\n" + "=" * 60)
print("             YOUR REAL TRAVEL ITINERARY")
print("=" * 60)

for day in itinerary:
    print(f"\nDAY {day['day']}")

    for number, place in enumerate(day["places"], start=1):
        print(f"{number}. {place['name']}")
        print(f"   Category: {place['category']}")

print("\nTotal attractions found:", len(planner_places))
print("Total attractions scheduled:",
      sum(len(day["places"]) for day in itinerary))

print("=" * 60)

