
# Task 3: Country-Wise Netflix Content Analysis

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Step 1: Load the cleaned dataset
df = pd.read_csv("Netflix_Cleaned.csv")

# Clean country information
df["country"] = df["country"].fillna("").astype(str).str.strip()

# Split multiple countries and create one row per country-title pair
country_df = df[df["country"] != ""].copy()

country_df["country"] = country_df["country"].str.split(",")

country_df = country_df.explode("country")

country_df["country"] = country_df["country"].str.strip()

# Remove blank country names and duplicate title-country pairs
country_df = country_df[country_df["country"] != ""]
country_df = country_df.drop_duplicates(
    subset=["show_id", "country"]
)

# Step 2: Calculate content count by country
country_counts = (
    country_df.groupby("country")["show_id"]
    .nunique()
    .sort_values(ascending=False)
)

# Step 3: Identify top 10 countries
top_10 = country_counts.head(10)

print("\nCOUNTRY-WISE NETFLIX CONTENT ANALYSIS")
print("=" * 45)
print("\nTop 10 Countries by Content Count:\n")
print(top_10.to_string())

# Create ranking report
ranking = top_10.reset_index()
ranking.columns = ["Country", "Content_Count"]
ranking.insert(0, "Rank", range(1, len(ranking) + 1))

ranking.to_csv("Netflix_Country_Ranking.csv", index=False)

# Step 4: Create charts
sns.set_theme(style="whitegrid")

fig, axes = plt.subplots(1, 2, figsize=(16, 7))

# Chart 1: Top 10 countries
sns.barplot(
    data=ranking,
    x="Content_Count",
    y="Country",
    hue="Country",
    palette="Reds_r",
    legend=False,
    ax=axes[0]
)

axes[0].set_title("Top 10 Countries by Netflix Content")
axes[0].set_xlabel("Number of Titles")
axes[0].set_ylabel("Country")

# Add count labels
for container in axes[0].containers:
    axes[0].bar_label(container, padding=3)

# Chart 2: Movie vs TV Show by country
top_countries = top_10.index.tolist()

type_counts = (
    country_df[country_df["country"].isin(top_countries)]
    .groupby(["country", "type"])["show_id"]
    .nunique()
    .reset_index(name="Count")
)

sns.barplot(
    data=type_counts,
    x="Count",
    y="country",
    hue="type",
    order=top_countries,
    ax=axes[1]
)

axes[1].set_title("Movies vs TV Shows by Country")
axes[1].set_xlabel("Number of Titles")
axes[1].set_ylabel("Country")
axes[1].legend(title="Content Type")

plt.suptitle(
    "Netflix Country-Wise Content Analysis",
    fontsize=16,
    fontweight="bold"
)

plt.tight_layout()

# Save dashboard
plt.savefig("Netflix_Country_Dashboard.png", dpi=300,
            bbox_inches="tight")
plt.show()

# Step 5: Generate business insights
total_countries = country_df["country"].nunique()
total_country_entries = country_counts.sum()

print("\nBUSINESS INSIGHTS")
print("=" * 45)
print("Countries represented:", total_countries)
print("Total country-title associations:", total_country_entries)

if not country_counts.empty:
    print("Top content-producing country:", country_counts.index[0])
    print("Number of titles in top country:", country_counts.iloc[0])

    top_share = country_counts.iloc[0] / total_country_entries * 100
    print(f"Top country's share of country-title entries: {top_share:.2f}%")

    print("\nTop 5 Countries:")
    print(country_counts.head(5).to_string())

print("\nFiles created:")
print("1. Netflix_Country_Ranking.csv")
print("2. Netflix_Country_Dashboard.png")
