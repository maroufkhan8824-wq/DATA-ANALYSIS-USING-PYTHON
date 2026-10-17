
# TASK 6: NETFLIX BUSINESS INSIGHTS REPORT
# Python + Pandas + Matplotlib + Seaborn + Plotly

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from pathlib import Path

# ==================================================
# STEP 1: LOAD DATASET AND PERFORM COMPLETE EDA
# ==================================================

INPUT_FILE = "Netflix_Cleaned.csv"
OUTPUT_DIR = Path("Netflix_Business_Report")
OUTPUT_DIR.mkdir(exist_ok=True)

df = pd.read_csv(INPUT_FILE)

# Clean column names
df.columns = df.columns.str.strip().str.lower()

# Check required columns
required_columns = [
    "show_id", "type", "title", "country",
    "release_year", "rating", "duration", "listed_in"
]

missing_columns = [
    col for col in required_columns if col not in df.columns
]

if missing_columns:
    raise ValueError(f"Missing required columns: {missing_columns}")

# Clean text fields
for col in df.select_dtypes(include=["object", "string"]).columns:
    df[col] = df[col].astype("string").str.strip()
    df[col] = df[col].replace(r"^\s*$", pd.NA, regex=True)

# Convert numeric/date columns
df["release_year"] = pd.to_numeric(
    df["release_year"], errors="coerce"
)

if "date_added" in df.columns:
    df["date_added"] = pd.to_datetime(
        df["date_added"], errors="coerce"
    )

# Standardize categories
df["type"] = df["type"].str.title()
df["rating"] = df["rating"].str.upper()

# Remove exact duplicate rows
original_rows = len(df)
df = df.drop_duplicates().copy()
duplicates_removed = original_rows - len(df)

# EDA summary
eda_summary = pd.DataFrame({
    "Metric": [
        "Total titles",
        "Total columns",
        "Duplicate rows removed",
        "Missing cells",
        "Unique titles",
        "Unique release years"
    ],
    "Value": [
        len(df),
        len(df.columns),
        duplicates_removed,
        int(df.isna().sum().sum()),
        df["show_id"].nunique(),
        df["release_year"].nunique()
    ]
})

eda_summary.to_csv(
    OUTPUT_DIR / "EDA_Summary.csv", index=False
)

df.isna().sum().rename("Missing_Values").to_csv(
    OUTPUT_DIR / "Missing_Values_Report.csv"
)

# ==================================================
# STEP 2: CONTENT TYPE ANALYSIS
# ==================================================

type_counts = (
    df.groupby("type")["show_id"]
    .nunique()
    .sort_values(ascending=False)
)

type_report = type_counts.reset_index()
type_report.columns = ["Content_Type", "Total_Titles"]
type_report["Percentage"] = (
    type_report["Total_Titles"] / df["show_id"].nunique() * 100
).round(2)

type_report.to_csv(
    OUTPUT_DIR / "Content_Type_Report.csv", index=False
)

# ==================================================
# STEP 3: COUNTRY-WISE CONTENT ANALYSIS
# ==================================================

country_df = df[["show_id", "country"]].dropna().copy()

country_df["country"] = country_df["country"].str.split(",")
country_df = country_df.explode("country")
country_df["country"] = country_df["country"].str.strip()

country_df = country_df[
    country_df["country"].notna()
    & (country_df["country"] != "")
]

country_df = country_df.drop_duplicates(
    subset=["show_id", "country"]
)

country_counts = (
    country_df.groupby("country")["show_id"]
    .nunique()
    .sort_values(ascending=False)
)

country_report = country_counts.head(15).reset_index()
country_report.columns = ["Country", "Total_Titles"]
country_report.insert(
    0, "Rank", range(1, len(country_report) + 1)
)

country_report.to_csv(
    OUTPUT_DIR / "Top_Countries_Report.csv", index=False
)

# ==================================================
# STEP 4: RELEASE YEAR TREND ANALYSIS
# ==================================================

year_df = df.dropna(subset=["release_year"]).copy()
year_df["release_year"] = year_df["release_year"].astype(int)

yearly = (
    year_df.groupby("release_year")["show_id"]
    .nunique()
    .sort_index()
    .reset_index(name="Total_Titles")
)

yearly["Year_Over_Year_Change"] = (
    yearly["Total_Titles"].diff()
)

yearly["Growth_Percentage"] = (
    yearly["Total_Titles"].pct_change() * 100
).round(2)

yearly.to_csv(
    OUTPUT_DIR / "Release_Year_Report.csv", index=False
)

peak_year = int(
    yearly.loc[yearly["Total_Titles"].idxmax(), "release_year"]
) if not yearly.empty else None

peak_year_count = int(
    yearly["Total_Titles"].max()
) if not yearly.empty else 0

# ==================================================
# STEP 5: RATING ANALYSIS
# ==================================================

rating_df = df.copy()
rating_df["rating"] = rating_df["rating"].fillna("Unknown")

rating_counts = (
    rating_df.groupby("rating")["show_id"]
    .nunique()
    .sort_values(ascending=False)
    .reset_index(name="Total_Titles")
)

rating_counts.to_csv(
    OUTPUT_DIR / "Rating_Report.csv", index=False
)

rating_by_type = (
    rating_df.groupby(["rating", "type"])["show_id"]
    .nunique()
    .reset_index(name="Total_Titles")
)

rating_by_type.to_csv(
    OUTPUT_DIR / "Rating_By_Type_Report.csv", index=False
)

# ==================================================
# STEP 6: GENRE ANALYSIS
# ==================================================

genre_df = df[["show_id", "listed_in"]].dropna().copy()

genre_df["listed_in"] = genre_df["listed_in"].str.split(",")
genre_df = genre_df.explode("listed_in")
genre_df["listed_in"] = genre_df["listed_in"].str.strip()

genre_df = genre_df[
    genre_df["listed_in"].notna()
    & (genre_df["listed_in"] != "")
]

genre_df = genre_df.drop_duplicates(
    subset=["show_id", "listed_in"]
)

genre_counts = (
    genre_df.groupby("listed_in")["show_id"]
    .nunique()
    .sort_values(ascending=False)
    .reset_index(name="Total_Titles")
)

genre_counts.columns = ["Genre", "Total_Titles"]

genre_counts.to_csv(
    OUTPUT_DIR / "Genre_Report.csv", index=False
)

top_genres = genre_counts.head(15)

# ==================================================
# STEP 7: BUILD INTERACTIVE DASHBOARDS
# ==================================================

sns.set_theme(style="whitegrid")

# Dashboard 1: Executive overview
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=(
        "Movies vs TV Shows",
        "Top 10 Countries",
        "Top 10 Genres",
        "Content Ratings"
    ),
    specs=[
        [{"type": "pie"}, {"type": "bar"}],
        [{"type": "bar"}, {"type": "bar"}]
    ]
)

fig.add_trace(
    go.Pie(
        labels=type_report["Content_Type"],
        values=type_report["Total_Titles"],
        hole=0.45,
        name="Content Type"
    ),
    row=1, col=1
)

top_countries_10 = country_counts.head(10).sort_values()

fig.add_trace(
    go.Bar(
        x=top_countries_10.values,
        y=top_countries_10.index,
        orientation="h",
        name="Countries"
    ),
    row=1, col=2
)

top_genres_10 = top_genres.head(10).sort_values("Total_Titles")

fig.add_trace(
    go.Bar(
        x=top_genres_10["Total_Titles"],
        y=top_genres_10["Genre"],
        orientation="h",
        name="Genres"
    ),
    row=2, col=1
)

fig.add_trace(
    go.Bar(
        x=rating_counts["rating"],
        y=rating_counts["Total_Titles"],
        name="Ratings"
    ),
    row=2, col=2
)

fig.update_layout(
    title="Netflix Business Intelligence Dashboard",
    height=900,
    template="plotly_white",
    showlegend=False
)

fig.write_html(
    OUTPUT_DIR / "Executive_Dashboard.html"
)

# Dashboard 2: Release year trends
trend_fig = px.line(
    yearly,
    x="release_year",
    y="Total_Titles",
    markers=True,
    title="Netflix Titles by Release Year",
    labels={
        "release_year": "Release Year",
        "Total_Titles": "Number of Titles"
    }
)

trend_fig.update_layout(template="plotly_white")

trend_fig.write_html(
    OUTPUT_DIR / "Release_Trend_Dashboard.html"
)

# Dashboard 3: Rating comparison
rating_fig = px.bar(
    rating_by_type,
    x="rating",
    y="Total_Titles",
    color="type",
    barmode="group",
    title="Ratings by Movies and TV Shows",
    labels={
        "rating": "Rating",
        "Total_Titles": "Number of Titles",
        "type": "Content Type"
    }
)

rating_fig.update_layout(template="plotly_white")

rating_fig.write_html(
    OUTPUT_DIR / "Rating_Comparison_Dashboard.html"
)

# Dashboard 4: Genre analysis
genre_fig = px.bar(
    top_genres.sort_values("Total_Titles"),
    x="Total_Titles",
    y="Genre",
    orientation="h",
    title="Top 15 Netflix Genres",
    labels={
        "Total_Titles": "Number of Titles",
        "Genre": "Genre"
    }
)

genre_fig.update_layout(template="plotly_white")

genre_fig.write_html(
    OUTPUT_DIR / "Genre_Dashboard.html"
)

# ==================================================
# STEP 8: GENERATE BUSINESS INSIGHTS
# ==================================================

total_titles = df["show_id"].nunique()

movie_count = int(
    df.loc[df["type"] == "Movie", "show_id"].nunique()
)

tv_count = int(
    df.loc[df["type"] == "Tv Show", "show_id"].nunique()
)

movie_percentage = (
    movie_count / total_titles * 100 if total_titles else 0
)

tv_percentage = (
    tv_count / total_titles * 100 if total_titles else 0
)

top_country = (
    country_counts.index[0] if not country_counts.empty else "N/A"
)

top_country_count = (
    int(country_counts.iloc[0]) if not country_counts.empty else 0
)

top_genre = (
    genre_counts.iloc[0]["Genre"] if not genre_counts.empty else "N/A"
)

top_genre_count = (
    int(genre_counts.iloc[0]["Total_Titles"])
    if not genre_counts.empty else 0
)

top_rating = (
    rating_counts.iloc[0]["rating"] if not rating_counts.empty else "N/A"
)

top_rating_count = (
    int(rating_counts.iloc[0]["Total_Titles"])
    if not rating_counts.empty else 0
)

# ==================================================
# STEP 9: EXECUTIVE REPORT
# ==================================================

report_path = OUTPUT_DIR / "Netflix_Executive_Report.txt"

with open(report_path, "w", encoding="utf-8") as report:

    report.write("NETFLIX BUSINESS INSIGHTS REPORT\n")
    report.write("=" * 45 + "\n\n")

    report.write("1. EXECUTIVE SUMMARY\n")
    report.write(
        f"The dataset contains {total_titles:,} unique titles.\n"
    )
    report.write(
        f"Movies: {movie_count:,} ({movie_percentage:.2f}%).\n"
    )
    report.write(
        f"TV Shows: {tv_count:,} ({tv_percentage:.2f}%).\n\n"
    )

    report.write("2. CONTENT TYPE INSIGHTS\n")
    if movie_count > tv_count:
        report.write(
            "Movies represent the larger share of the catalog.\n\n"
        )
    elif tv_count > movie_count:
        report.write(
            "TV Shows represent the larger share of the catalog.\n\n"
        )
    else:
        report.write("Movies and TV Shows have equal counts.\n\n")

    report.write("3. GEOGRAPHIC INSIGHTS\n")
    report.write(
        f"Leading country by title count: {top_country} "
        f"({top_country_count:,} titles).\n"
    )
    report.write(
        "Titles associated with multiple countries are counted "
        "once for each associated country.\n\n"
    )

    report.write("4. GENRE INSIGHTS\n")
    report.write(
        f"Most common listed genre: {top_genre} "
        f"({top_genre_count:,} titles).\n\n"
    )

    report.write("5. CONTENT RATING INSIGHTS\n")
    report.write(
        f"Most common rating category: {top_rating} "
        f"({top_rating_count:,} titles).\n\n"
    )

    report.write("6. RELEASE YEAR INSIGHTS\n")
    if peak_year is not None:
        report.write(
            f"Year with the highest title count: {peak_year} "
            f"({peak_year_count:,} titles).\n"
        )
    report.write(
        "Recent release years may be incomplete in the dataset.\n\n"
    )

    report.write("7. RECOMMENDATIONS\n")
    report.write(
        "- Monitor the Movies and TV Shows content mix.\n"
        "- Explore genre gaps in important markets.\n"
        "- Compare rating categories when planning audience segments.\n"
        "- Track release-year trends while accounting for incomplete years.\n"
        "- Use viewer engagement and subscription data before making "
        "investment decisions.\n\n"
    )

    report.write("8. DATA LIMITATIONS\n")
    report.write(
        "- This dataset describes catalog titles, not actual viewership.\n"
        "- Country and genre counts may overlap.\n"
        "- Ratings do not directly measure audience demand.\n"
        "- Missing values may affect individual analyses.\n"
    )

# ==================================================
# STEP 10: PRINT FINAL SUMMARY
# ==================================================

print("\n" + "=" * 50)
print("NETFLIX BUSINESS ANALYSIS COMPLETED")
print("=" * 50)

print("Total unique titles:", total_titles)
print(f"Movies: {movie_count} ({movie_percentage:.2f}%)")
print(f"TV Shows: {tv_count} ({tv_percentage:.2f}%)")
print("Top country:", top_country)
print("Top genre:", top_genre)
print("Most common rating:", top_rating)

print("\nOUTPUT FILES")
for file in sorted(OUTPUT_DIR.iterdir()):
    print(file)

print("\nOpen Executive_Dashboard.html in your browser.")
print("Executive report:", report_path)
