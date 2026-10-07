"""Monta o dashboard a partir das métricas calculadas em analyze.py."""
import json

import plotly.graph_objects as go

from config import DOCS, OUT
from report import AMBER, COBALT, NEUTRAL, br, fig_html, kpi, render

m = json.loads((OUT / "metrics.json").read_text())

# 1. Popularidade mediana por gênero
g = sorted(m["genre"], key=lambda r: r["median_popularity"])
f1 = go.Figure(go.Bar(
    x=[r["median_popularity"] for r in g], y=[r["genre"] for r in g], orientation="h",
    marker=dict(color=COBALT, cornerradius=4), text=[f'{r["median_popularity"]:.0f}' for r in g],
    textposition="outside", cliponaxis=False,
    customdata=[[r["hit_rate_pct"], r["tracks"]] for r in g],
    hovertemplate="%{y}<br>Mediana: %{x}<br>Hits: %{customdata[0]}%<br>Faixas: %{customdata[1]:,}<extra></extra>"))
f1.update_xaxes(title="Popularidade mediana (0–100)", range=[0, 60])

# 2. Correlação de Spearman (divergente)
c = sorted(m["spearman_corr"].items(), key=lambda kv: kv[1])
names = {"instrumentalness": "Instrumentalidade", "energy": "Energia", "duration_min": "Duração",
         "liveness": "Ao vivo", "tempo": "Andamento (BPM)", "speechiness": "Fala", "danceability": "Dançabilidade",
         "valence": "Positividade", "loudness": "Volume", "acousticness": "Acústica"}
f2 = go.Figure(go.Bar(
    x=[v for _, v in c], y=[names[k] for k, _ in c], orientation="h",
    marker=dict(color=[AMBER if v < 0 else COBALT for _, v in c], cornerradius=4),
    hovertemplate="%{y}: ρ = %{x:.3f}<extra></extra>"))
f2.update_xaxes(title="Correlação de Spearman com a popularidade", range=[-0.25, 0.25], zeroline=True, zerolinecolor=NEUTRAL)

# 3. Popularidade por década de lançamento
d = [r for r in m["decade"] if r["tracks"] >= 100]
f3 = go.Figure(go.Scatter(
    x=[f'{r["decade"]}s' for r in d], y=[r["median_popularity"] for r in d], mode="lines+markers",
    line=dict(color=COBALT, width=2), marker=dict(size=9, color=COBALT, line=dict(color="#fff", width=2)),
    customdata=[r["tracks"] for r in d],
    hovertemplate="Década de %{x}<br>Mediana: %{y}<br>Faixas: %{customdata:,}<extra></extra>"))
f3.update_yaxes(title="Popularidade mediana", range=[30, 60])

# 4. Subgêneros: melhores e piores
sg = m["subgenre_top5"] + m["subgenre_bottom5"]
sg = sorted(sg, key=lambda r: r["median_popularity"])
f4 = go.Figure(go.Bar(
    x=[r["median_popularity"] for r in sg], y=[f'{r["subgenre"]} ({r["genre"]})' for r in sg], orientation="h",
    marker=dict(color=[COBALT if r in m["subgenre_top5"] else NEUTRAL for r in sg], cornerradius=4),
    text=[f'{r["median_popularity"]:.0f}' for r in sg], textposition="outside", cliponaxis=False,
    hovertemplate="%{y}<br>Mediana: %{x}<extra></extra>"))
f4.update_xaxes(title="Popularidade mediana", range=[0, 75])

top = g[-1]; low = g[0]
corr_max = max(m["spearman_corr"].items(), key=lambda kv: abs(kv[1]))
sections = [
    {"title": "Pop e latin lideram; EDM fica para trás",
     "insight": f'O pop tem a maior popularidade mediana ({top["median_popularity"]:.0f}) e a maior taxa de hits ({br(top["hit_rate_pct"])}%). '
                f'O EDM tem a menor mediana ({low["median_popularity"]:.0f}) e só {br(low["hit_rate_pct"])}% de hits.',
     "chart": fig_html(f1, 300)},
    {"title": "As características do áudio quase não explicam o sucesso",
     "insight": f'Nenhuma característica passa de |ρ| = {br(abs(corr_max[1]),2)}. A mais forte é a instrumentalidade, com efeito negativo: '
                'faixas sem vocal tendem a ser menos populares. Dançabilidade e energia, intuições comuns, praticamente não se relacionam com a popularidade.',
     "chart": fig_html(f2, 380),
     "note": "Correlação calculada apenas nas faixas com popularidade maior que zero."},
    {"title": "Os subgêneros separam mais do que os gêneros",
     "insight": f'A distância entre o melhor e o pior subgênero ({sg[-1]["median_popularity"]:.0f} contra {sg[0]["median_popularity"]:.0f}) é maior que entre os gêneros. '
                'Dentro do próprio EDM e do R&B há subgêneros fortes e fracos.',
     "chart": fig_html(f4, 400),
     "note": "Apenas subgêneros com pelo menos 200 faixas."},
    {"title": "Clássicos que sobrevivem nas playlists são mais populares",
     "insight": 'Faixas dos anos 60 e 70 que ainda aparecem nas playlists têm mediana acima das lançadas nos anos 2000. '
                'É um viés de sobrevivência: só os clássicos que continuam sendo ouvidos chegam ao dataset.',
     "chart": fig_html(f3, 300),
     "note": "Décadas com menos de 100 faixas foram omitidas."},
]
kpis = [kpi(f'{m["tracks"]:,}'.replace(",", "."), "faixas únicas analisadas"),
        kpi(f'{m["duplicates_removed"]:,}'.replace(",", "."), "duplicatas entre playlists removidas"),
        kpi(f'{100*m["hits"]/m["tracks"]:.1f}%'.replace(".", ","), f'são hits (popularidade ≥ {m["hit_threshold"]})'),
        kpi(f'{abs(corr_max[1]):.2f}'.replace(".", ","), "maior correlação de áudio (|ρ|)")]
render(DOCS / "index.html",
       title="O que faz uma música ser popular no Spotify?",
       level="Nível bronze · Análise exploratória e storytelling visual",
       question="Quais gêneros concentram as músicas mais populares, se as características do áudio explicam o sucesso e como a idade da faixa se relaciona com a popularidade.",
       kpis=kpis, sections=sections,
       method="Pipeline em Python e SQL (DuckDB): download com checksum, staging com tipagem, deduplicação para uma linha por faixa, marts por gênero e década, correlação de Spearman e testes de qualidade rodando no GitHub Actions.",
       source=f'TidyTuesday 2020-01-21 (spotifyr), {m["rows_raw"]:,} entradas de playlists coletadas em janeiro de 2020. A popularidade é uma foto daquele momento.'.replace(",", "."),
       repo_url="https://github.com/bishoppython/spotify-popularidade-analytics")
print("OK: docs/index.html")
