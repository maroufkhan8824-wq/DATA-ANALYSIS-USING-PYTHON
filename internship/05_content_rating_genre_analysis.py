
# Task 5: Netflix Content Rating & Genre Analysis
# Libraries: Pandas, Plotly

import pandas as pd
import plotly.express as px
from pathlib import Path

# Step 1: Load the cleaned dataset
df = pd.read_csv("Netflix_Cleaned.csv")

# Clean text columns
for col in ["type", "rating", "listed_in"]:
    if col in df.columns:
        df[col] = df[col].astype("string").str.strip()

# Handle missing values for analysis
df["rating"] = df["rating"].replace("", pd.NA).fillna("Unknown")
df["listed_in"] = df["listed_in"].replace("", pd.NA).fillna("Unknown")
df["type"] = df["type"].fillna("Unknown").str.title()

# Output folder
output_dir = Path("Netflix_Analysis_Output")
output_dir.mkdir(exist_ok=True)

# Step 2: Analyze rating categories
rating_counts = (
    df.groupby("rating")["show_id"]
    .nunique()
    .sort_values(ascending=False)
    .reset_index(name="Total_Titles")
)

rating_counts.to_csv(
    output_dir / "Netflix_Rating_Analysis.csv", index=False
)

print("\nCONTENT RATING ANALYSIS")
print(rating_counts.to_string(index=False))

# Step 3: Identify the most common genres
# Each title may belong to multiple genres
genre_df = df[["show_id", "type", "listed_in"]].copy()

genre_df["Genre"] = genre_df["listed_in"].str.split(",")
genre_df = genre_df.explode("Genre")
genre_df["Genre"] = genre_df["Genre"].str.strip()

genre_df = genre_df[
    genre_df["Genre"].notna()
    & (genre_df["Genre"] != "")
    & (genre_df["Genre"] != "Unknown")
]

genre_df = genre_df.drop_duplicates(
    subset=["show_id", "Genre"]
)

genre_counts = (
    genre_df.groupby("Genre")["show_id"]
    .nunique()
    .sort_values(ascending=False)
    .reset_index(name="Total_Titles")
)

top_genres = genre_counts.head(15)

genre_counts.to_csv(
    output_dir / "Netflix_Genre_Analysis.csv", index=False
)

print("\nTOP 15 GENRES")
print(top_genres.to_string(index=False))

# Step 4: Compare ratings across content types
rating_type = (
    df.groupby(["rating", "type"])["show_id"]
    .nunique()
    .reset_index(name="Total_Titles")
)

rating_type.to_csv(
    output_dir / "Netflix_Rating_by_Type.csv", index=False
)

# Prepare data for interactive charts
rating_chart = px.bar(
    rating_counts,
    x="rating",
    y="Total_Titles",
    title="Netflix Content by Rating",
    labels={
        "rating": "Content Rating",
        "Total_Titles": "Number of Titles"
    },
    color="rating",
    hover_data=["Total_Titles"]
)

genre_chart = px.bar(
    top_genres.sort_values("Total_Titles"),
    x="Total_Titles",
    y="Genre",
    orientation="h",
    title="Top 15 Netflix Genres",
    labels={
        "Genre": "Genre",
        "Total_Titles": "Number of Titles"
    },
    hover_data=["Total_Titles"]
)

type_chart = px.bar(
    rating_type,
    x="rating",
    y="Total_Titles",
    color="type",
    barmode="group",
    title="Content Ratings: Movies vs TV Shows",
    labels={
        "rating": "Content Rating",
        "Total_Titles": "Number of Titles",
        "type": "Content Type"
    },
    hover_data=["Total_Titles"]
)

# Step 5: Create an interactive dashboard with a content-type filter
dashboard_data = df[
    ["show_id", "title", "type", "rating", "listed_in"]
].copy()

dashboard_data["rating"] = dashboard_data["rating"].replace(
    "Unknown", "Not Specified"
)
dashboard_data["listed_in"] = dashboard_data["listed_in"].replace(
    "Unknown", "Not Specified"
)

dashboard = px.histogram(
    dashboard_data,
    x="rating",
    color="type",
    barmode="group",
    title="Interactive Netflix Rating Dashboard",
    labels={
        "rating": "Content Rating",
        "count": "Number of Titles",
        "type": "Content Type"
    },
    category_orders={
        "rating": sorted(dashboard_data["rating"].unique())
    },
    hover_data=["title"]
)

dashboard.update_layout(
    xaxis_tickangle=-45,
    legend_title_text="Content Type",
    template="plotly_white"
)

# Save interactive HTML charts
rating_chart.write_html(
    output_dir / "rating_analysis.html"
)
genre_chart.write_html(
    output_dir / "genre_analysis.html"
)
type_chart.write_html(
    output_dir / "rating_by_content_type.html"
)
dashboard.write_html(
    output_dir / "interactive_dashboard.html"
)

# Step 6: Generate audience insights
print("\nAUDIENCE INSIGHTS")
print("=" * 40)

if not rating_counts.empty:
    print(
        "Most common rating:",
        rating_counts.iloc[0]["rating"]
    )
    print(
        "Titles in this rating:",
        int(rating_counts.iloc[0]["Total_Titles"])
    )

if not genre_counts.empty:
    print("Most common genre:", genre_counts.iloc[0]["Genre"])
    print(
        "Titles in this genre:",
        int(genre_counts.iloc[0]["Total_Titles"])
    )

print("\nRating distribution by content type:")
print(rating_type.to_string(index=False))

print("\nAnalysis completed successfully!")
print("Open interactive_dashboard.html in a web browser.")
print("All reports and charts are saved in:", output_dir)
