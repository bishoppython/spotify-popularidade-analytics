from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "spotify_songs.csv"
DB = ROOT / "data" / "warehouse.duckdb"
SQL = ROOT / "sql"
OUT = ROOT / "outputs"
DOCS = ROOT / "docs"

SOURCE_URL = (
    "https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/"
    "data/2020/2020-01-21/spotify_songs.csv"
)
SOURCE_SHA256 = "9902920cfe4940f0914ebb6716801a42f7f19ac88fbd6693eaae7e2822b16845"
HIT_THRESHOLD = 70  # popularidade >= 70 é tratada como "hit"
