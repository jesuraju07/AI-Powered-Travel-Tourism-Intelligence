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
        raise ValueError("Rooms cannot exceed travellers.")

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
        raise ValueError("Invalid miscellaneous percentage.")

    travel = travel_cost_per_person * travellers
    hotel = hotel_cost_per_room * rooms * days
    food = food_cost_per_person * travellers * days
    transport = local_transport_per_person * travellers * days
    attractions = attraction_cost_per_person * travellers

    subtotal = travel + hotel + food + transport + attractions
    miscellaneous = subtotal * miscellaneous_percent / 100
    total = subtotal + miscellaneous

    return {
        "travel": round(travel, 2),
        "hotel": round(hotel, 2),
        "food": round(food, 2),
        "local_transport": round(transport, 2),
        "attractions": round(attractions, 2),
        "subtotal": round(subtotal, 2),
        "miscellaneous": round(miscellaneous, 2),
        "total_budget": round(total, 2),
        "per_person_budget": round(total / travellers, 2)
    }
