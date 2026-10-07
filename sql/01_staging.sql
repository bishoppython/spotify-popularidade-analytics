-- Staging: tipagem, padronização e data de lançamento com precisão variável (ano, ano-mês ou data completa).
create or replace table stg_playlist_tracks as
select
    track_id,
    trim(track_name)                                   as track_name,
    trim(track_artist)                                 as track_artist,
    cast(track_popularity as integer)                  as popularity,
    track_album_id,
    cast(case
        when length(track_album_release_date) = 4 then track_album_release_date || '-01-01'
        when length(track_album_release_date) = 7 then track_album_release_date || '-01'
        else track_album_release_date end as date)      as release_date,
    case length(track_album_release_date)
        when 4 then 'year' when 7 then 'month' else 'day' end as release_date_precision,
    playlist_id,
    playlist_genre                                     as genre,
    playlist_subgenre                                  as subgenre,
    danceability, energy, loudness, speechiness, acousticness,
    instrumentalness, liveness, valence, tempo,
    duration_ms / 60000.0                              as duration_min
from raw_spotify
where track_id is not null;
