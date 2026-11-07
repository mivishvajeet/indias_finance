"""Ask Finance AI: Local Text-to-SQL and RAG Research Assistant Workspace."""
import streamlit as st
import pandas as pd
from ai.rag_assistant import AskFinanceAIAssistant


def render_ask_finance():
    """Renders the local conversational AI financial research assistant."""
    st.markdown("## 🤖 Ask Finance AI — Institutional Research Assistant")
    st.caption("Local Text-to-SQL · Guardrailed Read-Only Execution · Zero Cloud API Costs · Exact Data Provenance")

    # Local Engine Telemetry Badge
    is_ollama = AskFinanceAIAssistant.is_ollama_available()
    engine_badge = '<span class="status-badge badge-verified">OLLAMA LOCAL LLM (PORT 11434)</span>' if is_ollama else '<span class="status-badge badge-neutral">LOCAL DETERMINISTIC TEXT-TO-SQL (OFFLINE CPU)</span>'

    st.markdown(f"""
    <div style="background: #111A26; border: 1px solid #253346; border-radius: 4px; padding: 10px 16px; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center;">
        <div>
            <span style="font-size: 0.78rem; font-weight: 700; color: #91A0B3;">ACTIVE AI INFERENCE ENGINE:</span>
            <span style="margin-left: 8px;">{engine_badge}</span>
        </div>
        <div style="font-size: 0.75rem; color: #64748B; font-family: 'JetBrains Mono';">
            Guardrails: SELECT-Only · Allowlist Enforced · ₹0.00
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Initialize conversation state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Example Prompt Chips
    st.markdown("#### 💡 Quick Research Prompts")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("📉 Stocks below 20-Day SMA", use_container_width=True):
            st.session_state["active_prompt"] = "Which stocks are trading below their 20-day moving average?"
    with c2:
        if st.button("🚀 Top Single-Session Performers", use_container_width=True):
            st.session_state["active_prompt"] = "Which tracked stocks had the highest returns?"
    with c3:
        if st.button("⚖️ Mutual Funds by Sharpe Ratio", use_container_width=True):
            st.session_state["active_prompt"] = "Which mutual funds have the highest Sharpe ratio?"

    c4, c5, c6 = st.columns(3)
    with c4:
        if st.button("🏛️ Latest Macro Indicators (Repo/USD)", use_container_width=True):
            st.session_state["active_prompt"] = "Show the latest macroeconomic CPI, Repo rate, and USD/INR observations."
    with c5:
        if st.button("🚨 Explain Latest Incident", use_container_width=True):
            st.session_state["active_prompt"] = "Explain the latest pipeline incident."
    with c6:
        if st.button("🧹 Clear Chat History", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.pop("active_prompt", None)
            st.rerun()

    # Chat Input
    prompt_val = st.session_state.pop("active_prompt", None)
    user_input = st.chat_input("Ask a financial, technical, or pipeline question...") or prompt_val

    if user_input:
        # Run assistant
        res = AskFinanceAIAssistant.answer_question(user_input)
        st.session_state.chat_history.append({"query": user_input, "response": res})

    # Render Conversation Feed
    if not st.session_state.chat_history:
        st.info("Ask any question about tracked equities, technical indicators, mutual funds, macro trends, or data pipeline health.")
        return

    for turn in reversed(st.session_state.chat_history):
        q = turn["query"]
        r = turn["response"]

        with st.chat_message("user"):
            st.markdown(f"**{q}**")

        with st.chat_message("assistant"):
            st.markdown(r["direct_answer"])

            # Data Table
            if not r["table_data"].empty:
                st.dataframe(r["table_data"], use_container_width=True, hide_index=True)

            # Metadata Badges
            st.markdown(f"""
            <div style="font-size: 0.75rem; color: #91A0B3; font-family: 'JetBrains Mono'; margin-top: 6px;">
                Provenance: <b>{r['provenance']}</b> · Date: <b>{r['observation_date']}</b> · Latency: <b>{r['latency_ms']}ms</b>
            </div>
            """, unsafe_allow_html=True)

            # Expandable SQL & Safety
            with st.expander("🔍 Inspect Generated SQL Query & Safety Guardrails"):
                st.code(r["sql_used"], language="sql")
                st.caption(f"Assumptions: {r['assumptions']}")
