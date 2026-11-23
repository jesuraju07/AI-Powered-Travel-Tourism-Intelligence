
def calculate_trip_budget(
    travellers,
    days,
    rooms,
    travel_cost_per_person,
    hotel_cost_per_room,
    food_cost_per_person,
    local_transport_per_person,
    attraction_cost_per_person,
    miscellaneous_percent=10
):

    if travellers < 1 or days < 1 or rooms < 1:
        raise ValueError("Travellers, days and rooms must be at least 1.")

    if rooms > travellers:
        raise ValueError("Rooms cannot exceed the number of travellers.")

    costs = [
        travel_cost_per_person,
        hotel_cost_per_room,
        food_cost_per_person,
        local_transport_per_person,
        attraction_cost_per_person
    ]

    if any(cost < 0 for cost in costs):
        raise ValueError("Expenses cannot be negative.")

    if not 0 <= miscellaneous_percent <= 100:
        raise ValueError("Miscellaneous percentage must be between 0 and 100.")

    # Travel expenses for all travellers
    travel_total = travel_cost_per_person * travellers

    # Accommodation expenses
    hotel_total = hotel_cost_per_room * rooms * days

    # Food expenses
    food_total = food_cost_per_person * travellers * days

    # Local transportation
    transport_total = local_transport_per_person * travellers * days

    # Tourist attraction tickets
    attraction_total = attraction_cost_per_person * travellers

    subtotal = (
        travel_total
        + hotel_total
        + food_total
        + transport_total
        + attraction_total
    )

    miscellaneous_total = subtotal * miscellaneous_percent / 100

    grand_total = subtotal + miscellaneous_total

    return {
        "travel": round(travel_total, 2),
        "hotel": round(hotel_total, 2),
        "food": round(food_total, 2),
        "local_transport": round(transport_total, 2),
        "attractions": round(attraction_total, 2),
        "subtotal": round(subtotal, 2),
        "miscellaneous": round(miscellaneous_total, 2),
        "total_budget": round(grand_total, 2),
        "per_person_budget": round(grand_total / travellers, 2)
    }
