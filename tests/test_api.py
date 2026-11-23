
from fastapi.testclient import TestClient
from api import app

client = TestClient(app)


# 1. HOME ENDPOINT
def test_home_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


# 2. HEALTH ENDPOINT
def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


# 3. PROJECT ENDPOINT
def test_project_endpoint():
    response = client.get("/project")
    assert response.status_code == 200
    assert "project" in response.json()
    assert "features" in response.json()


# 4. DESTINATIONS ENDPOINT
def test_destinations_endpoint():
    response = client.get("/destinations")
    assert response.status_code == 200

    data = response.json()

    assert "destinations" in data
    assert "total_destinations" in data
    assert len(data["destinations"]) > 0


# 5. DESTINATION SEARCH
def test_destination_search():
    response = client.get(
        "/destinations/search",
        params={"q": "Paris"}
    )

    assert response.status_code == 200

    data = response.json()

    assert "destinations" in data
    assert "total_results" in data


# 6. COUNTRIES ENDPOINT
def test_countries_endpoint():
    response = client.get("/destinations/countries")

    assert response.status_code == 200
    assert "countries" in response.json()


# 7. CATEGORIES ENDPOINT
def test_categories_endpoint():
    response = client.get("/destinations/categories")

    assert response.status_code == 200
    assert "categories" in response.json()


# 8. TOURISM OVERVIEW
def test_tourism_overview():
    response = client.get("/analytics/overview")

    assert response.status_code == 200
    assert "total_records" in response.json()


# 9. YEARLY ANALYTICS
def test_yearly_analytics():
    response = client.get("/analytics/yearly")

    assert response.status_code == 200
    assert "yearly_statistics" in response.json()


# 10. SENTIMENT PREDICTION
def test_sentiment_prediction():
    response = client.post(
        "/sentiment/predict",
        json={
            "text": "The hotel was wonderful and the staff were friendly."
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "sentiment" in data
    assert data["sentiment"] in [
        "Positive",
        "Negative",
        "Neutral"
    ]


# 11. SENTIMENT STATISTICS
def test_sentiment_statistics():
    response = client.get("/sentiment/statistics")

    assert response.status_code == 200
    assert "total_reviews" in response.json()
    assert "sentiment_counts" in response.json()


# 12. SENTIMENT DISTRIBUTION
def test_sentiment_distribution():
    response = client.get("/sentiment/distribution")

    assert response.status_code == 200
    assert "distribution" in response.json()


# 13. NEARBY RECOMMENDATIONS
def test_nearby_recommendations():
    response = client.get(
        "/recommendations/nearby",
        params={
            "place_name": "Paris",
            "top_n": 5
        }
    )

    assert response.status_code == 200
    assert "recommendations" in response.json()


# 14. INVALID SENTIMENT REQUEST
def test_invalid_sentiment_request():
    response = client.post(
        "/sentiment/predict",
        json={"text": ""}
    )

    assert response.status_code == 422


# 15. UNKNOWN ENDPOINT
def test_unknown_endpoint():
    response = client.get("/this-endpoint-does-not-exist")

    assert response.status_code == 404
    
