
from pathlib import Path
import math

import joblib
import numpy as np
import pandas as pd

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field


# ==========================================================
# 1. APPLICATION CONFIGURATION
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent

DESTINATIONS_PATH = BASE_DIR / "data" / "processed" / "cleaned_destinations.csv"
TOURISM_PATH = BASE_DIR / "data" / "processed" / "cleaned_tourism_statistics.csv"
REVIEWS_PATH = BASE_DIR / "data" / "processed" / "cleaned_tourist_reviews.csv"
SENTIMENT_MODEL_PATH = BASE_DIR / "models" / "sentiment_pipeline.pkl"


app = FastAPI(
    title="AI Travel and Tourism Intelligence Platform",
    description="""
## Global AI-Powered Travel Intelligence Backend

Explore destinations, analyze tourism trends, predict tourist review
sentiment, and discover nearby attractions.

**Technology:** Python, FastAPI, Pandas, NumPy and Machine Learning.
    """,
    version="1.0.0",
    openapi_tags=[
        {
            "name": "General",
            "description": "System information and health monitoring"
        },
        {
            "name": "Destinations",
            "description": "Global destination search and discovery"
        },
        {
            "name": "Tourism Analytics",
            "description": "Tourism statistics and trends"
        },
        {
            "name": "Sentiment Analysis",
            "description": "Machine learning-based review sentiment analysis"
        },
        {
            "name": "Recommendations",
            "description": "Nearby destination recommendations"
        }
    ],
    swagger_ui_parameters={
        "docExpansion": "none",
        "defaultModelsExpandDepth": -1,
        "displayRequestDuration": True
    }
)


# ==========================================================
# 2. LOAD DATASETS
# ==========================================================

def load_csv(path: Path, dataset_name: str) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"{dataset_name} not found: {path}"
        )

    return pd.read_csv(path)


destinations_df = load_csv(
    DESTINATIONS_PATH,
    "Cleaned destinations dataset"
)

tourism_df = load_csv(
    TOURISM_PATH,
    "Cleaned tourism statistics dataset"
)


# Validate destination columns
required_destination_columns = [
    "name_en",
    "country_en",
    "city_en",
    "category",
    "latitude",
    "longitude"
]

for column in required_destination_columns:
    if column not in destinations_df.columns:
        raise ValueError(
            f"Missing destination column: {column}"
        )


# Validate tourism columns
required_tourism_columns = [
    "entity",
    "code",
    "year",
    "in_tour_arrivals_trips_total_overnight_vis_tourists",
    "owid_region"
]

for column in required_tourism_columns:
    if column not in tourism_df.columns:
        raise ValueError(
            f"Missing tourism column: {column}"
        )


# Convert tourism values to numeric
tourism_df["year"] = pd.to_numeric(
    tourism_df["year"],
    errors="coerce"
)

tourism_df[
    "in_tour_arrivals_trips_total_overnight_vis_tourists"
] = pd.to_numeric(
    tourism_df[
        "in_tour_arrivals_trips_total_overnight_vis_tourists"
    ],
    errors="coerce"
)

tourism_df = tourism_df.dropna(
    subset=[
        "entity",
        "year",
        "in_tour_arrivals_trips_total_overnight_vis_tourists"
    ]
).copy()

tourism_df["year"] = tourism_df["year"].astype(int)


# Lazy-loaded datasets and model
reviews_df = None
sentiment_model = None


def dataframe_to_records(data: pd.DataFrame):
    """Convert a DataFrame into JSON-safe records."""
    return data.to_json(
        orient="records",
        date_format="iso"
    ) and __import__("json").loads(
        data.to_json(orient="records", date_format="iso")
    )


def get_reviews():
    global reviews_df

    if reviews_df is None:
        reviews_df = load_csv(
            REVIEWS_PATH,
            "Cleaned tourist reviews dataset"
        )

        if "sentiment" not in reviews_df.columns:
            raise HTTPException(
                status_code=500,
                detail="Sentiment column is missing from reviews dataset"
            )

    return reviews_df


def get_sentiment_model():
    global sentiment_model

    if sentiment_model is None:
        if not SENTIMENT_MODEL_PATH.exists():
            raise HTTPException(
                status_code=500,
                detail="Sentiment model file was not found"
            )

        try:
            sentiment_model = joblib.load(SENTIMENT_MODEL_PATH)
        except Exception as error:
            raise HTTPException(
                status_code=500,
                detail=f"Could not load sentiment model: {error}"
            )

    return sentiment_model


# ==========================================================
# 3. GENERAL API
# ==========================================================

@app.get("/", tags=["General"], summary="Home")
def home():
    return {
        "message": "AI Travel and Tourism Intelligence API",
        "status": "Running successfully",
        "version": "1.0.0"
    }


@app.get("/health", tags=["General"], summary="Health Check")
def health_check():
    return {
        "status": "healthy",
        "message": "API is working correctly",
        "datasets": {
            "destinations": len(destinations_df),
            "tourism_records": len(tourism_df)
        }
    }


@app.get("/project", tags=["General"], summary="Project Information")
def project_info():
    return {
        "project": "AI-Powered Travel and Tourism Intelligence Platform",
        "features": [
            "Destination Search",
            "Tourist Attraction Discovery",
            "Travel Itinerary Planning",
            "Food Explorer",
            "Trip Budget Calculator",
            "Travel Package Recommendations",
            "Tourism Analytics",
            "Sentiment Analysis",
            "Destination Clustering"
        ]
    }


# ==========================================================
# 4. DESTINATION APIs
# ==========================================================

@app.get(
    "/destinations",
    tags=["Destinations"],
    summary="Get Destinations"
)
def get_destinations(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    data = destinations_df.iloc[skip:skip + limit]

    return {
        "total_destinations": len(destinations_df),
        "returned": len(data),
        "destinations": dataframe_to_records(data)
    }


@app.get(
    "/destinations/search",
    tags=["Destinations"],
    summary="Search Destinations"
)
def search_destinations(
    q: str = Query(..., min_length=1, max_length=150),
    limit: int = Query(20, ge=1, le=100)
):
    search_text = q.strip()

    if not search_text:
        raise HTTPException(
            status_code=422,
            detail="Search query cannot be empty"
        )

    search_columns = [
        "name_en",
        "country_en",
        "city_en",
        "category"
    ]

    mask = pd.Series(
        False,
        index=destinations_df.index
    )

    for column in search_columns:
        mask |= (
            destinations_df[column]
            .fillna("")
            .astype(str)
            .str.contains(
                search_text,
                case=False,
                regex=False
            )
        )

    results = destinations_df[mask].head(limit)

    return {
        "search_query": search_text,
        "total_results": int(mask.sum()),
        "returned": len(results),
        "destinations": dataframe_to_records(results)
    }


@app.get(
    "/destinations/countries",
    tags=["Destinations"],
    summary="Get Countries"
)
def get_countries():
    countries = sorted(
        destinations_df["country_en"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    return {
        "total_countries": len(countries),
        "countries": countries
    }


@app.get(
    "/destinations/categories",
    tags=["Destinations"],
    summary="Get Destination Categories"
)
def get_categories():
    categories = sorted(
        destinations_df["category"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    return {
        "total_categories": len(categories),
        "categories": categories
    }


# ==========================================================
# 5. TOURISM ANALYTICS APIs
# ==========================================================

@app.get(
    "/analytics/overview",
    tags=["Tourism Analytics"],
    summary="Tourism Overview"
)
def tourism_overview():
    latest_year = int(tourism_df["year"].max())

    latest_data = tourism_df[
        tourism_df["year"] == latest_year
    ]

    return {
        "total_records": len(tourism_df),
        "total_entities": int(tourism_df["entity"].nunique()),
        "total_countries": int(
            tourism_df.loc[
                tourism_df["code"].notna(),
                "code"
            ].nunique()
        ),
        "available_years": {
            "first": int(tourism_df["year"].min()),
            "latest": latest_year
        },
        "latest_year_records": len(latest_data),
        "latest_year_arrivals_sum": float(
            latest_data[
                "in_tour_arrivals_trips_total_overnight_vis_tourists"
            ].sum()
        )
    }


@app.get(
    "/analytics/countries",
    tags=["Tourism Analytics"],
    summary="Country Tourism Statistics"
)
def country_tourism(
    year: int | None = Query(None, ge=1900, le=2100),
    limit: int = Query(20, ge=1, le=200)
):
    data = tourism_df[
        tourism_df["code"].notna()
    ].copy()

    if year is not None:
        data = data[data["year"] == year]

        if data.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No country tourism data found for year {year}"
            )
    else:
        data = (
            data.sort_values("year")
            .groupby("code", as_index=False)
            .tail(1)
        )

    data = data.sort_values(
        "in_tour_arrivals_trips_total_overnight_vis_tourists",
        ascending=False
    ).head(limit)

    return {
        "year": (
            year if year is not None
            else int(data["year"].max()) if not data.empty
            else None
        ),
        "returned": len(data),
        "countries": dataframe_to_records(data)
    }


@app.get(
    "/analytics/regions",
    tags=["Tourism Analytics"],
    summary="Regional Tourism Statistics"
)
def region_tourism(
    year: int | None = Query(None, ge=1900, le=2100)
):
    data = tourism_df[
        tourism_df["owid_region"].notna()
    ].copy()

    if year is not None:
        data = data[data["year"] == year]

        if data.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No regional tourism data found for year {year}"
            )

    region_data = (
        data.groupby("owid_region")
        .agg(
            total_arrivals=(
                "in_tour_arrivals_trips_total_overnight_vis_tourists",
                "sum"
            ),
            entity_records=("entity", "count")
        )
        .reset_index()
        .sort_values("total_arrivals", ascending=False)
    )

    return {
        "year": year,
        "regions": dataframe_to_records(region_data)
    }


@app.get(
    "/analytics/yearly",
    tags=["Tourism Analytics"],
    summary="Yearly Tourism Trends"
)
def yearly_tourism():
    yearly_data = (
        tourism_df.groupby("year")
        .agg(
            total_recorded_arrivals=(
                "in_tour_arrivals_trips_total_overnight_vis_tourists",
                "sum"
            ),
            entity_records=("entity", "count")
        )
        .reset_index()
        .sort_values("year")
    )

    return {
        "total_years": len(yearly_data),
        "yearly_statistics": dataframe_to_records(yearly_data)
    }


# ==========================================================
# 6. SENTIMENT ANALYSIS APIs
# ==========================================================

class SentimentRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Tourist review text"
    )


@app.post(
    "/sentiment/predict",
    tags=["Sentiment Analysis"],
    summary="Predict Review Sentiment"
)
def predict_sentiment(request: SentimentRequest):
    review_text = request.text.strip()

    if not review_text:
        raise HTTPException(
            status_code=422,
            detail="Review text cannot be empty"
        )

    model = get_sentiment_model()

    try:
        prediction = model.predict([review_text])[0]

        result = {
            "text": review_text,
            "sentiment": str(prediction)
        }

        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba([review_text])[0]

            result["confidence"] = round(
                float(np.max(probabilities)),
                4
            )

        return result

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Sentiment prediction failed: {error}"
        )


@app.get(
    "/sentiment/statistics",
    tags=["Sentiment Analysis"],
    summary="Sentiment Statistics"
)
def sentiment_statistics():
    data = get_reviews()

    counts = data["sentiment"].value_counts().to_dict()

    return {
        "total_reviews": len(data),
        "sentiment_counts": {
            str(label): int(count)
            for label, count in counts.items()
        }
    }


@app.get(
    "/sentiment/distribution",
    tags=["Sentiment Analysis"],
    summary="Sentiment Distribution"
)
def sentiment_distribution():
    data = get_reviews()

    counts = data["sentiment"].value_counts()
    total = int(counts.sum())

    distribution = []

    for label, count in counts.items():
        distribution.append({
            "sentiment": str(label),
            "count": int(count),
            "percentage": round(
                int(count) / total * 100,
                2
            ) if total else 0
        })

    return {
        "total_reviews": total,
        "distribution": distribution
    }


# ==========================================================
# 7. NEARBY DESTINATION RECOMMENDATIONS
# ==========================================================

@app.get(
    "/recommendations/nearby",
    tags=["Recommendations"],
    summary="Find Nearby Destinations"
)
def nearby_recommendations(
    place_name: str = Query(..., min_length=1, max_length=150),
    top_n: int = Query(5, ge=1, le=50)
):
    search_name = place_name.strip()

    if not search_name:
        raise HTTPException(
            status_code=422,
            detail="Place name cannot be empty"
        )

    data = destinations_df.copy()

    # Find the selected city first
    city_matches = data[
        data["city_en"]
        .fillna("")
        .astype(str)
        .str.lower()
        == search_name.lower()
    ]

    if not city_matches.empty:
        origin = city_matches.iloc[0]

    else:
        # Otherwise, find an exact destination name
        name_matches = data[
            data["name_en"]
            .fillna("")
            .astype(str)
            .str.lower()
            == search_name.lower()
        ]

        if name_matches.empty:
            raise HTTPException(
                status_code=404,
                detail=f"Destination not found: {search_name}"
            )

        origin = name_matches.iloc[0]

    origin_lat = pd.to_numeric(
        origin["latitude"],
        errors="coerce"
    )

    origin_lon = pd.to_numeric(
        origin["longitude"],
        errors="coerce"
    )

    if pd.isna(origin_lat) or pd.isna(origin_lon):
        raise HTTPException(
            status_code=400,
            detail="Selected destination has invalid coordinates"
        )

    # Convert coordinates to numeric
    data["latitude"] = pd.to_numeric(
        data["latitude"],
        errors="coerce"
    )

    data["longitude"] = pd.to_numeric(
        data["longitude"],
        errors="coerce"
    )

    data = data.dropna(
        subset=["latitude", "longitude"]
    ).copy()

    # Haversine distance calculation
    earth_radius = 6371

    lat1 = math.radians(float(origin_lat))
    lon1 = math.radians(float(origin_lon))

    lat2 = np.radians(data["latitude"].to_numpy())
    lon2 = np.radians(data["longitude"].to_numpy())

    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    a = (
        np.sin(delta_lat / 2) ** 2
        + math.cos(lat1)
        * np.cos(lat2)
        * np.sin(delta_lon / 2) ** 2
    )

    a = np.clip(a, 0, 1)

    data["distance_km"] = (
        2 * earth_radius * np.arcsin(np.sqrt(a))
    )

    # Exclude the selected destination itself
    data = data.drop(index=origin.name, errors="ignore")

    recommendations = (
        data.sort_values("distance_km")
        .head(top_n)
        .copy()
    )

    recommendations["distance_km"] = (
        recommendations["distance_km"].round(2)
    )

    return {
        "place_name": search_name,
        "total_recommendations": len(recommendations),
        "recommendations": dataframe_to_records(recommendations)
    }


# ==========================================================
# 8. STARTUP INFORMATION
# ==========================================================

@app.on_event("startup")
def startup_event():
    print("=" * 55)
    print("AI TRAVEL AND TOURISM INTELLIGENCE API")
    print("=" * 55)
    print("API Status: Ready")
    print("Destinations:", len(destinations_df))
    print("Tourism Records:", len(tourism_df))
    print("Documentation: http://127.0.0.1:8000/docs")
    print("=" * 55)
