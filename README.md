# 🌍 AI-Powered Travel and Tourism Intelligence Platform

An intelligent travel and tourism platform designed to help users explore destinations, discover attractions, analyze tourism information, and plan personalized trips using data science and machine learning.

## 🚀 Project Overview

The AI-Powered Travel and Tourism Intelligence Platform combines data analytics, machine learning, and web technologies to provide useful travel insights and recommendations.

The platform uses destination datasets, tourism statistics, and tourist reviews to support travel planning and destination discovery.

## ✨ Key Features

- **Destination Discovery:** Explore destinations across different countries.
- **Attraction Recommendations:** Discover nearby tourist attractions.
- **AI Travel Itinerary Planner:** Generate day-by-day travel itineraries.
- **Budget Planning:** Support travel budget estimation.
- **Food Recommendations:** Explore food-related travel information.
- **Sentiment Analysis:** Analyze tourist reviews and identify positive, negative, and neutral opinions.
- **Tourism Analytics:** Explore tourism statistics and trends.
- **Machine Learning:** Apply clustering and predictive models to travel-related data.
- **Interactive Dashboard:** Access project features through a Streamlit interface.
- **REST API:** Connect application services using FastAPI.

## 🛠️ Technologies Used

| Category | Technologies |
|---|---|
| Programming | Python |
| Data Analysis | Pandas, NumPy |
| Machine Learning | Scikit-learn |
| Data Visualization | Matplotlib, Seaborn |
| Frontend | Streamlit |
| Backend | FastAPI |
| API Server | Uvicorn |
| Model Tracking | MLflow |
| API Communication | Requests |
| Deployment | Docker, Docker Compose |
| Version Control | Git, GitHub |

## 📂 Project Structure

```text
AI_Powered_Travel_and_Tourism_Intelligence/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── models/
├── services/
│
├── app.py
├── api.py
├── api_client.py
│
├── attraction_service.py
├── budget_service.py
├── destination_service.py
├── food_service.py
│
├── mlflow_sentiment.py
├── mlflow_tracking.py
│
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
│
├── requirements.txt
├── requirements-docker.txt
│
├── README.md
└── .gitignore
```

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/jesuraju07/AI-Powered-Travel-Tourism-Intelligence.git
```

### 2. Open the Project Folder

```bash
cd AI-Powered-Travel-Tourism-Intelligence
```

### 3. Create a Virtual Environment

```bash
python -m venv .venv
```

### 4. Activate the Environment

**Windows PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

## ▶️ Run the Application Locally

### Start the FastAPI Backend

Open a terminal and run:

```bash
uvicorn api:app --reload --host 127.0.0.1 --port 8000
```

API documentation:

http://127.0.0.1:8000/docs

### Start the Streamlit Frontend

Open another terminal and run:

```bash
streamlit run app.py
```

The application will be available at:

http://localhost:8501

## 🐳 Run with Docker

Make sure Docker Desktop is running.

Build and start the containers:

```bash
docker compose up -d --build
```

Check running containers:

```bash
docker compose ps
```

Access the applications:

- **Streamlit:** http://localhost:8501
- **FastAPI:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

Stop the containers:

```bash
docker compose down
```

## 📊 Datasets

The project uses travel-related datasets, including:

- Destination information
- Tourism statistics
- Tourist reviews

Raw datasets are stored in the `data/raw/` directory, with processed datasets stored in `data/processed/`.

## 🎯 Project Objective

The main objective is to develop an intelligent travel platform that combines data science, machine learning, and web application technologies to make travel discovery and planning more informative and accessible.

## 👨‍💻 Developer

**JESU RAJU A**

GitHub: [jesuraju07](https://github.com/jesuraju07)

Project Repository: [AI-Powered Travel and Tourism Intelligence](https://github.com/jesuraju07/AI-Powered-Travel-Tourism-Intelligence)

---

⭐ If you find this project interesting, consider giving the repository a star!
