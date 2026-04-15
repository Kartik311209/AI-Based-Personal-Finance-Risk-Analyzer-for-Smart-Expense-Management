import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# ── Design tokens (kept in sync with CSS) ──────────────────────────────────
C = {
    'bg':        'rgba(0,0,0,0)',
    'text':      '#64748b',
    'grid':      'rgba(255,255,255,0.05)',
    'green':     '#00e599',
    'blue':      '#0ea5e9',
    'purple':    '#8b5cf6',
    'orange':    '#f59e0b',
    'red':       '#ef4444',
    'pink':      '#ec4899',
    'teal':      '#14b8a6',
}

CAT_COLORS = ['#00e599', '#0ea5e9', '#8b5cf6', '#f59e0b', '#ec4899', '#f87171', '#14b8a6', '#fbbf24']

_BASE_LAYOUT = dict(
    plot_bgcolor=C['bg'],
    paper_bgcolor=C['bg'],
    font=dict(family="Inter, sans-serif", color=C['text'], size=12),
    margin=dict(l=0, r=0, t=10, b=0),
    hovermode='x unified',
    hoverlabel=dict(
        bgcolor='rgba(15,23,42,0.95)',
        bordercolor='rgba(255,255,255,0.1)',
        font=dict(color='#e2e8f0', size=12, family="Inter, sans-serif")
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom", y=-0.25,
        xanchor="center", x=0.5,
        title="",
        font=dict(size=11, color='#64748b')
    )
)


def _apply_base(fig, **overrides):
    layout = {**_BASE_LAYOUT, **overrides}
    fig.update_layout(**layout)
    return fig


def plot_expense_trend(df: pd.DataFrame) -> go.Figure:
    """Smooth gradient area chart — daily spend trend."""
    if df.empty:
        return go.Figure()

    daily = df.groupby('date')['amount'].sum().reset_index().sort_values('date')

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily['date'],
        y=daily['amount'],
        mode='lines',
        name='Daily Spend',
        line=dict(color=C['green'], width=2.5, shape='spline', smoothing=1.2),
        fill='tozeroy',
        fillcolor='rgba(0, 229, 153, 0.08)',
        hovertemplate='<b>%{x|%b %d}</b><br>₹%{y:,.0f}<extra></extra>',
    ))

    fig = _apply_base(fig,
        xaxis=dict(
            title="",
            showgrid=False,
            tickformat='%b %d',
            tickfont=dict(size=11),
            zeroline=False,
            linecolor='rgba(255,255,255,0.05)'
        ),
        yaxis=dict(
            title="",
            showgrid=True,
            gridcolor=C['grid'],
            tickprefix='₹',
            tickformat=',.0f',
            zeroline=False,
            tickfont=dict(size=11)
        )
    )
    return fig


def plot_stacked_bar(df: pd.DataFrame) -> go.Figure:
    """Stacked bar chart — monthly spend by category."""
    if df.empty or 'category' not in df.columns:
        return go.Figure()

    df = df.copy()
    df['month'] = df['date'].dt.strftime('%b %Y')
    grouped = df.groupby(['month', 'category'])['amount'].sum().reset_index()

    # Sort months chronologically
    month_order = df.sort_values('date')['date'].dt.strftime('%b %Y').unique().tolist()
    month_order = list(dict.fromkeys(month_order))  # deduplicate, preserve order

    fig = px.bar(
        grouped,
        x='month', y='amount', color='category',
        color_discrete_sequence=CAT_COLORS,
        category_orders={'month': month_order},
        barmode='stack',
        custom_data=['category']
    )
    fig.update_traces(
        hovertemplate='<b>%{customdata[0]}</b><br>₹%{y:,.0f}<extra></extra>',
        marker_line_width=0,
    )
    fig = _apply_base(fig,
        xaxis=dict(title="", showgrid=False, tickfont=dict(size=11)),
        yaxis=dict(title="", showgrid=True, gridcolor=C['grid'],
                   tickprefix='₹', tickformat=',.0f', tickfont=dict(size=11))
    )
    return fig


def plot_category_bar(df: pd.DataFrame) -> go.Figure:
    """Horizontal sorted bar — spend by category (for Overview)."""
    if df.empty or 'category' not in df.columns:
        return go.Figure()

    cat_totals = df.groupby('category')['amount'].sum().sort_values(ascending=True).reset_index()
    total = cat_totals['amount'].sum()
    cat_totals['pct'] = (cat_totals['amount'] / total * 100).round(1)

    colors = [CAT_COLORS[i % len(CAT_COLORS)] for i in range(len(cat_totals))]

    fig = go.Figure(go.Bar(
        x=cat_totals['amount'],
        y=cat_totals['category'],
        orientation='h',
        marker=dict(
            color=colors,
            cornerradius=6,
            line=dict(width=0)
        ),
        customdata=cat_totals['pct'],
        hovertemplate='<b>%{y}</b><br>₹%{x:,.0f} (%{customdata:.1f}%)<extra></extra>',
        text=[f'  ₹{v:,.0f}' for v in cat_totals['amount']],
        textposition='outside',
        textfont=dict(size=11, color='#64748b')
    ))

    fig = _apply_base(fig,
        xaxis=dict(title="", showgrid=True, gridcolor=C['grid'],
                   tickprefix='₹', tickformat=',.0f', tickfont=dict(size=10)),
        yaxis=dict(title="", showgrid=False, tickfont=dict(size=12, color='#94a3b8')),
        hovermode='y unified',
        margin=dict(l=0, r=60, t=10, b=0),
        legend=dict(visible=False),
    )
    return fig


def plot_donut(df: pd.DataFrame) -> go.Figure:
    """Donut chart for category share."""
    if df.empty or 'category' not in df.columns:
        return go.Figure()

    cat_totals = df.groupby('category')['amount'].sum().reset_index()

    fig = go.Figure(go.Pie(
        labels=cat_totals['category'],
        values=cat_totals['amount'],
        hole=0.62,
        marker=dict(colors=CAT_COLORS, line=dict(color='rgba(0,0,0,0)', width=2)),
        hovertemplate='<b>%{label}</b><br>₹%{value:,.0f}<br>%{percent}<extra></extra>',
        textinfo='none',
    ))

    total = cat_totals['amount'].sum()
    fig.add_annotation(
        text=f'<b>₹{total:,.0f}</b>',
        x=0.5, y=0.55,
        font=dict(size=16, color='#f8fafc', family='Outfit, sans-serif'),
        showarrow=False
    )
    fig.add_annotation(
        text='Total Spent',
        x=0.5, y=0.42,
        font=dict(size=11, color='#475569', family='Inter, sans-serif'),
        showarrow=False
    )

    fig = _apply_base(fig,
        legend=dict(
            orientation='v', yanchor='middle', y=0.5,
            xanchor='left', x=1.05,
            font=dict(size=11, color='#64748b')
        ),
        margin=dict(l=0, r=80, t=10, b=0)
    )
    return fig
