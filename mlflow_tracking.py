
import mlflow
from datetime import datetime

# --------------------------------
# 1. Connect to MLflow server
# --------------------------------

mlflow.set_tracking_uri("http://127.0.0.1:5000")

print("MLflow Tracking URI:", mlflow.get_tracking_uri())


# --------------------------------
# 2. Create or select experiment
# --------------------------------

experiment_name = "Travel_Intelligence"

mlflow.set_experiment(experiment_name)

experiment = mlflow.get_experiment_by_name(experiment_name)

print("Experiment Name:", experiment.name)
print("Experiment ID:", experiment.experiment_id)


# --------------------------------
# 3. Start a new MLflow run
# --------------------------------

with mlflow.start_run(
    run_name="Sentiment_Analysis_Test"
):

    # Model parameters
    mlflow.log_param("model", "Logistic Regression")
    mlflow.log_param("dataset", "Tourist Reviews")
    mlflow.log_param("task", "Sentiment Analysis")
    mlflow.log_param("algorithm", "TF-IDF")

    # Sample metrics for testing MLflow
    mlflow.log_metric("accuracy", 0.89)
    mlflow.log_metric("precision", 0.87)
    mlflow.log_metric("recall", 0.85)
    mlflow.log_metric("f1_score", 0.86)

    # Add experiment tags
    mlflow.set_tag("project", "AI Travel Intelligence")
    mlflow.set_tag("model_type", "Classification")

    # Get run information
    run_id = mlflow.active_run().info.run_id

    print("\nRun logged successfully!")
    print("Run ID:", run_id)


# --------------------------------
# 4. Completion
# --------------------------------

print("\n------------------------------")
print("MLFLOW TRACKING COMPLETED")
print("------------------------------")
print("Experiment:", experiment_name)
print("Check your MLflow dashboard!")
