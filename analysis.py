# %%
# # Netflix Data Analysis
# Cleaning, EDA and visualisation of the Netflix Titles dataset.
# Put Kaggle's `netflix_titles.csv` in `data/`. If it is missing, a synthetic sample is generated so the notebook still runs.

# %%
import os
import pandas as pd, numpy as np
import matplotlib.pyplot as plt, seaborn as sns
sns.set_theme(style="whitegrid")
os.makedirs("images", exist_ok=True)
PATH = "data/netflix_titles.csv"
if not os.path.exists(PATH):
    from generate_data import generate
    generate(PATH)
df = pd.read_csv(PATH)
print(df.shape)
df.head()

# %%
# ## 1. Missing values
missing = df.isna().sum().sort_values(ascending=False)
print((missing / len(df) * 100).round(1).astype(str) + " %")

# %%
# ## 2. Cleaning
# Decisions: text gaps become "Unknown" (we keep the rows), duplicates are dropped,
# dates are parsed, and `duration` is split into numeric minutes (movies) / seasons (TV).
df = df.drop_duplicates().copy()
for c in ["director", "cast", "country"]:
    df[c] = df[c].fillna("Unknown")
df["rating"] = df["rating"].fillna(df["rating"].mode()[0])
df["date_added"] = pd.to_datetime(df["date_added"].str.strip(), format="mixed", errors="coerce")
df = df.dropna(subset=["date_added"]).copy()
df["year_added"] = df["date_added"].dt.year
df["month_added"] = df["date_added"].dt.month
df["minutes"] = np.where(df["type"] == "Movie", df["duration"].str.extract(r"(\d+)")[0].astype(float), np.nan)
df["seasons"] = np.where(df["type"] == "TV Show", df["duration"].str.extract(r"(\d+)")[0].astype(float), np.nan)
df.to_csv("cleaned_dataset.csv", index=False)
print("Cleaned shape:", df.shape)

# %%
# ## 3. Which country produces the most content?
countries = df.assign(country=df["country"].str.split(", ")).explode("country")
countries = countries[countries["country"] != "Unknown"]
top_c = countries["country"].value_counts().head(10)
plt.figure(figsize=(9, 5))
sns.barplot(x=top_c.values, y=top_c.index, hue=top_c.index, palette="Reds_r", legend=False)
plt.title("Top 10 content-producing countries"); plt.xlabel("Titles")
plt.tight_layout(); plt.savefig("images/top_countries.png", dpi=150); plt.show()

# %%
# ## 4. Movies vs TV Shows
split = df["type"].value_counts()
plt.figure(figsize=(5, 5))
plt.pie(split, labels=split.index, autopct="%1.1f%%", colors=["#e50914", "#221f1f"], startangle=90,
        textprops={"color": "white", "fontsize": 12, "weight": "bold"}, wedgeprops={"edgecolor": "white"})
plt.title("Movies vs TV Shows"); plt.tight_layout()
plt.savefig("images/movies_vs_tv.png", dpi=150); plt.show()

# %%
# ## 5. Average movie duration
avg_min = df["minutes"].mean()
print(f"Average movie duration: {avg_min:.1f} minutes (median {df['minutes'].median():.0f})")
plt.figure(figsize=(8, 4.5))
sns.histplot(df["minutes"].dropna(), bins=30, color="#e50914")
plt.axvline(avg_min, color="black", ls="--", label=f"mean = {avg_min:.0f} min"); plt.legend()
plt.title("Distribution of movie durations"); plt.xlabel("Minutes")
plt.tight_layout(); plt.savefig("images/movie_duration.png", dpi=150); plt.show()

# %%
# ## 6. Genre popularity
genres = df.assign(g=df["listed_in"].str.split(", ")).explode("g")
top_g = genres.groupby(["g", "type"]).size().unstack(fill_value=0)
top_g["total"] = top_g.sum(axis=1)
top_g = top_g.sort_values("total", ascending=False).head(12).drop(columns="total")
top_g.plot(kind="barh", stacked=True, figsize=(9, 6), color=["#e50914", "#221f1f"]).invert_yaxis()
plt.title("Most popular genres"); plt.xlabel("Titles"); plt.ylabel("")
plt.tight_layout(); plt.savefig("images/genres.png", dpi=150); plt.show()

# %%
# ## 7. Content added each year
yearly = df.groupby(["year_added", "type"]).size().unstack(fill_value=0)
yearly.plot(marker="o", figsize=(9, 4.5), color=["#e50914", "#221f1f"])
plt.title("Titles added to Netflix per year"); plt.ylabel("Titles"); plt.xlabel("Year added")
plt.tight_layout(); plt.savefig("images/content_per_year.png", dpi=150); plt.show()

# %%
# ## 8. Heatmap: when is content added? (year x month)
heat = df.pivot_table(index="year_added", columns="month_added", values="show_id", aggfunc="count", fill_value=0)
plt.figure(figsize=(10, 5))
sns.heatmap(heat, cmap="Reds", annot=True, fmt="d", cbar_kws={"label": "Titles"})
plt.title("Titles added by year and month"); plt.xlabel("Month"); plt.ylabel("Year")
plt.tight_layout(); plt.savefig("images/added_heatmap.png", dpi=150); plt.show()

# %%
# ## 9. Heatmap: rating by type
rt = pd.crosstab(df["rating"], df["type"])
plt.figure(figsize=(5, 6))
sns.heatmap(rt, annot=True, fmt="d", cmap="Reds")
plt.title("Content rating by type"); plt.tight_layout()
plt.savefig("images/rating_heatmap.png", dpi=150); plt.show()

# %%
# ## 10. Key insights
print(f"1. {top_c.index[0]} produces the most content ({top_c.iloc[0]} titles).")
print(f"2. {split.iloc[0]/split.sum():.0%} of the catalogue is {split.index[0]}s.")
print(f"3. Average movie length is {avg_min:.0f} minutes.")
print(f"4. Most popular genre: {genres['g'].value_counts().index[0]}.")
print(f"5. Peak year for additions: {int(yearly.sum(axis=1).idxmax())}.")
