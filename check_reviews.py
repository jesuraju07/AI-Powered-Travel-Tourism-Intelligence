
import pandas as pd
import numpy as np

# ==========================================
# 1. LOAD CLEANED TOURIST REVIEWS DATASET
# ==========================================

file_path = "data/processed/cleaned_tourist_reviews.csv"

reviews = pd.read_csv(file_path)

print("=" * 60)
print("TOURIST REVIEWS DATASET CHECK")
print("=" * 60)


# ==========================================
# 2. DATASET INFORMATION
# ==========================================

print("\n1. DATASET SHAPE")
print("Rows and Columns:", reviews.shape)

print("\n2. COLUMN NAMES")
print(reviews.columns.tolist())

print("\n3. FIRST 5 RECORDS")
print(reviews.head())


# ==========================================
# 3. DATA TYPES
# ==========================================

print("\n4. DATA TYPES")
print(reviews.dtypes)


# ==========================================
# 4. MISSING VALUES
# ==========================================

print("\n5. MISSING VALUES")
print(reviews.isnull().sum())

print("\nTotal Missing Values:",
      reviews.isnull().sum().sum())


# ==========================================
# 5. DUPLICATE RECORDS
# ==========================================

print("\n6. DUPLICATE RECORDS")
print("Duplicate Rows:", reviews.duplicated().sum())


# ==========================================
# 6. SENTIMENT DISTRIBUTION
# ==========================================

print("\n7. SENTIMENT DISTRIBUTION")

if "sentiment" in reviews.columns:

    print(reviews["sentiment"].value_counts())

    print("\nSentiment Percentage:")
    print(
        (reviews["sentiment"].value_counts(normalize=True) * 100)
        .round(2)
    )

else:
    print("Sentiment column not found!")


# ==========================================
# 7. RATING DISTRIBUTION
# ==========================================

print("\n8. RATING DISTRIBUTION")

if "rating" in reviews.columns:
    print(reviews["rating"].value_counts().sort_index())

else:
    print("Rating column not found!")


# ==========================================
# 8. TEXT DATA CHECK
# ==========================================

print("\n9. TEXT DATA CHECK")

if "text" in reviews.columns:

    print("Empty Reviews:",
          reviews["text"].isna().sum())

    print("Unique Reviews:",
          reviews["text"].nunique())

    print("\nSample Review:")
    print(reviews["text"].iloc[0])

else:
    print("Text column not found!")


# ==========================================
# 9. FINAL DATASET VALIDATION
# ==========================================

required_columns = ["text", "sentiment"]

missing_columns = [
    col for col in required_columns
    if col not in reviews.columns
]

print("\n10. FINAL VALIDATION")

if not missing_columns and reviews.shape[0] > 0:
    print("Dataset loaded successfully!")
    print("Required columns are available.")
    print("Ready for Sentiment Analysis ML training.")

else:
    print("Dataset validation failed.")
    print("Missing columns:", missing_columns)


print("\n" + "=" * 60)
print("DATASET CHECK COMPLETED")
print("=" * 60)
