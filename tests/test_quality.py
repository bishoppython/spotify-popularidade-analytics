"""Testes de qualidade de dados: rodam no CI depois do pipeline."""
import sys
from pathlib import Path

import duckdb
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from config import DB  # noqa: E402


@pytest.fixture(scope="module")
def con():
    c = duckdb.connect(str(DB), read_only=True)
    yield c
    c.close()


def scalar(con, sql):
    return con.execute(sql).fetchone()[0]


def test_dim_track_tem_grao_unico(con):
    assert scalar(con, "select count(*) - count(distinct track_id) from dim_track") == 0


def test_ids_sem_nulos(con):
    assert scalar(con, "select count(*) from dim_track where track_id is null") == 0


def test_popularidade_no_intervalo(con):
    assert scalar(con, "select count(*) from dim_track where popularity not between 0 and 100") == 0


@pytest.mark.parametrize("col", ["danceability", "energy", "speechiness", "acousticness",
                                 "instrumentalness", "liveness", "valence"])
def test_features_entre_0_e_1(con, col):
    assert scalar(con, f"select count(*) from dim_track where {col} not between 0 and 1") == 0


def test_toda_faixa_tem_genero(con):
    assert scalar(con, "select count(*) from dim_track d anti join bridge_track_genre b using(track_id)") == 0


def test_reconciliacao_staging_dim(con):
    assert scalar(con, "select count(distinct track_id) from stg_playlist_tracks") == scalar(con, "select count(*) from dim_track")


def test_datas_de_lancamento_plausiveis(con):
    assert scalar(con, "select count(*) from dim_track where release_year < 1900 or release_year > 2020") == 0
