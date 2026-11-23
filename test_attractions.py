
from services.destination_service import search_destinations
from services.attraction_service import find_attractions


city = input("Enter destination city: ")

try:
    destinations = search_destinations(city)

    if not destinations:
        print("Destination not found.")
        raise SystemExit

    print("\nAvailable destinations:")

    for i, place in enumerate(destinations):
        print(
            i + 1,
            place["display_name"]
        )

    choice = int(input("\nSelect destination number: ")) - 1

    if choice < 0 or choice >= len(destinations):
        print("Invalid selection.")
        raise SystemExit

    selected = destinations[choice]

    print("\nSelected:", selected["display_name"])
    print("\nSearching tourist attractions...")

    attractions = find_attractions(
        selected["latitude"],
        selected["longitude"]
    )

    print("\nTotal attractions found:", len(attractions))

    for i, place in enumerate(attractions[:20], start=1):

        print("\n", "=" * 45)
        print("Attraction:", i)
        print("Name:", place["name"])
        print("Category:", place["category"])
        print("Distance:", place["distance_km"], "km")
        print("Latitude:", place["latitude"])
        print("Longitude:", place["longitude"])

except (RuntimeError, ValueError) as error:
    print("\nERROR:", error)
