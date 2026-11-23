
from services.budget_service import calculate_trip_budget


print("=" * 55)
print("       AI TRAVEL EXPENSE CALCULATOR")
print("=" * 55)

try:
    travellers = int(input("Number of travellers: "))
    days = int(input("Number of trip days: "))
    rooms = int(input("Number of hotel rooms: "))

    print("\nEnter estimated expenses in INR")

    travel = float(input("Travel cost per person (round trip): "))
    hotel = float(input("Hotel cost per room per night: "))
    food = float(input("Food cost per person per day: "))
    transport = float(input("Local transport per person per day: "))
    attractions = float(input("Attraction tickets per person (whole trip): "))

    result = calculate_trip_budget(
        travellers=travellers,
        days=days,
        rooms=rooms,
        travel_cost_per_person=travel,
        hotel_cost_per_room=hotel,
        food_cost_per_person=food,
        local_transport_per_person=transport,
        attraction_cost_per_person=attractions
    )

    print("\n" + "=" * 55)
    print("             YOUR TRAVEL BUDGET")
    print("=" * 55)

    print(f"Travel expenses:       Rs. {result['travel']:,.2f}")
    print(f"Hotel expenses:        Rs. {result['hotel']:,.2f}")
    print(f"Food expenses:         Rs. {result['food']:,.2f}")
    print(f"Local transportation:  Rs. {result['local_transport']:,.2f}")
    print(f"Attraction tickets:    Rs. {result['attractions']:,.2f}")
    print("-" * 55)
    print(f"Subtotal:              Rs. {result['subtotal']:,.2f}")
    print(f"Miscellaneous (10%):   Rs. {result['miscellaneous']:,.2f}")
    print("=" * 55)
    print(f"TOTAL BUDGET:          Rs. {result['total_budget']:,.2f}")
    print(f"BUDGET PER PERSON:     Rs. {result['per_person_budget']:,.2f}")
    print("=" * 55)

except ValueError as error:
    print("\nInput error:", error)
