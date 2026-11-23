
import pandas as pd
import os

file_path = "data/processed/travel_packages.csv"

print("Checking:", os.path.abspath(file_path))

if os.path.exists(file_path):

    packages = pd.read_csv(file_path)

    print("\nTRAVEL PACKAGES DATASET")
    print("=" * 50)

    print("Dataset Shape:", packages.shape)

    print("\nColumns:")
    print(packages.columns.tolist())

    print("\nPackage Details:")
    print(packages[
        ["package_name", "destination", "country", "price_inr"]
    ])

    print("\nMissing Values:")
    print(packages.isnull().sum())

    print("\nDuplicate Rows:", packages.duplicated().sum())

    print("\nAverage Package Price:")
    print(packages["price_inr"].mean())

    print("\nSUCCESS: Dataset loaded!")

else:
    print("ERROR: CSV file not found!")
