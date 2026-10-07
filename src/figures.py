"""Gera as imagens estáticas usadas no README (o GitHub não renderiza o dashboard interativo)."""
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from config import DOCS, OUT  # noqa: E402

INK, MUTED, COBALT, AMBER, GRID = "#0C1E46", "#4B5B7E", "#1F4FD8", "#C27C0E", "#E3E9F4"
plt.rcParams.update({"font.size": 11, "axes.edgecolor": GRID, "axes.labelcolor": MUTED,
                     "xtick.color": MUTED, "ytick.color": INK, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
                     "axes.axisbelow": True, "axes.titleweight": "bold", "axes.titlesize": 13,
                     "axes.titlecolor": INK, "axes.titlelocation": "left"})
m = json.loads((OUT / "metrics.json").read_text())
img = DOCS / "img"
img.mkdir(parents=True, exist_ok=True)

g = sorted(m["genre"], key=lambda r: r["median_popularity"])
fig, ax = plt.subplots(figsize=(8, 3.6), dpi=150)
bars = ax.barh([r["genre"] for r in g], [r["median_popularity"] for r in g], color=COBALT, height=0.6)
ax.bar_label(bars, fmt="%.0f", padding=4, color=INK)
ax.set_xlabel("Popularidade mediana (0–100)"); ax.set_xlim(0, 60); ax.grid(axis="y", visible=False)
ax.set_title("Popularidade mediana por gênero")
fig.tight_layout(); fig.savefig(img / "genero.png"); plt.close(fig)

names = {"instrumentalness": "Instrumentalidade", "energy": "Energia", "duration_min": "Duração",
         "liveness": "Ao vivo", "tempo": "Andamento", "speechiness": "Fala", "danceability": "Dançabilidade",
         "valence": "Positividade", "loudness": "Volume", "acousticness": "Acústica"}
c = sorted(m["spearman_corr"].items(), key=lambda kv: kv[1])
fig, ax = plt.subplots(figsize=(8, 4.2), dpi=150)
ax.barh([names[k] for k, _ in c], [v for _, v in c], color=[AMBER if v < 0 else COBALT for _, v in c], height=0.6)
ax.axvline(0, color=MUTED, lw=1); ax.set_xlim(-0.25, 0.25); ax.grid(axis="y", visible=False)
ax.set_xlabel("Correlação de Spearman com a popularidade")
ax.set_title("Características do áudio x popularidade")
fig.tight_layout(); fig.savefig(img / "correlacao.png"); plt.close(fig)
print("OK: docs/img/genero.png, docs/img/correlacao.png")
