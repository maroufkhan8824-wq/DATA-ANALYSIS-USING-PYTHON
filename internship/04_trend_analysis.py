
# Task 4: Netflix Trend Analysis by Release Year

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Step 1: Load the cleaned dataset
df = pd.read_csv("Netflix_Cleaned.csv")

# Clean and organize release year
df["release_year"] = pd.to_numeric(
    df["release_year"], errors="coerce"
)

df = df.dropna(subset=["release_year"]).copy()
df["release_year"] = df["release_year"].astype(int)

# Count unique titles released each year
yearly_counts = (
    df.groupby("release_year")["show_id"]
    .nunique()
    .sort_index()
)

# Step 2: Calculate yearly content releases
yearly_report = yearly_counts.reset_index()
yearly_report.columns = ["Release_Year", "Total_Titles"]

# Step 3: Calculate year-over-year changes
yearly_report["Previous_Year_Titles"] = (
    yearly_report["Total_Titles"].shift(1)
)

yearly_report["Change"] = (
    yearly_report["Total_Titles"]
    - yearly_report["Previous_Year_Titles"]
)

yearly_report["Growth_Percentage"] = (
    yearly_report["Total_Titles"]
    .pct_change()
    .mul(100)
    .round(2)
)

# Save yearly analysis report
yearly_report.to_csv(
    "Netflix_Yearly_Trend_Report.csv",
    index=False
)

print("\nNETFLIX RELEASE YEAR TREND ANALYSIS")
print("=" * 45)

print("\nMost recent 15 release years:")
print(yearly_report.tail(15).to_string(index=False))

# Identify the year with the highest number of titles
peak_year = yearly_counts.idxmax()
peak_count = yearly_counts.max()

print("\nPeak release year:", peak_year)
print("Titles released in peak year:", peak_count)

# Step 4: Create visualizations
sns.set_theme(style="whitegrid")

fig, axes = plt.subplots(2, 1, figsize=(14, 10))

# Chart 1: Yearly release trend
sns.lineplot(
    x=yearly_counts.index,
    y=yearly_counts.values,
    marker="o",
    ax=axes[0]
)

axes[0].set_title("Netflix Content by Release Year")
axes[0].set_xlabel("Release Year")
axes[0].set_ylabel("Number of Titles")

# Chart 2: Year-over-year growth and decline
growth_data = yearly_report.dropna(
    subset=["Growth_Percentage"]
)

axes[1].bar(
    growth_data["Release_Year"],
    growth_data["Growth_Percentage"]
)

axes[1].axhline(y=0, linestyle="--")
axes[1].set_title("Year-over-Year Change in Title Count (%)")
axes[1].set_xlabel("Release Year")
axes[1].set_ylabel("Change (%)")

plt.suptitle(
    "Netflix Historical Release Trend Dashboard",
    fontsize=16,
    fontweight="bold"
)

plt.tight_layout()

# Save dashboard
plt.savefig(
    "Netflix_Release_Year_Dashboard.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# Step 5: Interpret business patterns
print("\nBUSINESS INSIGHTS")
print("=" * 45)

print(
    f"Highest title count: {peak_count} titles in {peak_year}"
)

if len(yearly_report) >= 2:
    last_year = yearly_report.iloc[-1]
    previous_year = yearly_report.iloc[-2]

    change = last_year["Change"]

    print(
        f"Latest year in data: {int(last_year['Release_Year'])}"
    )
    print(
        f"Title count: {int(last_year['Total_Titles'])}"
    )

    if change > 0:
        print("The title count increased from the previous recorded year.")
    elif change < 0:
        print("The title count decreased from the previous recorded year.")
    else:
        print("The title count remained unchanged from the previous recorded year.")

print("\nFiles created:")
print("1. Netflix_Yearly_Trend_Report.csv")
print("2. Netflix_Release_Year_Dashboard.png")
