
import pandas as pd
import mlflow
import mlflow.sklearn
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)


# ==========================================
# 1. LOAD DATASET
# ==========================================

print("\nLoading Tourist Reviews Dataset...")

reviews = pd.read_csv(
    "data/processed/cleaned_tourist_reviews.csv"
)

reviews = reviews.dropna(subset=["text", "sentiment"])

X = reviews["text"].astype(str)
y = reviews["sentiment"].astype(str)

print("Dataset Shape:", reviews.shape)
print("Total Reviews:", len(reviews))
print("Sentiments:", y.unique())


# ==========================================
# 2. SPLIT DATASET
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\nTraining Samples:", len(X_train))
print("Testing Samples:", len(X_test))


# ==========================================
# 3. CREATE ML PIPELINE
# ==========================================

pipeline = Pipeline([

    (
        "tfidf",
        TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            stop_words="english"
        )
    ),

    (
        "classifier",
        LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=42
        )
    )

])


# ==========================================
# 4. CONFIGURE MLFLOW
# ==========================================

mlflow.set_tracking_uri(
    "http://127.0.0.1:5000"
)

mlflow.set_experiment(
    "Travel_Intelligence"
)


# ==========================================
# 5. TRAIN MODEL AND TRACK EXPERIMENT
# ==========================================

with mlflow.start_run(
    run_name="Actual_Sentiment_Analysis"
):

    print("\nTraining Logistic Regression Model...")

    pipeline.fit(X_train, y_train)

    print("Training Completed!")


    # ======================================
    # 6. PREDICTIONS
    # ======================================

    y_pred = pipeline.predict(X_test)


    # ======================================
    # 7. EVALUATION METRICS
    # ======================================

    accuracy = accuracy_score(y_test, y_pred)

    precision = precision_score(
        y_test,
        y_pred,
        average="weighted",
        zero_division=0
    )

    recall = recall_score(
        y_test,
        y_pred,
        average="weighted",
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        y_pred,
        average="weighted",
        zero_division=0
    )

    print("\nMODEL PERFORMANCE")
    print("----------------------------")

    print("Accuracy:", accuracy)
    print("Precision:", precision)
    print("Recall:", recall)
    print("F1 Score:", f1)

    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))


    # ======================================
    # 8. LOG PARAMETERS INTO MLFLOW
    # ======================================

    mlflow.log_param(
        "model",
        "Logistic Regression"
    )

    mlflow.log_param(
        "vectorizer",
        "TF-IDF"
    )

    mlflow.log_param(
        "max_features",
        5000
    )

    mlflow.log_param(
        "ngram_range",
        "(1, 2)"
    )

    mlflow.log_param(
        "max_iter",
        1000
    )

    mlflow.log_param(
        "test_size",
        0.20
    )

    mlflow.log_param(
        "training_samples",
        len(X_train)
    )


    # ======================================
    # 9. LOG METRICS INTO MLFLOW
    # ======================================

    mlflow.log_metric("accuracy", accuracy)
    mlflow.log_metric("precision", precision)
    mlflow.log_metric("recall", recall)
    mlflow.log_metric("f1_score", f1)


    # ======================================
    # 10. SAVE MODEL LOCALLY
    # ======================================

    os.makedirs("models", exist_ok=True)

    joblib.dump(
        pipeline,
        "models/sentiment_pipeline.pkl"
    )


    # ======================================
    # 11. LOG MODEL INTO MLFLOW
    # ======================================

    mlflow.sklearn.log_model(
        sk_model=pipeline,
        artifact_path="sentiment_model"
    )


    # ======================================
    # 12. LOG CONFUSION MATRIX
    # ======================================

    cm = confusion_matrix(
        y_test,
        y_pred,
        labels=pipeline.classes_
    )

    import matplotlib.pyplot as plt
    from sklearn.metrics import ConfusionMatrixDisplay

    display = ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=pipeline.classes_
    )

    display.plot(xticks_rotation=45)

    plt.tight_layout()

    plt.savefig(
        "models/confusion_matrix.png"
    )

    plt.close()

    mlflow.log_artifact(
        "models/confusion_matrix.png"
    )


    # ======================================
    # 13. COMPLETION
    # ======================================

    print("\nMLFLOW SENTIMENT TRAINING COMPLETED!")

    print("Run ID:", mlflow.active_run().info.run_id)

    print("Model saved: models/sentiment_pipeline.pkl")

    print("Model logged successfully in MLflow!")
