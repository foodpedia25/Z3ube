"""
Pydantic models for API requests and responses
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


# Chat Models
class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    conversation_id: Optional[str] = None
    depth: str = Field("quick", description="Reasoning depth: quick, normal, or deep")
    model: str = Field("auto", description="AI Model to use: auto, openai, anthropic, gemini, llama, deepseek")
    image: Optional[str] = Field(None, description="Base64 encoded image (JPEG/PNG)")


class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    thinking_steps: Optional[List[Dict[str, Any]]] = None


# Think/Reasoning Models
class ThinkRequest(BaseModel):
    query: str = Field(..., description="Problem to reason about")
    depth: str = Field("normal", description="Reasoning depth: quick, normal, or deep")


class ThinkResponse(BaseModel):
    query: str
    steps: List[Dict[str, Any]]
    conclusion: str
    confidence: float
    execution_time: float


# Research Models
class ResearchRequest(BaseModel):
    topic: str = Field(..., description="Research topic")
    depth: str = Field("normal", description="Research depth")
    max_sources: int = Field(5, description="Maximum sources to use")


class ResearchResponse(BaseModel):
    topic: str
    summary: str
    key_findings: List[str]
    sources: List[Dict[str, Any]]
    confidence: float
    research_time: float


# Code Generation Models
class CodeRequest(BaseModel):
    description: str = Field(..., description="What the code should do")
    language: str = Field("python", description="Programming language")
    include_tests: bool = Field(True, description="Include tests")
    optimize: bool = Field(False, description="Optimize the code")


class CodeResponse(BaseModel):
    language: str
    code: str
    tests: Optional[str]
    explanation: str
    dependencies: List[str]
    quality_score: float


# Analysis Models
class AnalyzeRequest(BaseModel):
    problem: str = Field(..., description="Problem to analyze")
    context: Optional[Dict[str, Any]] = None


class AnalyzeResponse(BaseModel):
    problem: str
    analysis: str
    solutions: List[Dict[str, Any]]
    recommendation: str


# Health Models
class HealthResponse(BaseModel):
    status: str
    metrics: Dict[str, Any]
    circuit_breakers: Dict[str, str]
    recent_errors: List[Dict[str, Any]]
