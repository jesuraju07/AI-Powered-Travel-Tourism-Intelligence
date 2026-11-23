
from services.destination_service import search_destinations
from services.food_service import find_food_places


city = input("Enter destination city: ")

try:
    destinations = search_destinations(city)

    if not destinations:
        print("Destination not found.")
        raise SystemExit

    for i, place in enumerate(destinations, start=1):
        print(i, place["display_name"])

    choice = int(input("\nSelect destination number: ")) - 1

    if choice < 0 or choice >= len(destinations):
        print("Invalid selection.")
        raise SystemExit

    selected = destinations[choice]

    print("\nSelected:", selected["display_name"])
    print("\nSearching restaurants and food spots...")

    food_places = find_food_places(
        selected["latitude"],
        selected["longitude"]
    )

    print("\nTotal food places found:", len(food_places))

    for i, place in enumerate(food_places[:25], start=1):

        print("\n" + "=" * 45)
        print("FOOD PLACE:", i)
        print("Name:", place["name"])
        print("Category:", place["category"])
        print("Cuisine:", place["cuisine"])
        print("Distance:", place["distance_km"], "km")
        print("Address:", place["address"])
        print("Opening Hours:", place["opening_hours"])
        print("Website:", place["website"])

except (RuntimeError, ValueError) as error:
    print("\nERROR:", error)
