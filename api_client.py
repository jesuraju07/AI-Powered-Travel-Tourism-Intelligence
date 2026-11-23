
import requests

API_BASE_URL = "http://127.0.0.1:8000"


def check_api_connection():
    """Check whether FastAPI is running."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/health",
            timeout=10
        )

        response.raise_for_status()
        return response.json()

    except requests.RequestException as error:
        return {"error": str(error)}


def get_data(endpoint, params=None):
    """Fetch data from FastAPI."""
    try:
        response = requests.get(
            f"{API_BASE_URL}{endpoint}",
            params=params,
            timeout=30
        )

        response.raise_for_status()
        return response.json()

    except requests.RequestException as error:
        return {"error": str(error)}


def post_data(endpoint, payload):
    """Send data to FastAPI."""
    try:
        response = requests.post(
            f"{API_BASE_URL}{endpoint}",
            json=payload,
            timeout=30
        )

        response.raise_for_status()
        return response.json()

    except requests.RequestException as error:
        return {"error": str(error)}
