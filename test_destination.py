
from services.destination_service import search_destinations


search_text = input("Enter a city or destination: ")

try:
    results = search_destinations(search_text)

    if not results:
        print("\nNo destinations found.")

    for number, place in enumerate(results, start=1):
        print("\n" + "=" * 50)
        print(f"RESULT {number}")
        print("=" * 50)

        print("Name:", place["name"])
        print("City:", place["city"])
        print("State:", place["state"])
        print("Country:", place["country"])
        print("Country Code:", place["country_code"])
        print("Latitude:", place["latitude"])
        print("Longitude:", place["longitude"])
        print("Category:", place["category"])
        print("Type:", place["type"])
        print("Full Address:", place["display_name"])

except RuntimeError as error:
    print("\nERROR:", error)
