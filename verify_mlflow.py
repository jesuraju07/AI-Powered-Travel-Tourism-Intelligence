
import mlflow
import mlflow.sklearn
import joblib
import os

from mlflow.tracking import MlflowClient


# ==========================================
# 1. CONNECT TO MLFLOW
# ==========================================

print("\n" + "=" * 55)
print("       MLFLOW SYSTEM VERIFICATION")
print("=" * 55)

tracking_uri = "http://127.0.0.1:5000"

mlflow.set_tracking_uri(tracking_uri)

client = MlflowClient(tracking_uri=tracking_uri)

try:
    experiment = client.get_experiment_by_name(
        "Travel_Intelligence"
    )

    if experiment is None:
        raise Exception("Experiment not found")

    print("\n[PASS] MLflow server connection")
    print("[PASS] Experiment found:", experiment.name)

except Exception as e:
    print("\n[FAIL] MLflow connection:", e)
    raise SystemExit(1)


# ==========================================
# 2. CHECK EXPERIMENT RUNS
# ==========================================

runs = client.search_runs(
    experiment_ids=[experiment.experiment_id],
    order_by=["attributes.start_time DESC"]
)

print("\nTotal MLflow Runs:", len(runs))

if len(runs) == 0:
    print("[FAIL] No runs found")
    raise SystemExit(1)

print("[PASS] Experiment runs available")

for run in runs:
    print(
        "Run Name:",
        run.data.tags.get("mlflow.runName", "Unnamed")
    )


# ==========================================
# 3. FIND ACTUAL SENTIMENT MODEL RUN
# ==========================================

sentiment_runs = [
    run for run in runs
    if run.data.tags.get("mlflow.runName")
    == "Actual_Sentiment_Analysis"
]

if not sentiment_runs:
    print("\n[FAIL] Actual sentiment run not found")
    raise SystemExit(1)

run = sentiment_runs[0]
run_id = run.info.run_id

print("\n[PASS] Sentiment model run found")
print("Run ID:", run_id)


# ==========================================
# 4. CHECK PARAMETERS
# ==========================================

print("\nPARAMETER VERIFICATION")

required_params = [
    "model",
    "vectorizer",
    "max_features",
    "max_iter"
]

for param in required_params:

    if param in run.data.params:
        print(
            "[PASS]",
            param,
            "=",
            run.data.params[param]
        )
    else:
        print("[FAIL] Missing parameter:", param)


# ==========================================
# 5. CHECK METRICS
# ==========================================

print("\nMETRIC VERIFICATION")

required_metrics = [
    "accuracy",
    "precision",
    "recall",
    "f1_score"
]

for metric in required_metrics:

    if metric in run.data.metrics:
        print(
            "[PASS]",
            metric,
            "=",
            round(run.data.metrics[metric], 4)
        )
    else:
        print("[FAIL] Missing metric:", metric)


# ==========================================
# 6. CHECK MODEL ARTIFACT
# ==========================================

print("\nMODEL ARTIFACT VERIFICATION")


# MODEL ARTIFACT VERIFICATION

print("\nMODEL ARTIFACT VERIFICATION")

artifacts = client.list_artifacts(run_id)

artifact_names = [artifact.path for artifact in artifacts]

print("Available artifacts:", artifact_names)

# Check if the confusion matrix exists
if "confusion_matrix.png" in artifact_names:
    print("[PASS] Confusion matrix found")
else:
    print("[FAIL] Confusion matrix missing")

# Check if the model can be loaded from MLflow
try:
    loaded_model = mlflow.sklearn.load_model(
        f"runs:/{run_id}/sentiment_model"
    )

    print("[PASS] Sentiment model loaded from MLflow")

except Exception as e:
    print("[FAIL] Could not load sentiment model:", e)


# ==========================================
# 7. LOAD MODEL FROM MLFLOW
# ==========================================

print("\nMODEL LOADING TEST")

try:

    model_uri = f"runs:/{run_id}/sentiment_model"

    loaded_model = mlflow.sklearn.load_model(
        model_uri
    )

    print("[PASS] Model loaded from MLflow")

    sample_review = [
        "The hotel was beautiful and the service was excellent"
    ]

    prediction = loaded_model.predict(sample_review)

    print("Sample Review:", sample_review[0])
    print("Predicted Sentiment:", prediction[0])

    print("[PASS] Prediction successful")

except Exception as e:

    print("[FAIL] Model loading or prediction failed:", e)


# ==========================================
# 8. CHECK LOCAL MODEL
# ==========================================

print("\nLOCAL MODEL VERIFICATION")

local_model_path = "models/sentiment_pipeline.pkl"

if os.path.exists(local_model_path):

    local_model = joblib.load(local_model_path)

    print("[PASS] Local model file found")

    local_prediction = local_model.predict([
        "Amazing hotel with wonderful service"
    ])

    print("Local Prediction:", local_prediction[0])

else:

    print("[FAIL] Local model file missing")


# ==========================================
# FINAL REPORT
# ==========================================

print("\n" + "=" * 55)
print("       MLFLOW VERIFICATION COMPLETED")
print("=" * 55)
