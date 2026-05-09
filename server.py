"""
ForensiX CDR Analyzer — FastAPI Server
Exposes the forensic analysis tools and AI agent via REST API.
"""

import os
import tempfile
import pandas as pd
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from schemas import (
    ChatRequest, ChatResponse, ToolListResponse, ToolInfo,
    ToolRunRequest, ToolRunResponse, FileListResponse, FileInfo, HealthResponse
)
from tools import TOOL_REGISTRY
from agent import run_agent

load_dotenv()

app = FastAPI(
    title="ForensiX Agent Server",
    description="AI-powered forensic phone call evidence analysis API",
    version="1.0.0"
)

# Enable CORS for frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for uploaded data (for simplicity in this architecture)
# In production, this would be a database + cloud storage
DATA_STORE = {}

# Load default data if available
DEFAULT_CSV = "CDR-Call-Details.csv"
if os.path.exists(DEFAULT_CSV):
    try:
        DATA_STORE[DEFAULT_CSV] = pd.read_csv(DEFAULT_CSV)
        print(f"Loaded default dataset: {DEFAULT_CSV}")
    except Exception as e:
        print(f"Error loading default dataset: {e}")


def get_dataframe(filename: str) -> pd.DataFrame:
    """Retrieve dataframe from store or raise 404."""
    if filename not in DATA_STORE:
        raise HTTPException(status_code=404, detail=f"File '{filename}' not found.")
    return DATA_STORE[filename]


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Server health check."""
    return HealthResponse(
        status="online",
        version="1.0.0",
        tools_available=len(TOOL_REGISTRY),
        files_loaded=len(DATA_STORE)
    )


@app.get("/api/tools", response_model=ToolListResponse)
async def list_tools():
    """List all available forensic analysis tools."""
    tools_list = [
        ToolInfo(name=name, description=info["description"], icon=info["icon"])
        for name, info in TOOL_REGISTRY.items()
    ]
    return ToolListResponse(tools=tools_list, count=len(tools_list))


@app.get("/api/files", response_model=FileListResponse)
async def list_files():
    """List all uploaded evidence files."""
    files = []
    for name, df in DATA_STORE.items():
        files.append(FileInfo(
            name=name,
            size_bytes=df.memory_usage(deep=True).sum(),
            rows=len(df),
            columns=df.columns.tolist()
        ))
    return FileListResponse(files=files, count=len(files))


@app.post("/api/files/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a new CDR CSV file."""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")
    
    try:
        # Read the file into memory
        df = pd.read_csv(file.file)
        DATA_STORE[file.filename] = df
        return {"message": f"Successfully uploaded {file.filename}", "rows": len(df)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading CSV: {str(e)}")


@app.delete("/api/files/{filename}")
async def delete_file(filename: str):
    """Delete an evidence file."""
    if filename in DATA_STORE:
        if filename == DEFAULT_CSV:
            raise HTTPException(status_code=400, detail="Cannot delete default dataset.")
        del DATA_STORE[filename]
        return {"message": f"Deleted {filename}"}
    raise HTTPException(status_code=404, detail="File not found")


@app.post("/api/tools/{tool_name}/run", response_model=ToolRunResponse)
async def run_tool(tool_name: str, request: ToolRunRequest):
    """Run a specific forensic tool on a dataset."""
    if tool_name not in TOOL_REGISTRY:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found.")
    
    df = get_dataframe(request.file)
    tool_info = TOOL_REGISTRY[tool_name]
    
    try:
        # Pass serialize=True to get JSON instead of Figure objects
        result = tool_info["fn"](df, **request.args, serialize=True)
        return ToolRunResponse(
            success=True,
            tool=tool_name,
            summary=result.get("summary", ""),
            data=result.get("data"),
            chart_json=result.get("chart")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tool execution failed: {str(e)}")


@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """Run the AI agent analysis on a dataset."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured on server.")
    
    df = get_dataframe(request.file)
    
    try:
        # run_agent now returns a list of step dictionaries that match the AgentStep schema
        steps = run_agent(api_key, df, request.query)
        return ChatResponse(
            success=True,
            steps=steps,
            total_steps=len(steps)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
