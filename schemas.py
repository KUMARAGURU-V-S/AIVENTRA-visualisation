"""
ForensiX CDR Analyzer — Pydantic Schemas
Request/Response models for the FastAPI server.
"""

from pydantic import BaseModel, Field
from typing import Optional, Any


class ChatRequest(BaseModel):
    query: str = Field(..., description="The investigator's analysis query")
    file: str = Field(default="CDR-Call-Details.csv", description="Evidence file to analyze")


class AgentStep(BaseModel):
    type: str = Field(..., description="Step type: thought, tool_call, tool_result, error")
    content: str = Field(..., description="Step content or summary")
    tool: Optional[str] = Field(None, description="Tool name if applicable")
    args: Optional[dict] = Field(None, description="Tool arguments if applicable")
    icon: Optional[str] = Field(None, description="Display icon")
    chart_json: Optional[str] = Field(None, description="Plotly chart as JSON string")


class ChatResponse(BaseModel):
    success: bool
    steps: list[AgentStep]
    total_steps: int


class ToolInfo(BaseModel):
    name: str
    description: str
    icon: str


class ToolListResponse(BaseModel):
    tools: list[ToolInfo]
    count: int


class ToolRunRequest(BaseModel):
    file: str = Field(default="CDR-Call-Details.csv", description="Evidence file to analyze")
    args: Optional[dict] = Field(default_factory=dict, description="Tool arguments")


class ToolRunResponse(BaseModel):
    success: bool
    tool: str
    summary: str
    data: Any = None
    chart_json: Optional[str] = None


class FileInfo(BaseModel):
    name: str
    size_bytes: int
    rows: Optional[int] = None
    columns: Optional[list[str]] = None


class FileListResponse(BaseModel):
    files: list[FileInfo]
    count: int


class HealthResponse(BaseModel):
    status: str
    version: str
    tools_available: int
    files_loaded: int
