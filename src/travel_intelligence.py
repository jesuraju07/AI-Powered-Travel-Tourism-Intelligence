
import pandas as pd
import joblib
import os

from recommendation import recommend_places


# Project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "data", "processed")
MODEL_DIR = os.path.join(BASE_DIR, "models")


# Load datasets
destinations = pd.read_csv(
    os.path.join(DATA_DIR, "clustered_destinations.csv")
)

tourism = pd.read_csv(
    os.path.join(DATA_DIR, "cleaned_tourism_statistics.csv")
)

reviews = pd.read_csv(
    os.path.join(DATA_DIR, "cleaned_tourist_reviews.csv")
)


# Load trained models
sentiment_model = joblib.load(
    os.path.join(MODEL_DIR, "sentiment_model.pkl")
)

tfidf = joblib.load(
    os.path.join(MODEL_DIR, "tfidf_vectorizer.pkl")
)

kmeans = joblib.load(
    os.path.join(MODEL_DIR, "clustering_model.pkl")
)

scaler = joblib.load(
    os.path.join(MODEL_DIR, "destination_scaler.pkl")
)


# Prepare recommendation data
recommendation_data = destinations[
    [
        "name_en",
        "country_en",
        "city_en",
        "category",
        "latitude",
        "longitude"
    ]
].dropna(
    subset=["name_en", "latitude", "longitude", "category"]
).reset_index(drop=True)


# Sentiment prediction
def predict_review_sentiment(review_text):

    review_vector = tfidf.transform([review_text])

    prediction = sentiment_model.predict(review_vector)

    return prediction[0]


# Destination recommendations
def get_recommendations(place_name, top_n=5):

    return recommend_places(
        recommendation_data,
        place_name,
        top_n
    )


# Destination cluster prediction
def predict_destination_cluster(latitude, longitude):

    location = pd.DataFrame({
        "latitude": [latitude],
        "longitude": [longitude]
    })

    location_scaled = scaler.transform(location)

    cluster = kmeans.predict(location_scaled)

    return int(cluster[0])


# Display tourism statistics
def get_tourism_statistics(country_name):

    result = tourism[
        tourism["entity"].str.lower() == country_name.lower()
    ]

    return result.sort_values("year")
