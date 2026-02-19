"""
Z3ube FastAPI Server - Main API Gateway

Endpoints:
- POST /chat - Conversational interface
- POST /think - Deep reasoning
- POST /research - Research tasks
- POST /code - Code generation
- POST /analyze - Problem analysis
- GET /health - System health
- GET /knowledge/graph - Knowledge graph data
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import asyncio
from typing import AsyncGenerator
import json

from api.models import (
    ChatRequest, ChatResponse,
    ThinkRequest, ThinkResponse,
    ResearchRequest, ResearchResponse,
    CodeRequest, CodeResponse,
    AnalyzeRequest, AnalyzeResponse,
    HealthResponse
)

from core.reasoning_engine import reasoning_engine
from core.self_learning import learning_system
from core.auto_healer import auto_healer
from core.research_engine import research_engine
from core.code_generator import code_generator
from core.knowledge_graph import knowledge_graph

# Initialize FastAPI app
app = FastAPI(
    title="Z3ube API",
    description="Next-Generation AI Agent Platform API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Z3ube API",
        "version": "1.0.0",
        "status": "operational",
        "capabilities": [
            "reasoning",
            "research",
            "code_generation",
            "self_learning",
            "auto_healing"
        ]
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Conversational interface with Z3ube
    """
    try:
        # Use reasoning engine for response with auto-healing
        async def generate_response():
            result = await reasoning_engine.reason(request.message, depth=request.depth, model=request.model)
            return result
        
        result = await auto_healer.detect_and_heal(
            generate_response,
            "chat_response",
            {"message": request.message}
        )
        
        # Record interaction for learning
        learning_system.record_interaction(
            query=request.message,
            response=result.conclusion,
            success=True,
            tags=["chat"]
        )
        
        return ChatResponse(
            response=result.conclusion,
            conversation_id=request.conversation_id or "default",
            thinking_steps=[s.to_dict() for s in result.steps]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Stream conversational response with thinking steps
    """
    async def event_generator():
        try:
            async for chunk in reasoning_engine.reason_stream(request.message, depth=request.depth, model=request.model):
                yield chunk
        except Exception as e:
            yield json.dumps({"type": "error", "data": str(e)}) + "\n"

    return StreamingResponse(event_generator(), media_type="application/x-ndjson")


@app.post("/think", response_model=ThinkResponse)
async def think(request: ThinkRequest):
    """
    Deep reasoning and planning
    """
    try:
        async def perform_reasoning():
            return await reasoning_engine.reason(request.query, depth=request.depth)
        
        result = await auto_healer.detect_and_heal(
            perform_reasoning,
            "reasoning",
            {"query": request.query}
        )
        
        # Record for learning
        learning_system.record_interaction(
            query=request.query,
            response=result.conclusion,
            success=True,
            tags=["reasoning", request.depth]
        )
        
        return ThinkResponse(**result.to_dict())
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/research", response_model=ResearchResponse)
async def research(request: ResearchRequest):
    """
    Conduct deep research on a topic
    """
    try:
        async def perform_research():
            return await research_engine.conduct_research(
                topic=request.topic,
                depth=request.depth,
                max_sources=request.max_sources
            )
        
        result = await auto_healer.detect_and_heal(
            perform_research,
            "research",
            {"topic": request.topic}
        )
        
        # Record for learning
        learning_system.record_interaction(
            query=f"Research: {request.topic}",
            response=result.summary,
            success=True,
            tags=["research"]
        )
        
        return ResearchResponse(**result.to_dict())
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/code", response_model=CodeResponse)
async def generate_code(request: CodeRequest):
    """
    Generate code from description
    """
    try:
        async def perform_code_generation():
            return await code_generator.generate_code(
                description=request.description,
                language=request.language,
                include_tests=request.include_tests,
                optimize=request.optimize
            )
        
        result = await auto_healer.detect_and_heal(
            perform_code_generation,
            "code_generation",
            {"description": request.description, "language": request.language}
        )
        
        # Record for learning
        learning_system.record_interaction(
            query=f"Generate {request.language} code: {request.description}",
            response=result.code[:100],
            success=True,
            tags=["code_generation", request.language]
        )
        
        return CodeResponse(**result.to_dict())
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_problem(request: AnalyzeRequest):
    """
    Analyze problem and propose solutions
    """
    try:
        # Use reasoning engine for analysis
        result = await reasoning_engine.reason(
            f"Analyze this problem and propose solutions: {request.problem}",
            depth="deep"
        )
        
        return AnalyzeResponse(
            problem=request.problem,
            analysis=result.conclusion,
            solutions=[{
                "description": "Multi-step solution based on reasoning",
                "confidence": result.confidence
            }],
            recommendation=result.conclusion
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Get system health status
    """
    health_data = auto_healer.get_health_status()
    return HealthResponse(**health_data)


@app.get("/knowledge/graph")
async def get_knowledge_graph():
    """
    Get knowledge graph data for visualization
    """
    try:
        graph_data = knowledge_graph.get_graph_data()
        return graph_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """
    Get learning and performance statistics
    """
    return {
        "learning": learning_system.get_learning_stats(),
        "reasoning_context": reasoning_engine.get_context(),
        "health": auto_healer.get_health_status()
    }


@app.get("/patterns")
async def get_patterns():
    """
    Get learned patterns
    """
    return {
        "patterns": learning_system.get_all_patterns()
    }


@app.post("/code/project")
async def generate_project(request: CodeRequest):
    """
    Generate a full project structure
    """
    try:
        files = await code_generator.generate_project_structure(
            description=request.description,
            project_type=request.language # reusing language field for project type
        )
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/system/status")
async def system_status():
    """
    Get real-time system status for Neural Dashboard
    """
    try:
        current_health = auto_healer.get_health_status()
        learning_stats = learning_system.get_learning_stats()
        reasoning_ctx = reasoning_engine.get_context()
        
        return {
            "health": current_health,
            "learning": learning_stats,
            "reasoning": reasoning_ctx,
            "system": {
                "uptime": "99.9%", # Mock for now
                "latency": "45ms",
                "active_connections": 12
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/knowledge/graph")
async def get_knowledge_graph():
    """
    Get knowledge graph data
    """
    return knowledge_graph.get_graph_data()


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    print("🚀 Z3ube API Server starting...")
    print("📡 Core systems initialized")
    print("🧠 Reasoning engine ready")
    print("📚 Research engine ready")
    print("💻 Code generator ready")
    print("🔧 Auto-healer active")
    print("📈 Self-learning enabled")
    
    # improved seed data for knowledge graph
    concepts = [
        ("Z3ube", {"type": "system", "importance": 1.0}),
        ("AI", {"type": "concept", "importance": 0.9}),
        ("Reasoning", {"type": "module", "importance": 0.8}),
        ("Learning", {"type": "module", "importance": 0.8}),
        ("Robotics", {"type": "domain", "importance": 0.7}),
        ("Code", {"type": "skill", "importance": 0.7}),
        ("Python", {"type": "language", "importance": 0.6}),
        ("ROS2", {"type": "framework", "importance": 0.6}),
        ("Gemini", {"type": "model", "importance": 0.8}),
        ("Auto-Healing", {"type": "module", "importance": 0.7})
    ]
    
    for concept, attrs in concepts:
        knowledge_graph.add_concept(concept, attrs)
        
    relationships = [
        ("Z3ube", "AI", "is_a"),
        ("Z3ube", "Reasoning", "has_module"),
        ("Z3ube", "Learning", "has_module"),
        ("Z3ube", "Robotics", "supports"),
        ("Z3ube", "Code", "generates"),
        ("Code", "Python", "supports"),
        ("Robotics", "ROS2", "uses"),
        ("Reasoning", "Gemini", "uses"),
        ("Z3ube", "Auto-Healing", "has_module"),
        ("AI", "Python", "implemented_in")
    ]
    
    for source, target, rel in relationships:
        knowledge_graph.add_relationship(source, target, rel)
        
    print(f"✅ Knowledge Graph initialized with {len(concepts)} nodes")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("👋 Z3ube API Server shutting down...")
    await research_engine.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
