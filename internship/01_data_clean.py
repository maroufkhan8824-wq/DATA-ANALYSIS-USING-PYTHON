
import pandas as pd

# Step 1: Import the dataset
df = pd.read_csv("Dataset.csv")

print("Original Dataset:")
print(df.head())

print("\nDataset Shape:", df.shape)

# Step 2: Identify missing values
print("\nMissing Values Before Cleaning:")
print(df.isnull().sum())

# Step 3: Clean column names and text formatting
df.columns = df.columns.str.strip()

for col in df.select_dtypes(include=["object", "string"]).columns:
    df[col] = df[col].astype("string").str.strip()
    df[col] = df[col].replace(r"^\s*$", pd.NA, regex=True)

# Step 4: Remove duplicate records
duplicates = df.duplicated().sum()
print("\nDuplicate Records:", duplicates)

df = df.drop_duplicates()

# Step 5: Standardize Type, Rating, and Country
if "type" in df.columns:
    df["type"] = df["type"].str.title()

if "rating" in df.columns:
    df["rating"] = df["rating"].str.upper()

if "country" in df.columns:
    df["country"] = df["country"].apply(
        lambda x: ", ".join(
            item.strip() for item in x.split(",")
            if item.strip()
        ) if pd.notna(x) else x
    )

# Step 6: Standardize date format
if "date_added" in df.columns:
    df["date_added"] = pd.to_datetime(
        df["date_added"], errors="coerce"
    )

# Step 7: Check missing values after cleaning
print("\nMissing Values After Cleaning:")
print(df.isnull().sum())

# Step 8: Export the cleaned dataset
df.to_csv("Netflix_Cleaned.csv", index=False)

print("\nFinal Dataset Shape:", df.shape)
print("Netflix dataset cleaned and saved successfully!")
