# ForensiX Agent Server

ForensiX is an AI-powered digital forensics API server that analyzes Call Detail Records (CDR) to detect suspicious patterns. It is powered by Google Gemini and provides a REST API that any project can connect to.

## Features

- **FastAPI Server**: Robust API backend with tool discovery, file management, and agent interaction.
- **AI Agent**: Gemini-powered agent that plans its approach, calls tools, and reports findings.
- **8 Forensic Tools**: Detects high-frequency callers, burner phones, anomalous charges, time distribution anomalies, behavioral clusters, and more.
- **Interactive Visualizations**: Returns Plotly charts as JSON, which can be rendered in any frontend.
- **Streamlit Client**: Included Streamlit UI that acts as a client to the API server.

## Installation

1. Clone the repository
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Set your Google Gemini API key in `.env`:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

## Running the Architecture

You need to run both the API Server and the UI Client.

### 1. Start the API Server
```bash
uvicorn server:app --host 0.0.0.0 --port 8000
```
*API documentation will be available at `http://localhost:8000/docs`*

### 2. Start the Streamlit Client
In a new terminal:
```bash
streamlit run app.py
```

## Integrating with Other Projects

Because ForensiX is an API, you can connect it to Next.js, React, or other Python scripts.

**Example: Running a tool via Python**
```python
import requests

response = requests.post("http://localhost:8000/api/tools/detect_burner_phones/run", json={
    "file": "CDR-Call-Details.csv",
    "args": {"max_account_length": 30}
})
print(response.json())
```
