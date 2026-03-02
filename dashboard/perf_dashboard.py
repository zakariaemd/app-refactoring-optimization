# ============================================
# PERFORMANCE COMPARISON DASHBOARD
# Before vs After Refactoring
# ============================================

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'after'))

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# ============================================
# DATA — Before vs After
# ============================================

df_perf = pd.DataFrame({
    'metric':  ['Temps réponse moy (ms)', 'Requêtes DB / opération',
                'Taux erreur (%)', 'Cache Hit Rate (%)',
                'Lignes code / module', 'Couverture tests (%)'],
    'before':  [850, 12, 18, 0,  420, 0],
    'after':   [45,   1,  2, 78, 85, 87]
})

df_improvements = pd.DataFrame({
    'amélioration':   [
        'Cache système', 'Requête N+1 → JOIN',
        'Validation centralisée', 'Connection pooling',
        'Modèles typés', 'Tests unitaires'
    ],
    'gain_pct': [94.7, 91.7, 88.9, 85.0, 79.8, 87.0],
    'categorie': ['Performance', 'Performance', 'Qualité',
                  'Performance', 'Maintenabilité', 'Qualité']
})

df_timeline = pd.DataFrame({
    'semaine': ['S1','S2','S3','S4','S5','S6'],
    'bugs':    [24, 19, 12, 7, 3, 1],
    'perf_score': [32, 45, 58, 72, 83, 91],
    'test_coverage': [0, 15, 35, 55, 72, 87]
})

df_code_quality = pd.DataFrame({
    'dimension':  ['Lisibilité','Maintenabilité','Performance',
                   'Sécurité','Testabilité','Documentation'],
    'avant': [2, 2, 1, 2, 1, 1],
    'apres': [5, 5, 5, 4, 5, 4]
})

# ============================================
# COLORS
# ============================================
C = {
    'bg':     '#0a0e1a',
    'card':   '#141828',
    'c1':     '#00d4ff',
    'c2':     '#7c3aed',
    'c3':     '#10b981',
    'c4':     '#f59e0b',
    'danger': '#ef4444',
    'text':   '#e2e8f0',
    'sub':    '#94a3b8'
}

cat_colors = {
    'Performance':    C['c1'],
    'Qualité':        C['c3'],
    'Maintenabilité': C['c4']
}

# ============================================
# SUBPLOTS
# ============================================
fig = make_subplots(
    rows=3, cols=3,
    subplot_titles=(
        '📊 Before vs After — KPIs Clés',
        '🚀 Gain par Amélioration (%)',
        '📈 Radar Qualité Code',
        '🐛 Évolution Bugs sur 6 Semaines',
        '⚡ Score Performance dans le Temps',
        '🧪 Couverture Tests (%)',
        '', '', ''
    ),
    specs=[
        [{"type": "xy"},     {"type": "xy"},     {"type": "polar"}],
        [{"type": "xy"},     {"type": "xy"},     {"type": "xy"}],
        [{"type": "xy", "colspan": 3}, None, None]
    ],
    vertical_spacing=0.13,
    horizontal_spacing=0.08
)

# --- R1C1 : Before vs After Grouped Bar
fig.add_trace(go.Bar(
    name='❌ Avant',
    x=df_perf['metric'], y=df_perf['before'],
    marker_color=C['danger'], opacity=0.85,
    hovertemplate='%{x}<br>Avant: %{y}<extra></extra>'
), row=1, col=1)
fig.add_trace(go.Bar(
    name='✅ Après',
    x=df_perf['metric'], y=df_perf['after'],
    marker_color=C['c3'], opacity=0.85,
    hovertemplate='%{x}<br>Après: %{y}<extra></extra>'
), row=1, col=1)

# --- R1C2 : Gains par amélioration
fig.add_trace(go.Bar(
    y=df_improvements['amélioration'],
    x=df_improvements['gain_pct'],
    orientation='h',
    marker_color=[cat_colors[c] for c in df_improvements['categorie']],
    hovertemplate='%{y}<br>Gain: %{x:.1f}%<extra></extra>',
    showlegend=False
), row=1, col=2)

# --- R1C3 : Radar qualité code
categories_radar = df_code_quality['dimension'].tolist()
categories_radar_closed = categories_radar + [categories_radar[0]]

fig.add_trace(go.Scatterpolar(
    r=df_code_quality['avant'].tolist() + [df_code_quality['avant'].iloc[0]],
    theta=categories_radar_closed,
    fill='toself',
    name='Avant',
    line_color=C['danger'],
    fillcolor='rgba(239,68,68,0.2)'
), row=1, col=3)
fig.add_trace(go.Scatterpolar(
    r=df_code_quality['apres'].tolist() + [df_code_quality['apres'].iloc[0]],
    theta=categories_radar_closed,
    fill='toself',
    name='Après',
    line_color=C['c3'],
    fillcolor='rgba(16,185,129,0.2)'
), row=1, col=3)

# --- R2C1 : Évolution bugs
fig.add_trace(go.Scatter(
    x=df_timeline['semaine'], y=df_timeline['bugs'],
    mode='lines+markers',
    line=dict(color=C['danger'], width=3),
    marker=dict(size=10),
    fill='tozeroy', fillcolor='rgba(239,68,68,0.15)',
    name='Bugs',
    hovertemplate='%{x}<br>Bugs: %{y}<extra></extra>'
), row=2, col=1)

# --- R2C2 : Score performance
fig.add_trace(go.Scatter(
    x=df_timeline['semaine'], y=df_timeline['perf_score'],
    mode='lines+markers',
    line=dict(color=C['c1'], width=3),
    marker=dict(size=10),
    fill='tozeroy', fillcolor='rgba(0,212,255,0.15)',
    name='Perf Score',
    hovertemplate='%{x}<br>Score: %{y}/100<extra></extra>'
), row=2, col=2)

# --- R2C3 : Couverture tests
fig.add_trace(go.Bar(
    x=df_timeline['semaine'],
    y=df_timeline['test_coverage'],
    marker_color=C['c4'],
    name='Test Coverage',
    hovertemplate='%{x}<br>Coverage: %{y}%<extra></extra>'
), row=2, col=3)

# --- R3 : Résumé des améliorations (Waterfall)
fig.add_trace(go.Waterfall(
    orientation='v',
    measure=['absolute','relative','relative','relative',
             'relative','relative','total'],
    x=['Score Départ','Cache','JOIN SQL','Validation',
       'Pooling','Tests','Score Final'],
    y=[32, 12, 18, 10, 8, 11, 0],
    connector=dict(line=dict(color=C['sub'])),
    increasing=dict(marker_color=C['c3']),
    decreasing=dict(marker_color=C['danger']),
    totals=dict(marker_color=C['c1']),
    showlegend=False,
    hovertemplate='%{x}<br>Score: %{y}<extra></extra>'
), row=3, col=1)

# ============================================
# KPI CARDS
# ============================================
kpi_cards = [
    ('⚡ Temps Réponse',   '850ms → 45ms'),
    ('📉 Requêtes DB',     '12 → 1 par op'),
    ('🐛 Taux Erreur',     '18% → 2%'),
    ('💾 Cache Hit',        '0% → 78%'),
    ('🧪 Tests Coverage',  '0% → 87%'),
    ('📈 Score Global',    '32 → 91/100'),
]
card_x = [0.08, 0.25, 0.42, 0.59, 0.76, 0.93]
for idx, (label, value) in enumerate(kpi_cards):
    fig.add_annotation(
        x=card_x[idx], y=1.07,
        xref='paper', yref='paper',
        text=f"<b>{value}</b><br><span style='font-size:9px'>{label}</span>",
        showarrow=False,
        font=dict(size=12, color=C['c3']),
        align='center',
        bgcolor=C['card'],
        bordercolor=C['c1'],
        borderwidth=1,
        borderpad=8,
        opacity=0.95
    )

# ============================================
# LAYOUT
# ============================================
fig.update_layout(
    title=dict(
        text='🔧 App Refactoring Dashboard — Before vs After 2024',
        font=dict(size=26, color=C['text'], family='Inter'),
        x=0.5, xanchor='center', y=0.98
    ),
    paper_bgcolor=C['bg'],
    plot_bgcolor=C['card'],
    font=dict(color=C['text'], family='Inter'),
    height=1300,
    barmode='group',
    showlegend=True,
    legend=dict(bgcolor=C['card'], bordercolor=C['c1'], borderwidth=1),
    margin=dict(t=150, b=40, l=40, r=40)
)

for ann in fig['layout']['annotations']:
    ann['font'] = dict(size=12, color=C['c1'])

fig.update_xaxes(gridcolor='rgba(255,255,255,0.05)',
                 linecolor='rgba(255,255,255,0.1)',
                 tickfont=dict(size=9))
fig.update_yaxes(gridcolor='rgba(255,255,255,0.05)',
                 linecolor='rgba(255,255,255,0.1)',
                 tickfont=dict(size=9))

fig.update_polars(
    bgcolor=C['card'],
    radialaxis=dict(gridcolor='rgba(255,255,255,0.1)',
                    linecolor='rgba(255,255,255,0.1)',
                    range=[0, 5]),
    angularaxis=dict(gridcolor='rgba(255,255,255,0.1)')
)

fig.write_html("dashboard/perf_dashboard.html")
fig.write_image("dashboard/perf_dashboard.png", width=1400, height=1300, scale=2)
print("✅ Performance Dashboard exporté !")
