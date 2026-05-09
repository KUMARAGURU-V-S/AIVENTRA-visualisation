"""
ForensiX CDR Analyzer — Streamlit UI Client
Connects to the ForensiX FastAPI server to perform forensic analysis.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import os
import requests
from dotenv import load_dotenv

load_dotenv()

SERVER_URL = os.getenv("API_SERVER_URL", "http://localhost:8000")

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


def check_server_health():
    try:
        response = requests.get(f"{SERVER_URL}/api/health", timeout=3)
        return response.status_code == 200
    except requests.RequestException:
        return False


def get_available_tools():
    try:
        response = requests.get(f"{SERVER_URL}/api/tools")
        if response.status_code == 200:
            return response.json().get("tools", [])
    except requests.RequestException:
        pass
    return []


def get_uploaded_files():
    try:
        response = requests.get(f"{SERVER_URL}/api/files")
        if response.status_code == 200:
            return response.json().get("files", [])
    except requests.RequestException:
        pass
    return []


def upload_file(file):
    try:
        files = {"file": (file.name, file, "text/csv")}
        response = requests.post(f"{SERVER_URL}/api/files/upload", files=files)
        return response.status_code == 200, response.json()
    except requests.RequestException as e:
        return False, str(e)


def render_header():
    st.markdown("""
    <div class="forensix-header">
        <h1>🔍 ForensiX CDR Analyzer</h1>
        <p>AI-Powered Forensic Phone Call Evidence Analysis • Powered by Gemini Agent</p>
    </div>
    """, unsafe_allow_html=True)


# ─── Main Application ───
def main():
    render_header()
    
    server_online = check_server_health()
    if not server_online:
        st.error(f"⚠️ Cannot connect to ForensiX API Server at {SERVER_URL}. Please ensure the server is running.")
        return

    # ─── Sidebar ───
    with st.sidebar:
        st.markdown("### ⚙️ Server Connection")
        st.success("✅ Connected to API Server")
        
        # We don't ask for API key here anymore, it's on the server side in .env
        
        st.markdown("---")

        # Data source
        st.markdown("### 📂 Evidence Data")
        
        files_data = get_uploaded_files()
        file_names = [f["name"] for f in files_data]
        
        if not file_names:
            st.warning("No files uploaded.")
        
        selected_file = st.selectbox("Select Evidence Dataset", file_names)
        
        uploaded_file = st.file_uploader("Upload New CDR CSV", type="csv")
        if uploaded_file is not None:
            if st.button("Upload to Server"):
                with st.spinner("Uploading..."):
                    success, msg = upload_file(uploaded_file)
                    if success:
                        st.success(f"Uploaded {uploaded_file.name}")
                        st.rerun()
                    else:
                        st.error(f"Upload failed: {msg}")

        st.markdown("---")

        # Tool reference
        st.markdown("### 🧰 Available Tools")
        tools = get_available_tools()
        for info in tools:
            st.markdown(f"""<div class="tool-card">{info['icon']} <strong>{info['name'].replace('_', ' ').title()}</strong><br/><small>{info['description'][:80]}...</small></div>""", unsafe_allow_html=True)

    if not selected_file:
        st.warning("⚠️ No evidence datasets available. Please upload a file.")
        return

    # ─── Tabs ───
    tab1, tab2, tab3 = st.tabs(["📊 Evidence Overview", "🤖 AI Agent Analysis", "🔧 Individual Tools"])

    # ──────────────────────────────
    # TAB 1: Evidence Overview
    # ──────────────────────────────
    with tab1:
        st.markdown("## 📊 Evidence Overview")
        st.markdown(f"**Selected Dataset:** {selected_file}")
        
        selected_file_info = next((f for f in files_data if f["name"] == selected_file), None)
        if selected_file_info:
            cols = st.columns(3)
            cols[0].markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{selected_file_info.get("rows", "N/A")}</div>
                <div class="stat-label">Total Records</div>
            </div>
            """, unsafe_allow_html=True)
            
            size_mb = selected_file_info.get("size_bytes", 0) / (1024 * 1024)
            cols[1].markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{size_mb:.2f} MB</div>
                <div class="stat-label">File Size</div>
            </div>
            """, unsafe_allow_html=True)
            
            cols[2].markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{len(selected_file_info.get("columns", []))}</div>
                <div class="stat-label">Columns</div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("🔎 View Columns"):
                st.write(", ".join(selected_file_info.get("columns", [])))
                
        st.info("💡 Note: In API-First mode, raw data preview and summary charts are generated by running tools instead of direct pandas operations on the client.")

    # ──────────────────────────────
    # TAB 2: AI Agent Analysis
    # ──────────────────────────────
    with tab2:
        st.markdown("## 🤖 AI Forensic Agent")
        st.markdown("The AI agent will plan its analysis approach, call forensic tools via the API, interpret results, and generate a comprehensive report.")

        query = st.text_area(
            "📝 Investigation Query",
            value="Analyze this CDR evidence to identify suspicious phone numbers, detect burner phones, find anomalous behavior patterns, and generate a forensic report with the top suspects and their activities.",
            height=100,
        )

        if st.button("🚀 Launch Forensic Analysis", type="primary", use_container_width=True):
            # Create containers for live updates
            status_container = st.container()
            results_container = st.container()

            with status_container:
                with st.spinner("🔬 ForensiX Agent is analyzing the evidence via API..."):
                    try:
                        response = requests.post(f"{SERVER_URL}/api/chat", json={
                            "query": query,
                            "file": selected_file
                        })
                        
                        if response.status_code == 200:
                            data = response.json()
                            steps = data.get("steps", [])
                            
                            with results_container:
                                for step in steps:
                                    step_type = step.get("type")
                                    content = step.get("content")
                                    chart_json = step.get("chart_json")
                                    
                                    if step_type == "thought":
                                        st.markdown(f'<div class="agent-thought">🧠 <strong>Agent Reasoning</strong><br/>{content}</div>', unsafe_allow_html=True)
                                    elif step_type == "tool_call":
                                        st.markdown(f'<div class="agent-tool-call">⚡ {content}</div>', unsafe_allow_html=True)
                                    elif step_type == "tool_result":
                                        st.markdown(f'<div class="agent-result">✅ {content}</div>', unsafe_allow_html=True)
                                        if chart_json:
                                            # Deserialize Plotly JSON and render
                                            fig = pio.from_json(chart_json)
                                            st.plotly_chart(fig, use_container_width=True)
                                    elif step_type == "error":
                                        st.markdown(f'<div class="agent-error">❌ {content}</div>', unsafe_allow_html=True)
                            
                            st.success(f"✅ Analysis complete! Agent executed {len(steps)} steps.")
                        else:
                            st.error(f"❌ Server Error: {response.text}")
                    except Exception as e:
                        st.error(f"❌ Connection error: {str(e)}")

    # ──────────────────────────────
    # TAB 3: Individual Tools
    # ──────────────────────────────
    with tab3:
        st.markdown("## 🔧 Run Individual Analysis Tools")
        st.markdown("Select and run specific forensic tools independently via the API.")

        if tools:
            tool_name = st.selectbox(
                "Select Tool",
                options=[t["name"] for t in tools],
                format_func=lambda x: next((f"{t['icon']} {t['name'].replace('_', ' ').title()}" for t in tools if t["name"] == x), x)
            )

            # Some tools take args, but for simplicity in the UI we use defaults
            st.info("Running tool with default parameters.")

            if st.button(f"▶️ Run Tool", use_container_width=True):
                with st.spinner(f"Executing on server..."):
                    try:
                        response = requests.post(f"{SERVER_URL}/api/tools/{tool_name}/run", json={
                            "file": selected_file,
                            "args": {}
                        })
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.markdown(f"**Result:** {result['summary']}")
                            
                            if result.get("chart_json"):
                                fig = pio.from_json(result["chart_json"])
                                st.plotly_chart(fig, use_container_width=True)
                            
                            if result.get("data"):
                                with st.expander("📋 View Raw Data"):
                                    st.dataframe(pd.DataFrame(result["data"]), use_container_width=True)
                        else:
                            st.error(f"❌ Error: {response.text}")
                    except Exception as e:
                        st.error(f"❌ Connection error: {str(e)}")


if __name__ == "__main__":
    main()
