"""Creates a synthetic dataset with the SAME columns as Kaggle's 'Netflix Movies and TV Shows'
(netflix_titles.csv). Use it to test the pipeline; replace with the real file for real insights."""
import numpy as np, pandas as pd, os

def generate(path="data/netflix_titles.csv", n=4000, seed=42):
    rng = np.random.default_rng(seed)
    countries = ["United States", "India", "United Kingdom", "Canada", "France", "Japan",
                 "South Korea", "Spain", "Germany", "Mexico", "Brazil", "Australia"]
    cw = np.array([30, 14, 9, 5, 4, 5, 5, 4, 3, 3, 3, 2], float); cw /= cw.sum()
    genres_m = ["Dramas", "Comedies", "Documentaries", "Action & Adventure", "Thrillers",
                "Horror Movies", "Romantic Movies", "International Movies", "Independent Movies"]
    genres_t = ["TV Dramas", "TV Comedies", "Crime TV Shows", "Reality TV", "Kids' TV",
                "Anime Series", "Docuseries", "International TV Shows"]
    ratings_m = ["PG-13", "R", "PG", "TV-MA", "TV-14", "TV-PG", "G", "NR"]
    ratings_t = ["TV-MA", "TV-14", "TV-PG", "TV-Y7", "TV-Y", "TV-G"]
    rows = []
    for i in range(n):
        is_movie = rng.random() < 0.69
        added = pd.Timestamp("2015-01-01") + pd.Timedelta(days=int(rng.beta(4, 1.3) * 2300))
        rel = int(min(added.year, rng.normal(2015, 7)))
        rel = max(1950, rel)
        k = rng.integers(1, 3)
        ctry = ", ".join(rng.choice(countries, k, replace=False, p=cw))
        pool = genres_m if is_movie else genres_t
        g = ", ".join(rng.choice(pool, rng.integers(1, 4), replace=False))
        rows.append({
            "show_id": f"s{i+1}", "type": "Movie" if is_movie else "TV Show",
            "title": f"Title {i+1}", "director": f"Director {rng.integers(1, 900)}" if rng.random() > .3 else np.nan,
            "cast": f"Actor {rng.integers(1, 2000)}, Actor {rng.integers(1, 2000)}" if rng.random() > .1 else np.nan,
            "country": ctry if rng.random() > .08 else np.nan,
            "date_added": added.strftime("%B %-d, %Y") if rng.random() > .01 else np.nan,
            "release_year": rel, "rating": rng.choice(ratings_m if is_movie else ratings_t) if rng.random() > .005 else np.nan,
            "duration": f"{int(np.clip(rng.normal(100, 25), 40, 200))} min" if is_movie else f"{rng.choice([1,2,3,4,5], p=[.67,.18,.08,.04,.03])} Season" + ("s" if False else ""),
            "listed_in": g, "description": "Synthetic description."})
    df = pd.DataFrame(rows)
    df.loc[df.type == "TV Show", "duration"] = df.loc[df.type == "TV Show", "duration"].apply(
        lambda s: s if s.startswith("1 ") else s + "s")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    return df

if __name__ == "__main__":
    generate(); print("Sample data written to data/netflix_titles.csv")
