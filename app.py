import os
import sys
import math
import requests
import pandas as pd
import streamlit as st
import joblib

from services.destination_service import search_destinations
from services.attraction_service import find_attractions
from services.budget_service import calculate_trip_budget
from services.itinerary_service import plan_itinerary

# ---------------------------------------------------------
# Configuration and paths
# ---------------------------------------------------------
st.set_page_config(
    page_title="AI Travel & Tourism Intelligence",
   page_icon="🌍",
    layout="wide"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_CANDIDATES = [
    os.path.join(BASE_DIR, "data", "processed"),
    os.path.join(BASE_DIR, "processed"),
]
MODEL_PATH = os.path.join(BASE_DIR, "models", "sentiment_pipeline.pkl")

def find_data_file(filename):
    for folder in DATA_CANDIDATES:
        path = os.path.join(folder, filename)
        if os.path.isfile(path):
            return path
    return None

@st.cache_data
def load_csv(filename):
    path = find_data_file(filename)
    if not path:
        return None
    try:
        return pd.read_csv(path)
    except Exception as exc:
        st.warning(f"Could not load {filename}: {exc}")
        return None

@st.cache_resource
def load_sentiment_model():
    if not os.path.isfile(MODEL_PATH):
        return None
    try:
        return joblib.load(MODEL_PATH)
    except Exception:
        return None

destinations = load_csv("cleaned_destinations.csv")
tourism = load_csv("cleaned_tourism_statistics.csv")
reviews = load_csv("cleaned_tourist_reviews.csv")
clusters = load_csv("clustered_destinations.csv")
packages = load_csv("travel_packages.csv")
sentiment_model = load_sentiment_model()

# ---------------------------------------------------------
# Helpers
# -----------------------------------------

def find_local_attractions(latitude, longitude, radius=5000):

    if destinations is None or destinations.empty:
        return []

    required_columns = ["latitude", "longitude", "name_en"]

    if not all(col in destinations.columns for col in required_columns):
        return []

    df = destinations.copy()

    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

    df = df.dropna(subset=required_columns)

    lat1 = math.radians(latitude)
    lon1 = math.radians(longitude)

    lat2 = df["latitude"].apply(math.radians)
    lon2 = df["longitude"].apply(math.radians)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * lat2.apply(math.cos)
        * (dlon / 2).apply(math.sin) ** 2
    )

    df["distance_km"] = 6371 * 2 * a.apply(math.sqrt).apply(
        lambda x: math.asin(min(1, x))
    )

    df = df[df["distance_km"] <= radius / 1000]
    df = df.sort_values("distance_km").head(100)

    places = []

    for _, row in df.iterrows():
        places.append({
            "name": str(row["name_en"]),
            "category": row.get("category", "Destination"),
            "latitude": row["latitude"],
            "longitude": row["longitude"],
            "lat": row["latitude"],
            "lon": row["longitude"],
            "distance_km": round(row["distance_km"], 2),
            "website": "",
            "description": "",
            "address": str(row.get("country_en", ""))
        })

    return places
# ---------------------------------------------------------
def safe_text(value, default="Not available"):
    if pd.isna(value) or str(value).strip() == "":
        return default
    return str(value)

def osm_food_search(lat, lon, radius=2500):
    """Optional live food search using OpenStreetMap Overpass."""
    query = f"""
    [out:json][timeout:20];
    (
      nwr(around:{radius},{lat},{lon})["amenity"~"restaurant|cafe|fast_food|food_court|ice_cream"];
    );
    out center tags;
    """
    endpoints = [
        "https://overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter"
    ]
    headers = {
        "User-Agent": "TravelTourismIntelligence/1.0 (educational project)",
        "Accept": "application/json"
    }
    last_error = None
    for endpoint in endpoints:
        try:
            response = requests.post(
                endpoint, data={"data": query}, headers=headers, timeout=25
            )
            response.raise_for_status()
            elements = response.json().get("elements", [])
            rows, seen = [], set()
            for item in elements:
                tags = item.get("tags", {})
                name = tags.get("name")
                if not name:
                    continue
                if "lat" in item and "lon" in item:
                    plat, plon = item["lat"], item["lon"]
                elif "center" in item:
                    plat, plon = item["center"].get("lat"), item["center"].get("lon")
                else:
                    continue
                if plat is None or plon is None:
                    continue
                key = (name.strip().lower(), round(float(plat), 5), round(float(plon), 5))
                if key in seen:
                    continue
                seen.add(key)
                rows.append({
                    "Name": name,
                    "Type": tags.get("amenity", "Food place"),
                    "Cuisine": tags.get("cuisine", "Not listed"),
                    "Opening hours": tags.get("opening_hours", "Not listed"),
                    "Address": ", ".join(
                        str(tags[k]) for k in ["addr:street", "addr:city"] if tags.get(k)
                    ) or "Not listed",
                    "Website": tags.get("website", ""),
                    "Latitude": float(plat),
                    "Longitude": float(plon),
                })
            return pd.DataFrame(rows)
        except Exception as exc:
            last_error = exc
    raise RuntimeError(f"Food data service unavailable: {last_error}")

def get_destination_options():
    options = []
    if destinations is not None:
        cols = [c for c in ["name_en", "city_en", "country_en", "latitude", "longitude", "category"] if c in destinations.columns]
        if {"name_en", "latitude", "longitude"}.issubset(cols):
            subset = destinations[cols].dropna(subset=["name_en", "latitude", "longitude"])
            for _, row in subset.iterrows():
                options.append({
                    "name": safe_text(row.get("name_en"), "Destination"),
                    "city": safe_text(row.get("city_en"), ""),
                    "country": safe_text(row.get("country_en"), ""),
                    "latitude": float(row["latitude"]),
                    "longitude": float(row["longitude"]),
                    "category": safe_text(row.get("category"), "Place"),
                    "source": "Project destination dataset"
                })
    return options

def destination_label(item):
    city = item.get("city", "")
    country = item.get("country", "")
    details = ", ".join(x for x in [city, country] if x and x != "Not available")
    return f'{item["name"]}' + (f" — {details}" if details else "")

def render_destination_map(lat, lon):
    st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}))

# ---------------------------------------------------------
# Navigation
# ---------------------------------------------------------
st.sidebar.title("🌍 Travel Intelligence")
st.sidebar.caption("AI-Powered Travel and Tourism Intelligence Platform")
page = st.sidebar.radio(
    "Navigate",
    [
        "Home",
        "Global Destination Search",
        "Attractions & Itinerary",
        "Food Explorer",
        "Trip Budget Calculator",
        "Travel Packages",
        "Tourism Analytics",
        "Sentiment Analysis",
        "Clustering & Recommendations",
    ],
)
st.sidebar.divider()
st.sidebar.caption("Dataset-based insights and optional OpenStreetMap live lookups.")

# ---------------------------------------------------------
# Home
# ---------------------------------------------------------
if page == "Home":
    st.title("🌍 AI-Powered Travel and Tourism Intelligence")
    st.write("Explore destinations, attractions, food places, budgets, itineraries, tourism statistics and traveller sentiment.")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Destination records", f"{len(destinations):,}" if destinations is not None else "Not loaded")
    c2.metric("Countries", f"{destinations['country_en'].nunique():,}" if destinations is not None and "country_en" in destinations else "—")
    c3.metric("Tourist reviews", f"{len(reviews):,}" if reviews is not None else "Not loaded")
    c4.metric("Sample packages", f"{len(packages):,}" if packages is not None else "Not loaded")
    st.subheader("Project data status")
    status = {
        "Destinations": destinations,
        "Tourism statistics": tourism,
        "Tourist reviews": reviews,
        "Clustered destinations": clusters,
        "Travel packages": packages,
        "Sentiment model": sentiment_model,
    }
    for label, obj in status.items():
        st.write(("✅ " if obj is not None else "⚠️ ") + label + (" loaded" if obj is not None else " not available"))
    if destinations is not None and "category" in destinations:
        st.subheader("Top destination categories")
        st.bar_chart(destinations["category"].fillna("Unknown").value_counts().head(12))
    if reviews is not None and "sentiment" in reviews:
        st.subheader("Review sentiment distribution")
        st.bar_chart(reviews["sentiment"].value_counts())

# ---------------------------------------------------------
# Global destination search
# ---------------------------------------------------------
elif page == "Global Destination Search":
    st.title("🔎 Global Destination Search")
    st.info("Search the project dataset or use OpenStreetMap geocoding for a broader city/place lookup. Coverage depends on the data provider.")
    query = st.text_input("Enter a city, destination or country", placeholder="e.g. New York, Paris, Goa")
    if query.strip():
        if destinations is not None:
            d = destinations.copy()
            for col in ["name_en", "city_en", "country_en", "category"]:
                if col not in d:
                    d[col] = ""
            mask = pd.Series(False, index=d.index)
            for col in ["name_en", "city_en", "country_en"]:
                mask |= d[col].astype(str).str.contains(query.strip(), case=False, na=False, regex=False)
            found = d[mask]
            st.write(f"**{len(found):,} matching records in your project dataset**")
            show_cols = [c for c in ["name_en", "city_en", "country_en", "category", "latitude", "longitude", "url_en"] if c in found.columns]
            if not found.empty:
                st.dataframe(found[show_cols].head(100), use_container_width=True, hide_index=True)
            else:
                st.warning("No matching record in the local destination dataset. Try the global lookup below.")
        if st.button("Search globally with OpenStreetMap", type="primary"):
            try:
                with st.spinner("Searching global place records..."):
                    results = search_destinations(query, limit=10)
                if results:
                    st.session_state["global_results"] = results
                else:
                    st.warning("No global results found.")
            except Exception as exc:
                st.error(str(exc))
    global_results = st.session_state.get("global_results", [])
    if global_results:
        labels = [f'{r.get("display_name", r.get("name", "Place"))}' for r in global_results]
        idx = st.selectbox("Select global search result", range(len(labels)), format_func=lambda i: labels[i])
        chosen = global_results[idx]
        st.subheader(chosen.get("name") or chosen.get("display_name"))
        a, b, c = st.columns(3)
        a.metric("Country", chosen.get("country") or "—")
        b.metric("Latitude", round(chosen["latitude"], 5))
        c.metric("Longitude", round(chosen["longitude"], 5))
        render_destination_map(chosen["latitude"], chosen["longitude"])
        st.caption("Coordinates and place details are supplied by OpenStreetMap Nominatim.")

# ---------------------------------------------------------
# Attractions and itinerary
# ---------------------------------------------------------
elif page == "Attractions & Itinerary":
    st.title("🗺️ Attractions & Day-by-Day Itinerary")
    st.write("Search a destination, retrieve nearby mapped attractions and organise them into a simple distance-based itinerary.")
    city = st.text_input("Destination to search", placeholder="e.g. Paris, London, Goa", key="itinerary_city")
    if st.button("Find destination", key="find_itinerary_destination"):
        try:
            st.session_state["itinerary_destinations"] = search_destinations(city, limit=8)
        except Exception as exc:
            st.error(str(exc))
    choices = st.session_state.get("itinerary_destinations", [])
    if choices:
        labels = [r.get("display_name", r.get("name", "Place")) for r in choices]
        selected_idx = st.selectbox("Choose the correct location", range(len(labels)), format_func=lambda i: labels[i])
        selected = choices[selected_idx]
        st.write("Selected:", selected.get("display_name"))
        days_col, places_col, radius_col = st.columns(3)
        days = days_col.number_input("Trip days", min_value=1, max_value=30, value=3)
        per_day = places_col.number_input("Maximum places per day", min_value=1, max_value=8, value=3)
        radius = radius_col.selectbox("Search radius", [1000, 2500, 5000], index=1, format_func=lambda x: f"{x/1000:g} km")
        if st.button("Retrieve attractions and build itinerary", type="primary"):
            try:
                with st.spinner("Retrieving OpenStreetMap attractions. Public servers can be busy..."):
                    places = find_attractions(selected["latitude"], selected["longitude"], radius=radius, max_results=150)
                if not places:
                    st.warning("No named attractions with coordinates were returned for this area.")
                else:
                    st.session_state["current_attractions"] = places
                    st.session_state["current_itinerary"] = plan_itinerary(places, int(days), int(per_day))
                    st.session_state["itinerary_location"] = selected
            except Exception as exc:
                st.error(f"Attraction lookup failed: {exc}")
                st.info("This is a public OpenStreetMap server availability issue. Try a smaller radius or retry later. The rest of the app remains available.")
    places = st.session_state.get("current_attractions", [])
    if places:
        st.subheader(f"Attractions found: {len(places)}")
        display = pd.DataFrame(places)
        display = display.drop(columns=["priority"], errors="ignore")
        st.dataframe(display, use_container_width=True, hide_index=True)
        loc = st.session_state.get("itinerary_location", {})
        map_df = pd.DataFrame({"lat": [p["lat"] for p in places], "lon": [p["lon"] for p in places]})
        st.subheader("Attraction map")
        st.map(map_df)
        st.subheader("Your itinerary")
        for day in st.session_state.get("current_itinerary", []):
            with st.expander(f"Day {day['day']}", expanded=True):
                for number, place in enumerate(day["places"], 1):
                    st.write(f"{number}. **{place['name']}** — {place.get('category', 'Attraction')} ({place.get('distance_km', 0)} km from destination centre)")
        st.caption("The itinerary groups places by straight-line geographic distance. It does not calculate road routes, opening hours or ticket availability.")

# ---------------------------------------------------------
# Food explorer
# ---------------------------------------------------------
elif page == "Food Explorer":
    st.title("🍽️ Food & Nearby Places")
    st.write("Look up restaurants, cafes and quick-service food places around a searched destination using OpenStreetMap.")
    food_city = st.text_input("Enter destination", placeholder="e.g. Paris")
    if st.button("Search destination for food places"):
        try:
            st.session_state["food_destinations"] = search_destinations(food_city, limit=5)
        except Exception as exc:
            st.error(str(exc))
    food_destinations = st.session_state.get("food_destinations", [])
    if food_destinations:
        labels = [r.get("display_name", r.get("name", "Place")) for r in food_destinations]
        fi = st.selectbox("Choose destination", range(len(labels)), format_func=lambda i: labels[i], key="food_destination_choice")
        fd = food_destinations[fi]
        food_radius = st.selectbox("Food search radius", [1000, 2500, 5000], index=1, format_func=lambda x: f"{x/1000:g} km")
        if st.button("Find restaurants and cafes"):
            try:
                with st.spinner("Searching OpenStreetMap..."):
                    food_df = osm_food_search(fd["latitude"], fd["longitude"], food_radius)
                st.session_state["food_results"] = food_df
            except Exception as exc:
                st.error(str(exc))
        food_df = st.session_state.get("food_results")
        if food_df is not None:
            if food_df.empty:
                st.warning("No named food places found in this search area.")
            else:
                st.dataframe(food_df.drop(columns=["Latitude", "Longitude"], errors="ignore"), use_container_width=True, hide_index=True)
                st.map(food_df.rename(columns={"Latitude": "lat", "Longitude": "lon"})[["lat", "lon"]])
                st.caption("Opening hours and cuisine are shown only when listed in OpenStreetMap. Ratings and prices are not provided by this lookup.")

# ---------------------------------------------------------
# Budget calculator
# ---------------------------------------------------------
elif page == "Trip Budget Calculator":
    st.title("💰 Trip Budget Calculator")
    st.caption("Enter your own estimated prices. These are calculations, not live travel quotes.")
    with st.form("budget_form"):
        c1, c2, c3 = st.columns(3)
        travellers = c1.number_input("Travellers", min_value=1, max_value=100, value=2)
        days = c2.number_input("Trip days", min_value=1, max_value=365, value=5)
        rooms = c3.number_input("Hotel rooms", min_value=1, max_value=100, value=1)
        c1, c2 = st.columns(2)
        travel = c1.number_input("Round-trip travel per person (₹)", min_value=0.0, value=15000.0, step=500.0)
        hotel = c2.number_input("Hotel per room per night (₹)", min_value=0.0, value=3000.0, step=250.0)
        c1, c2, c3 = st.columns(3)
        food = c1.number_input("Food per person per day (₹)", min_value=0.0, value=1000.0, step=100.0)
        local = c2.number_input("Local transport per person per day (₹)", min_value=0.0, value=500.0, step=100.0)
        tickets = c3.number_input("Attraction tickets per person (whole trip) (₹)", min_value=0.0, value=3000.0, step=100.0)
        misc = st.slider("Miscellaneous allowance (%)", 0, 30, 10)
        submitted = st.form_submit_button("Calculate trip budget", type="primary")
    if submitted:
        try:
            result = calculate_trip_budget(int(travellers), int(days), int(rooms), travel, hotel, food, local, tickets, misc)
            st.subheader("Estimated trip cost")
            for key, label in [
                ("travel", "Travel"), ("hotel", "Hotel"), ("food", "Food"),
                ("local_transport", "Local transport"), ("attractions", "Attraction tickets"),
                ("subtotal", "Subtotal"), ("miscellaneous", f"Miscellaneous ({misc}%)")
            ]:
                st.write(f"**{label}:** ₹{result[key]:,.2f}")
            a, b = st.columns(2)
            a.metric("Total trip budget", f"₹{result['total_budget']:,.2f}")
            b.metric("Budget per person", f"₹{result['per_person_budget']:,.2f}")
        except Exception as exc:
            st.error(str(exc))

# ---------------------------------------------------------
# Packages
# ---------------------------------------------------------
elif page == "Travel Packages":
    st.title("✈️ Travel Packages")
    if packages is None or packages.empty:
        st.error("Travel package dataset is missing.")
    else:
        data = packages.copy()
        data["price_inr"] = pd.to_numeric(data["price_inr"], errors="coerce")
        search = st.text_input("Search package, destination or country")
        countries = ["All"] + sorted(data["country"].dropna().astype(str).unique().tolist())
        country = st.selectbox("Country", countries)
        min_price = int(data["price_inr"].min())
        max_price = int(data["price_inr"].max())
        budget = st.slider("Price range (₹)", min_price, max_price, (min_price, max_price))
        if search:
            mask = (
                data["package_name"].astype(str).str.contains(search, case=False, na=False, regex=False)
                | data["destination"].astype(str).str.contains(search, case=False, na=False, regex=False)
                | data["country"].astype(str).str.contains(search, case=False, na=False, regex=False)
            )
            data = data[mask]
        if country != "All":
            data = data[data["country"] == country]
        data = data[data["price_inr"].between(*budget)]
        st.write(f"**{len(data)} packages found**")
        for _, row in data.iterrows():
            with st.container(border=True):
                a, b, c = st.columns([3, 1, 2])
                a.subheader(row["package_name"])
                a.write(f'{row["destination"]}, {row["country"]}')
                b.metric("Sample price", f'₹{row["price_inr"]:,.0f}')
                c.write(f'{row["duration_days"]} days / {row["duration_nights"]} nights')
                with st.expander("Package details"):
                    st.write("Hotel:", row.get("hotel_category", "Not listed"))
                    st.write("Transport:", row.get("transport", "Not listed"))
                    st.write("Meals:", row.get("meals", "Not listed"))
                    st.write("Activities:", row.get("activities", "Not listed"))
                    st.write(row.get("description", ""))
        st.caption("The supplied package dataset contains demonstration/sample packages. Prices and availability are not live booking quotes.")

# ---------------------------------------------------------
# Tourism analytics
# ---------------------------------------------------------
elif page == "Tourism Analytics":
    st.title("📊 Tourism Analytics")
    if tourism is None:
        st.error("Tourism statistics dataset is missing.")
    else:
        st.dataframe(tourism, use_container_width=True, hide_index=True)
        if "owid_region" in tourism:
            st.subheader("Records by world region")
            st.bar_chart(tourism["owid_region"].fillna("Unknown").value_counts())
        if {"year", "in_tour_arrivals_trips_total_overnight_vis_tourists"}.issubset(tourism.columns):
            chart = tourism.copy()
            chart["year"] = pd.to_numeric(chart["year"], errors="coerce")
            metric = "in_tour_arrivals_trips_total_overnight_vis_tourists"
            chart[metric] = pd.to_numeric(chart[metric], errors="coerce")
            chart = chart.dropna(subset=["year", metric])
            if not chart.empty:
                st.subheader("Tourism arrivals by year")
                st.line_chart(chart.groupby("year")[metric].sum().sort_index())

# ---------------------------------------------------------
# Sentiment analysis
# ---------------------------------------------------------
elif page == "Sentiment Analysis":
    st.title("😊 Tourist Review Sentiment Analysis")
    review_text = st.text_area("Enter a tourist review", placeholder="The hotel was beautiful and the service was excellent.")
    if st.button("Predict sentiment", type="primary"):
        if not review_text.strip():
            st.warning("Enter a review first.")
        elif sentiment_model is None:
            st.error("The sentiment model could not be loaded. Check models/sentiment_pipeline.pkl and your installed package versions.")
        else:
            try:
                prediction = sentiment_model.predict([review_text])[0]
                st.success(f"Predicted sentiment: {prediction}")
            except Exception as exc:
                st.error(f"Prediction failed: {exc}")
    if reviews is not None:
        st.divider()
        if "sentiment" in reviews:
            st.subheader("Dataset sentiment distribution")
            st.bar_chart(reviews["sentiment"].value_counts())
        st.subheader("Review sample")
        st.dataframe(reviews.head(100), use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# Clustering and recommendations
# ---------------------------------------------------------
elif page == "Clustering & Recommendations":
    st.title("🧠 Destination Clustering & Recommendations")
    if clusters is not None:
        cluster_col = "cluster" if "cluster" in clusters.columns else ("Cluster" if "Cluster" in clusters.columns else None)
        if cluster_col:
            st.subheader("Destinations by cluster")
            counts = clusters[cluster_col].value_counts().sort_index()
            st.bar_chart(counts)
            selected_cluster = st.selectbox("Choose a cluster", sorted(clusters[cluster_col].dropna().unique().tolist()))
            subset = clusters[clusters[cluster_col] == selected_cluster]
            show = [c for c in ["name_en", "city_en", "country_en", "category", "latitude", "longitude"] if c in subset.columns]
            st.write(f"{len(subset)} destination records in cluster {selected_cluster}")
            st.dataframe(subset[show].head(200), use_container_width=True, hide_index=True)
        else:
            st.warning("Cluster column was not found.")
    elif destinations is not None:
        st.info("Cluster file missing. You can still browse destinations by country.")
    if destinations is not None and "country_en" in destinations:
        st.divider()
        st.subheader("Browse destination recommendations by country")
        country_list = sorted(destinations["country_en"].dropna().astype(str).unique())
        selected_country = st.selectbox("Select a country", country_list, key="recommend_country")
        subset = destinations[destinations["country_en"] == selected_country]
        show = [c for c in ["name_en", "city_en", "country_en", "category"] if c in subset.columns]
        st.dataframe(subset[show].head(100), use_container_width=True, hide_index=True)

st.divider()
st.caption("AI-Powered Travel and Tourism Intelligence Platform | Built with Python, Streamlit, Machine Learning and OpenStreetMap data.")
