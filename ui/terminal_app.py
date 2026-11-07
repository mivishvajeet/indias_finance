"""India Finance Intelligence Terminal:
Institutional Financial Research × Data Engineering Observability × Local AI.
"""
from pathlib import Path
import sys
import streamlit as st

# Setup Root Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ui.components.theme import TERMINAL_CSS
from ui.components.topbar import render_topbar
from ui.components.sidebar import render_sidebar

# Import Page Modules
from ui.pages.market_overview import render_market_overview
from ui.pages.equity_screener import render_equity_screener
from ui.pages.stock_analytics import render_stock_analytics
from ui.pages.mutual_fund_intelligence import render_mutual_fund_intelligence
from ui.pages.macro_intelligence import render_macro_intelligence
from ui.pages.risk_analytics import render_risk_analytics
from ui.pages.data_operations import render_data_operations
from ui.pages.data_quality import render_data_quality
from ui.pages.data_lineage import render_data_lineage
from ui.pages.incident_center import render_incident_center
from ui.pages.ask_finance import render_ask_finance

# Configure Page
st.set_page_config(
    page_title="India Finance Intelligence Terminal",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply Institutional Bloomberg Dark Design Tokens
st.markdown(TERMINAL_CSS, unsafe_allow_html=True)

# Render Global Persistent Topbar & Navigation Sidebar
render_topbar()
active_module = render_sidebar()

# Route to Active Workspace
if active_module == "Market Overview":
    render_market_overview()
elif active_module == "Equity Screener":
    render_equity_screener()
elif active_module == "Stock Analytics":
    render_stock_analytics()
elif active_module == "Mutual Fund Intelligence":
    render_mutual_fund_intelligence()
elif active_module == "Macro Intelligence":
    render_macro_intelligence()
elif active_module == "Risk Analytics":
    render_risk_analytics()
elif active_module == "Data Operations":
    render_data_operations()
elif active_module == "Data Quality Center":
    render_data_quality()
elif active_module == "Data Lineage Explorer":
    render_data_lineage()
elif active_module == "Data Incident Center":
    render_incident_center()
elif active_module == "Ask Finance AI":
    render_ask_finance()
