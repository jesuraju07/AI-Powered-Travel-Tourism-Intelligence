from services.itinerary_service import plan_itinerary


sample_attractions = [
    {
        "name": "Central Park",
        "lat": 40.7829,
        "lon": -73.9654,
        "category": "Park"
    },
    {
        "name": "Times Square",
        "lat": 40.7580,
        "lon": -73.9855,
        "category": "Attraction"
    },
    {
        "name": "Rockefeller Center",
        "lat": 40.7587,
        "lon": -73.9787,
        "category": "Landmark"
    },
    {
        "name": "Statue of Liberty",
        "lat": 40.6892,
        "lon": -74.0445,
        "category": "Monument"
    },
    {
        "name": "The Metropolitan Museum of Art",
        "lat": 40.7794,
        "lon": -73.9632,
        "category": "Museum"
    },
    {
        "name": "Empire State Building",
        "lat": 40.7484,
        "lon": -73.9857,
        "category": "Landmark"
    }
]


print("=" * 55)
print("          AI TRAVEL ITINERARY PLANNER")
print("=" * 55)

days = int(input("Enter number of trip days: "))
max_places = int(input("Maximum attractions per day: "))

itinerary = plan_itinerary(
    sample_attractions,
    days,
    max_places
)

print("\nYOUR DAY-BY-DAY ITINERARY")

for day in itinerary:
    print(f"\nDAY {day['day']}")

    for number, place in enumerate(day["places"], start=1):
        print(f"{number}. {place['name']} ({place['category']})")

print("\nTotal attractions planned:",
      sum(len(day["places"]) for day in itinerary))

print("=" * 55)
