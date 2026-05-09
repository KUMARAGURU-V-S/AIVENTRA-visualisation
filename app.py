"""
ForensiX CDR Analyzer — Main Streamlit Application
AI-powered forensic analysis of phone Call Detail Records.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import time
from dotenv import load_dotenv
from tools import TOOL_REGISTRY
from agent import run_agent

load_dotenv()

# ─── Page Config ───
st.set_page_config(
    page_title="ForensiX CDR Analyzer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@300;400;600;700&display=swap');

    /* Global dark theme */
    .stApp {
        background: linear-gradient(135deg, #0a0a0f 0%, #0d1117 50%, #0a0a0f 100%);
        color: #e0e0e0;
    }

    /* Header styling */
    .forensix-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        border: 1px solid rgba(220, 20, 60, 0.3);
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 0 40px rgba(220, 20, 60, 0.1);
    }
    .forensix-header h1 {
        font-family: 'JetBrains Mono', monospace;
        font-size: 2.5rem;
        background: linear-gradient(135deg, #dc143c, #ff6b35, #ffd700);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .forensix-header p {
        color: #8892b0;
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
    }

    /* Agent step cards */
    .agent-thought {
        background: rgba(26, 26, 46, 0.8);
        border-left: 4px solid #4a90d9;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin: 0.8rem 0;
        font-family: 'Inter', sans-serif;
        color: #c8d6e5;
        line-height: 1.6;
    }
    .agent-tool-call {
        background: rgba(15, 52, 96, 0.5);
        border-left: 4px solid #ffd700;
        border-radius: 8px;
        padding: 0.8rem 1.2rem;
        margin: 0.5rem 0;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
        color: #ffd700;
    }
    .agent-result {
        background: rgba(20, 60, 20, 0.4);
        border-left: 4px solid #00d97e;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin: 0.5rem 0;
        font-family: 'Inter', sans-serif;
        color: #a3d9a5;
    }
    .agent-error {
        background: rgba(60, 20, 20, 0.4);
        border-left: 4px solid #dc143c;
        border-radius: 8px;
        padding: 0.8rem 1.2rem;
        margin: 0.5rem 0;
        color: #ff6b6b;
    }

    /* Stat cards */
    .stat-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 1px solid rgba(74, 144, 217, 0.2);
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .stat-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(74, 144, 217, 0.15);
    }
    .stat-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.8rem;
        font-weight: 700;
        color: #ffd700;
    }
    .stat-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        color: #8892b0;
        margin-top: 0.3rem;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1117 0%, #1a1a2e 100%);
        border-right: 1px solid rgba(220, 20, 60, 0.2);
    }

    /* Tool cards */
    .tool-card {
        background: rgba(26, 26, 46, 0.6);
        border: 1px solid rgba(255, 215, 0, 0.15);
        border-radius: 10px;
        padding: 0.8rem 1rem;
        margin: 0.4rem 0;
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        color: #c8d6e5;
    }

    /* Hide default streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data(file_path=None, uploaded_file=None):
    """Load CDR data from file path or uploaded file."""
    if uploaded_file is not None:
        return pd.read_csv(uploaded_file)
    elif file_path and os.path.exists(file_path):
        return pd.read_csv(file_path)
    return None


def render_header():
    st.markdown("""
    <div class="forensix-header">
        <h1>🔍 ForensiX CDR Analyzer</h1>
        <p>AI-Powered Forensic Phone Call Evidence Analysis • Powered by Gemini Agent</p>
    </div>
    """, unsafe_allow_html=True)


def render_stats(df):
    """Render dataset overview statistics."""
    cols = st.columns(5)
    stats = [
        (f"{len(df):,}", "Total Records"),
        (f"{df['Phone Number'].nunique():,}", "Unique Numbers"),
        (f"{(df['Churn'].astype(str).str.upper() == 'TRUE').sum():,}", "Flagged (Churn)"),
        (f"{df['Account Length'].median():.0f}d", "Median Account Age"),
        (f"{(df['Day Calls'] + df['Eve Calls'] + df['Night Calls'] + df['Intl Calls']).mean():.0f}", "Avg Total Calls"),
    ]
    for col, (value, label) in zip(cols, stats):
        col.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{value}</div>
            <div class="stat-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)


def render_overview_charts(df):
    """Render quick overview charts of the dataset."""
    col1, col2 = st.columns(2)

    with col1:
        df_temp = df.copy()
        df_temp["Total_Calls"] = df_temp["Day Calls"] + df_temp["Eve Calls"] + df_temp["Night Calls"] + df_temp["Intl Calls"]
        fig = px.histogram(
            df_temp, x="Total_Calls", nbins=60,
            color_discrete_sequence=["#4a90d9"],
            title="📞 Total Call Volume Distribution",
        )
        fig.update_layout(template="plotly_dark", paper_bgcolor="#0a0a0f", plot_bgcolor="#0a0a0f", height=350)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        call_data = pd.DataFrame({
            "Period": ["Day", "Evening", "Night", "International"],
            "Avg Calls": [df["Day Calls"].mean(), df["Eve Calls"].mean(), df["Night Calls"].mean(), df["Intl Calls"].mean()],
        })
        fig = px.bar(
            call_data, x="Period", y="Avg Calls",
            color="Period", color_discrete_map={"Day": "#ffd700", "Evening": "#ff6b35", "Night": "#dc143c", "International": "#4a90d9"},
            title="⏰ Average Calls by Time Period",
        )
        fig.update_layout(template="plotly_dark", paper_bgcolor="#0a0a0f", plot_bgcolor="#0a0a0f", height=350, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)


def run_individual_tool(tool_name, df):
    """Run a single tool and display results."""
    tool_info = TOOL_REGISTRY[tool_name]
    result = tool_info["fn"](df)
    st.markdown(f"**{tool_info['icon']} Result:** {result['summary']}")
    if result.get("chart"):
        st.plotly_chart(result["chart"], use_container_width=True)
    if result.get("data") and isinstance(result["data"], list):
        with st.expander("📋 View Raw Data"):
            st.dataframe(pd.DataFrame(result["data"]), use_container_width=True)


# ─── Main Application ───
def main():
    render_header()

    # ─── Sidebar ───
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")

        # API Key
        api_key = st.text_input(
            "🔑 Gemini API Key",
            value=os.getenv("GEMINI_API_KEY", ""),
            type="password",
            help="Get your free API key at aistudio.google.com",
        )

        st.markdown("---")

        # Data source
        st.markdown("### 📂 Evidence Data")
        data_source = st.radio("Source", ["Default CDR File", "Upload CSV"], label_visibility="collapsed")

        uploaded_file = None
        if data_source == "Upload CSV":
            uploaded_file = st.file_uploader("Upload CDR CSV", type="csv")

        st.markdown("---")

        # Tool reference
        st.markdown("### 🧰 Available Tools")
        for name, info in TOOL_REGISTRY.items():
            st.markdown(f"""<div class="tool-card">{info['icon']} <strong>{name.replace('_', ' ').title()}</strong><br/><small>{info['description'][:80]}...</small></div>""", unsafe_allow_html=True)

    # ─── Load Data ───
    default_path = os.path.join(os.path.dirname(__file__), "CDR-Call-Details.csv")
    df = load_data(file_path=default_path, uploaded_file=uploaded_file)

    if df is None:
        st.warning("⚠️ No CDR data loaded. Please upload a CSV file or ensure CDR-Call-Details.csv is in the project directory.")
        return

    # ─── Tabs ───
    tab1, tab2, tab3 = st.tabs(["📊 Evidence Overview", "🤖 AI Agent Analysis", "🔧 Individual Tools"])

    # ──────────────────────────────
    # TAB 1: Evidence Overview
    # ──────────────────────────────
    with tab1:
        st.markdown("## 📊 Evidence Overview")
        render_stats(df)
        st.markdown("<br>", unsafe_allow_html=True)
        render_overview_charts(df)

        with st.expander("🔎 Preview Raw Evidence Data"):
            st.dataframe(df.head(100), use_container_width=True)

    # ──────────────────────────────
    # TAB 2: AI Agent Analysis
    # ──────────────────────────────
    with tab2:
        st.markdown("## 🤖 AI Forensic Agent")
        st.markdown("The AI agent will plan its analysis approach, call forensic tools, interpret results, and generate a comprehensive report.")

        query = st.text_area(
            "📝 Investigation Query",
            value="Analyze this CDR evidence to identify suspicious phone numbers, detect burner phones, find anomalous behavior patterns, and generate a forensic report with the top suspects and their activities.",
            height=100,
        )

        if st.button("🚀 Launch Forensic Analysis", type="primary", use_container_width=True):
            if not api_key or api_key == "your_gemini_api_key_here":
                st.error("❌ Please enter a valid Gemini API key in the sidebar.")
                return

            # Create containers for live updates
            status_container = st.container()
            results_container = st.container()

            charts_collected = []
            step_counter = {"val": 0}

            def on_step(step_type, content, chart=None):
                step_counter["val"] += 1
                with results_container:
                    if step_type == "thought":
                        st.markdown(f'<div class="agent-thought">🧠 <strong>Agent Reasoning (Step {step_counter["val"]})</strong><br/>{content}</div>', unsafe_allow_html=True)
                    elif step_type == "tool_call":
                        st.markdown(f'<div class="agent-tool-call">⚡ {content}</div>', unsafe_allow_html=True)
                    elif step_type == "tool_result":
                        st.markdown(f'<div class="agent-result">✅ {content}</div>', unsafe_allow_html=True)
                        if chart:
                            st.plotly_chart(chart, use_container_width=True)
                            charts_collected.append(chart)
                    elif step_type == "error":
                        st.markdown(f'<div class="agent-error">❌ {content}</div>', unsafe_allow_html=True)

            with status_container:
                with st.spinner("🔬 ForensiX Agent is analyzing the evidence..."):
                    try:
                        steps = run_agent(api_key, df, query, on_step=on_step)
                        st.success(f"✅ Analysis complete! Agent executed {step_counter['val']} steps.")
                    except Exception as e:
                        st.error(f"❌ Agent error: {str(e)}")

    # ──────────────────────────────
    # TAB 3: Individual Tools
    # ──────────────────────────────
    with tab3:
        st.markdown("## 🔧 Run Individual Analysis Tools")
        st.markdown("Select and run specific forensic tools independently.")

        tool_name = st.selectbox(
            "Select Tool",
            options=list(TOOL_REGISTRY.keys()),
            format_func=lambda x: f"{TOOL_REGISTRY[x]['icon']} {x.replace('_', ' ').title()}",
        )

        if st.button(f"▶️ Run {tool_name.replace('_', ' ').title()}", use_container_width=True):
            with st.spinner(f"Running {tool_name}..."):
                run_individual_tool(tool_name, df)


if __name__ == "__main__":
    main()
