
# Task 2: Netflix Content Type Analysis Dashboard

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Step 1: Load the cleaned dataset
df = pd.read_csv("Netflix_Cleaned.csv")

# Standardize content type
df["type"] = df["type"].astype(str).str.strip().str.title()

# Step 2: Calculate total Movies and TV Shows
content_counts = df["type"].value_counts()
total_content = len(df)

print("NETFLIX CONTENT TYPE ANALYSIS")
print("-" * 35)
print("Total Content:", total_content)

for content_type, count in content_counts.items():
    percentage = (count / total_content) * 100
    print(f"{content_type}: {count} ({percentage:.2f}%)")

# Step 3: Prepare visualization data
sns.set_theme(style="whitegrid")

# Create dashboard with 3 charts
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

colors = ["#E50914", "#564D4D"]

# Chart 1: Bar chart
sns.barplot(
    x=content_counts.index,
    y=content_counts.values,
    hue=content_counts.index,
    palette=colors,
    legend=False,
    ax=axes[0]
)

axes[0].set_title("Movies vs TV Shows")
axes[0].set_xlabel("Content Type")
axes[0].set_ylabel("Number of Titles")

for i, count in enumerate(content_counts.values):
    axes[0].text(i, count + 50, str(count), ha="center")

# Chart 2: Pie chart
axes[1].pie(
    content_counts.values,
    labels=content_counts.index,
    autopct="%1.1f%%",
    colors=colors,
    startangle=90
)

axes[1].set_title("Content Distribution (%)")

# Chart 3: Percentage comparison
percentages = content_counts / total_content * 100

sns.barplot(
    x=percentages.index,
    y=percentages.values,
    hue=percentages.index,
    palette=colors,
    legend=False,
    ax=axes[2]
)

axes[2].set_title("Content Proportion")
axes[2].set_xlabel("Content Type")
axes[2].set_ylabel("Percentage (%)")
axes[2].set_ylim(0, 100)

for i, percentage in enumerate(percentages.values):
    axes[2].text(
        i, percentage + 1,
        f"{percentage:.2f}%",
        ha="center"
    )

plt.suptitle(
    "Netflix Content Type Analysis Dashboard",
    fontsize=16,
    fontweight="bold"
)

plt.tight_layout()

# Step 4: Save and display dashboard
plt.savefig("Netflix_Content_Dashboard.png", dpi=300)
plt.show()

# Step 5: Summarize key findings
movies = content_counts.get("Movie", 0)
tv_shows = content_counts.get("Tv Show", 0)

print("\nKEY FINDINGS")
print("-" * 35)
print(f"Movies: {movies} ({movies / total_content * 100:.2f}%)")
print(f"TV Shows: {tv_shows} ({tv_shows / total_content * 100:.2f}%)")

if movies > tv_shows:
    print("Movies make up the majority of Netflix content.")
else:
    print("TV Shows make up the majority of Netflix content.")

print("Dashboard saved as Netflix_Content_Dashboard.png")
