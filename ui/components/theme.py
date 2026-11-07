"""Institutional Bloomberg Terminal Design System and CSS Tokens."""

TERMINAL_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    :root {
        --bg-primary: #080C12;
        --bg-secondary: #0D131D;
        --bg-panel: #111A26;
        --bg-elevated: #172231;
        --border-color: #253346;
        
        --text-primary: #E6EDF5;
        --text-secondary: #91A0B3;
        --text-muted: #64748B;
        
        --color-pos: #00C087;
        --color-neg: #FF5C65;
        --color-warn: #F5B942;
        --color-info: #45A3FF;
        --color-bench: #A78BFA;
    }

    /* Core Application Reset */
    .stApp {
        background-color: var(--bg-primary);
        color: var(--text-primary);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Numeric & Monospace Elements */
    .num, .metric-val, code, pre {
        font-family: 'JetBrains Mono', monospace !important;
        font-variant-numeric: tabular-nums;
    }

    /* Top Ticker Ribbon */
    .terminal-topbar {
        background: var(--bg-secondary);
        border: 1px solid var(--border-color);
        border-radius: 4px;
        padding: 8px 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
        font-size: 0.84rem;
    }
    .ticker-group {
        display: flex;
        gap: 20px;
        flex-wrap: wrap;
    }
    .ticker-chip {
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .ticker-name {
        color: var(--text-secondary);
        font-weight: 600;
        font-size: 0.78rem;
    }
    .ticker-price {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
        color: var(--text-primary);
    }
    .ticker-delta-pos {
        color: var(--color-pos);
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .ticker-delta-neg {
        color: var(--color-neg);
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
        font-size: 0.8rem;
    }

    /* Institutional KPI Stat Card */
    .kpi-card {
        background: var(--bg-panel);
        border: 1px solid var(--border-color);
        border-radius: 4px;
        padding: 12px 16px;
        margin-bottom: 10px;
    }
    .kpi-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 4px;
    }
    .kpi-label {
        font-size: 0.74rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--text-secondary);
    }
    .kpi-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.45rem;
        font-weight: 700;
        color: var(--text-primary);
        font-variant-numeric: tabular-nums;
        line-height: 1.2;
    }
    .kpi-subtext {
        font-size: 0.75rem;
        color: var(--text-muted);
        margin-top: 4px;
        font-family: 'JetBrains Mono', monospace;
    }

    /* Badges & Status Chips */
    .status-badge {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 2px 7px;
        border-radius: 3px;
        display: inline-block;
        letter-spacing: 0.03em;
    }
    .badge-verified {
        background: rgba(0, 192, 135, 0.12);
        color: var(--color-pos);
        border: 1px solid var(--color-pos);
    }
    .badge-critical {
        background: rgba(255, 92, 101, 0.12);
        color: var(--color-neg);
        border: 1px solid var(--color-neg);
    }
    .badge-warning {
        background: rgba(245, 185, 66, 0.12);
        color: var(--color-warn);
        border: 1px solid var(--color-warn);
    }
    .badge-neutral {
        background: rgba(69, 163, 255, 0.12);
        color: var(--color-info);
        border: 1px solid var(--color-info);
    }

    /* Compact Financial Tables */
    .dataframe {
        background: var(--bg-panel) !important;
        border: 1px solid var(--border-color) !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.82rem !important;
    }
    
    /* Clean Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: var(--bg-secondary) !important;
        border-right: 1px solid var(--border-color) !important;
    }
    .brand-title {
        font-size: 1.05rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        color: #FFFFFF;
        line-height: 1.2;
        margin-bottom: 2px;
    }
    .brand-subtitle {
        font-size: 0.72rem;
        font-weight: 600;
        color: var(--color-info);
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 16px;
    }
    .sidebar-footer {
        padding: 12px 0;
        border-top: 1px solid var(--border-color);
        font-size: 0.75rem;
        color: var(--text-muted);
        font-family: 'JetBrains Mono', monospace;
    }
</style>
"""

PLOTLY_LAYOUT_TEMPLATE = dict(
    template="plotly_dark",
    plot_bgcolor="#080C12",
    paper_bgcolor="#080C12",
    font=dict(family="Inter, sans-serif", color="#91A0B3", size=11),
    xaxis=dict(
        gridcolor="#172231",
        linecolor="#253346",
        tickfont=dict(family="JetBrains Mono", size=10, color="#64748B"),
        showgrid=True,
    ),
    yaxis=dict(
        gridcolor="#172231",
        linecolor="#253346",
        tickfont=dict(family="JetBrains Mono", size=10, color="#64748B"),
        showgrid=True,
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        font=dict(size=10, color="#E6EDF5"),
    ),
    margin=dict(l=10, r=10, t=30, b=10),
)
