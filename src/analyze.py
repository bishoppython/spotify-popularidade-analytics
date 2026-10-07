"""Responde às perguntas de negócio e grava as métricas usadas no README e no dashboard."""
import json

import duckdb
import pandas as pd

from config import DB, HIT_THRESHOLD, OUT

FEATURES = ["danceability", "energy", "loudness", "speechiness", "acousticness",
            "instrumentalness", "liveness", "valence", "tempo", "duration_min"]


def main():
    OUT.mkdir(exist_ok=True)
    con = duckdb.connect(str(DB), read_only=True)
    tracks = con.execute("select * from dim_track").df()
    genre = con.execute("select * from mart_genre order by median_popularity desc").df()
    decade = con.execute("select * from mart_release_year order by decade").df()
    subgenre = con.execute("""
        select s.genre, s.subgenre, count(distinct s.track_id) tracks,
               round(median(d.popularity),1) median_popularity
        from (select distinct track_id, genre, subgenre from stg_playlist_tracks) s
        join dim_track d using(track_id) group by 1,2 having count(distinct s.track_id) >= 200
        order by median_popularity desc""").df()
    top_artists = con.execute(f"""
        select track_artist, count(*) tracks, round(median(popularity),1) median_popularity,
               sum(case when popularity >= {HIT_THRESHOLD} then 1 else 0 end) hits
        from dim_track group by 1 having count(*) >= 15
        order by median_popularity desc limit 10""").df()

    # Correlação de Spearman (robusta a outliers e a relações não lineares),
    # calculada só nas faixas com popularidade > 0 para não misturar faixas sem histórico.
    active = tracks[tracks.popularity > 0]
    corr = (active[FEATURES + ["popularity"]].corr(method="spearman")["popularity"]
            .drop("popularity").sort_values())

    # Hits vs. não-hits: diferença de mediana de cada característica.
    hits = active[active.popularity >= HIT_THRESHOLD]
    rest = active[active.popularity < HIT_THRESHOLD]
    profile = pd.DataFrame({"hits": hits[FEATURES].median(), "demais": rest[FEATURES].median()}).round(3)

    metrics = {
        "rows_raw": int(con.execute("select count(*) from stg_playlist_tracks").fetchone()[0]),
        "tracks": int(len(tracks)),
        "duplicates_removed": int(con.execute("select count(*) from stg_playlist_tracks").fetchone()[0] - len(tracks)),
        "zero_popularity_tracks": int((tracks.popularity == 0).sum()),
        "hit_threshold": HIT_THRESHOLD,
        "hits": int((tracks.popularity >= HIT_THRESHOLD).sum()),
        "release_years": [int(tracks.release_year.min()), int(tracks.release_year.max())],
        "genre": genre.to_dict(orient="records"),
        "decade": decade.to_dict(orient="records"),
        "subgenre_top5": subgenre.head(5).to_dict(orient="records"),
        "subgenre_bottom5": subgenre.tail(5).to_dict(orient="records"),
        "top_artists": top_artists.to_dict(orient="records"),
        "spearman_corr": corr.round(3).to_dict(),
        "hit_profile": profile.reset_index(names="feature").to_dict(orient="records"),
    }
    (OUT / "metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False, default=float))
    genre.to_csv(OUT / "genre.csv", index=False)
    decade.to_csv(OUT / "decade.csv", index=False)
    print(json.dumps({k: metrics[k] for k in ["tracks", "duplicates_removed", "zero_popularity_tracks", "hits"]}, indent=2))
    print(corr.round(3).to_string())
    print(genre.to_string(index=False))
    print(decade.to_string(index=False))
    print(subgenre.head(5).to_string(index=False)); print(subgenre.tail(5).to_string(index=False))
    print(profile.to_string())
    print(top_artists.to_string(index=False))


if __name__ == "__main__":
    main()
