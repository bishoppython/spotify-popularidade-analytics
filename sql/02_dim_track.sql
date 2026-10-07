-- Uma faixa aparece em várias playlists: o grão analítico correto é uma linha por track_id.
create or replace table dim_track as
select
    track_id,
    any_value(track_name)            as track_name,
    any_value(track_artist)          as track_artist,
    max(popularity)                  as popularity,
    min(release_date)                as release_date,
    year(min(release_date))          as release_year,
    any_value(danceability)          as danceability,
    any_value(energy)                as energy,
    any_value(loudness)              as loudness,
    any_value(speechiness)           as speechiness,
    any_value(acousticness)          as acousticness,
    any_value(instrumentalness)      as instrumentalness,
    any_value(liveness)              as liveness,
    any_value(valence)               as valence,
    any_value(tempo)                 as tempo,
    any_value(duration_min)          as duration_min,
    count(distinct playlist_id)      as n_playlists
from stg_playlist_tracks
group by track_id;

-- Ponte faixa x gênero (uma faixa pode estar em playlists de gêneros diferentes).
create or replace table bridge_track_genre as
select distinct track_id, genre from stg_playlist_tracks;
