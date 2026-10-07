-- Popularidade por gênero, já no grão de faixa.
create or replace table mart_genre as
select
    b.genre,
    count(*)                                              as tracks,
    round(median(d.popularity), 1)                        as median_popularity,
    round(avg(d.popularity), 1)                           as avg_popularity,
    round(100.0 * avg(case when d.popularity >= 70 then 1 else 0 end), 1) as hit_rate_pct,
    round(100.0 * avg(case when d.popularity = 0 then 1 else 0 end), 1)   as zero_pop_pct
from bridge_track_genre b
join dim_track d using (track_id)
group by b.genre;

-- Popularidade por década de lançamento (efeito de recência do algoritmo).
create or replace table mart_release_year as
select
    (release_year // 10) * 10                  as decade,
    count(*)                                   as tracks,
    round(median(popularity), 1)               as median_popularity,
    round(100.0 * avg(case when popularity >= 70 then 1 else 0 end), 1) as hit_rate_pct
from dim_track
where release_year is not null
group by 1;
