
import pandas as pd
import os

# Dataset folder
data_path = "data/raw"

# Dataset names
files = [
    "destinations.csv",
    "tourism_statistics.csv",
    "tourist_reviews.csv"
]

# Check each dataset
for file in files:

    file_path = os.path.join(data_path, file)

    print("\n" + "=" * 50)
    print("Dataset:", file)

    if os.path.exists(file_path):

        df = pd.read_csv(file_path, nrows=1000)

        print("Status: Available")
        print("Rows checked:", len(df))
        print("Columns:", df.shape[1])

        print("\nColumn Names:")
        print(df.columns.tolist())

        print("\nFirst 5 Records:")
        print(df.head())

        print("\nMissing Values:")
        print(df.isnull().sum())

    else:
        print("Status: File Not Found")

print("\nDataset Verification Completed!")
