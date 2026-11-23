
import pandas as pd
import numpy as np


def recommend_places(recommendation_data, place_name, top_n=5):

    selected = recommendation_data[
        recommendation_data["name_en"].str.lower() == place_name.lower()
    ]

    if selected.empty:
        return "Destination not found!"

    selected = selected.iloc[0]

    lat1 = np.radians(selected["latitude"])
    lon1 = np.radians(selected["longitude"])

    lat2 = np.radians(recommendation_data["latitude"])
    lon2 = np.radians(recommendation_data["longitude"])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        np.sin(dlat / 2) ** 2
        + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    )

    distance = 6371 * 2 * np.arcsin(np.sqrt(a))

    results = recommendation_data.copy()
    results["distance_km"] = distance

    results = results.drop(index=selected.name)

    results = results.sort_values("distance_km").head(top_n)

    return results[
        ["name_en", "country_en", "category", "distance_km"]
    ].round({"distance_km": 2})
